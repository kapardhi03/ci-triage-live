"""The integration contract: the record every observer writes, and the rules for combining.

Two facts measured in this repository are encoded here rather than assumed.

1. Observers 1 and 3 have zero shared columns and a shared cause. ExecutionTime predicts
   whether observer 3 sees the SSL NoSuchMethodError at AUC 0.6987 (p=1.06e-06) -- better
   than observer 1 predicts the label it exists to predict (0.6765). Their agreement is
   substantially one observation, so evidence is collapsed by cause_group before anything
   is aggregated.

2. The phase 01 table prices a shipped defect at ~40h against ~3h for a needless hold, at a
   3.19% base rate. One real failure among 196 flaky ones must still hold the release, so
   the case-level rule is hold-if-any-credibly-real, never a mean or a vote.

See docs/architecture.md and decisions/10-independence.md.
"""

from dataclasses import dataclass, field
from enum import Enum


class State(str, Enum):
    """NO_EVIDENCE and INDETERMINATE are different findings and must not be merged.

    A uniform probability encodes both identically, which erases the distinction exactly
    when it matters: one is a gap in coverage, the other is ambiguity in the world.
    """
    OBSERVED = "OBSERVED"            # the observer looked and has a probability
    INDETERMINATE = "INDETERMINATE"  # it looked; the evidence points equally
    NO_EVIDENCE = "NO_EVIDENCE"      # it could not look at all


class Verdict(str, Enum):
    REAL_DEFECT = "REAL_DEFECT"
    FLAKY = "FLAKY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    ABSTAIN = "ABSTAIN"


class Decision(str, Enum):
    SHIP = "SHIP"
    HOLD = "HOLD"
    ESCALATE = "ESCALATE"


class UncalibratedProbabilityError(ValueError):
    """A probability was emitted without declaring whether it is calibrated."""


@dataclass(frozen=True)
class Evidence:
    """What one observer saw about one test. The single structure every observer writes."""
    observer: str
    test: str
    state: State
    verdict: Verdict
    reads: frozenset               # what it read -- lets the overlap be computed, not hoped
    cause_group: str               # records sharing this are one observation, not several
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    probability: float = None
    calibrated: bool = None        # required whenever probability is not None
    note: str = ""

    def __post_init__(self):
        if self.state is State.OBSERVED and self.probability is None:
            raise ValueError("OBSERVED evidence must carry a probability")
        if self.state is State.NO_EVIDENCE and self.probability is not None:
            raise ValueError("NO_EVIDENCE must not carry a probability -- use INDETERMINATE")
        if self.probability is not None and self.calibrated is None:
            raise UncalibratedProbabilityError(
                f"{self.observer} emitted probability={self.probability} without declaring "
                f"whether it is calibrated; downstream arithmetic depends on that flag")


def input_overlap(*designs):
    """Intersect observers' `reads` sets. Overlap is a fact to check, not a hope."""
    sets = [frozenset(d) for d in designs]
    pairwise = {}
    for i, a in enumerate(sets):
        for j, b in enumerate(sets):
            if i < j:
                pairwise[(i, j)] = a & b
    return {"all": frozenset.intersection(*sets) if sets else frozenset(),
            "pairwise": pairwise}


def collapse_correlated(records):
    """Records sharing a cause_group contribute ONE voice, not several.

    This is the de-duplication. Averaging within a group -- or simply keeping all of them --
    lets a single physical event vote twice, which is precisely what the AUC 0.6987 coupling
    between observers 1 and 3 would otherwise do.
    """
    usable = [r for r in records if r.state is not State.NO_EVIDENCE]
    by_group = {}
    for r in usable:
        cur = by_group.get(r.cause_group)
        # keep the most informative record in the group: OBSERVED beats INDETERMINATE,
        # then the one furthest from 0.5. Never sum, never average across the group.
        if cur is None or _informativeness(r) > _informativeness(cur):
            by_group[r.cause_group] = r
    return list(by_group.values())


def _informativeness(r):
    if r.state is State.OBSERVED and r.probability is not None:
        return 1.0 + abs(r.probability - 0.5)
    return 0.0


def run_level(records, real_threshold=0.5):
    """Per test: collapse correlated evidence, then decide what this test's failure is."""
    collapsed = collapse_correlated(records)
    n_dropped = len([r for r in records if r.state is not State.NO_EVIDENCE]) - len(collapsed)
    no_ev = [r for r in records if r.state is State.NO_EVIDENCE]

    if not collapsed:
        return {"test": records[0].test if records else None, "verdict": Verdict.ABSTAIN,
                "state": State.NO_EVIDENCE, "p_real": None, "voices": 0,
                "deduplicated": n_dropped, "no_evidence": len(no_ev),
                "cause_groups": []}

    # P(real defect) = 1 - P(flaky), taken as the strongest surviving voice, not a mean.
    p_real = max((1.0 - r.probability) for r in collapsed
                 if r.state is State.OBSERVED and r.probability is not None) \
        if any(r.state is State.OBSERVED for r in collapsed) else None

    verdict = Verdict.ABSTAIN if p_real is None else (
        Verdict.REAL_DEFECT if p_real >= real_threshold else Verdict.FLAKY)
    return {"test": collapsed[0].test, "verdict": verdict,
            "state": State.OBSERVED if p_real is not None else State.INDETERMINATE,
            "p_real": p_real, "voices": len(collapsed), "deduplicated": n_dropped,
            "no_evidence": len(no_ev),
            "cause_groups": sorted({r.cause_group for r in collapsed})}


def case_level(run_results, credible=0.5, min_coverage=0.5):
    """One build -> one decision. Hold if ANY test is credibly a real defect.

    Never a mean and never a vote: 196 flaky tests do not cancel one real defect. Under the
    phase 01 table a mean would ship a ~40h bug to avoid a ~3h hold, and would do it
    confidently, because the mean is dominated by the cheap cases while the decision is
    dominated by the expensive one.
    """
    if not run_results:
        return {"decision": Decision.ESCALATE, "driver": None,
                "rule": "no run-level results", "coverage": 0.0}

    scored = [r for r in run_results if r["p_real"] is not None]
    coverage = len(scored) / len(run_results)

    real = [r for r in scored if r["p_real"] >= credible]
    if real:
        driver = max(real, key=lambda r: r["p_real"])
        return {"decision": Decision.HOLD, "driver": driver["test"],
                "rule": f"hold-if-any-credibly-real: {len(real)} of {len(run_results)} "
                        f"test(s) at or above {credible}",
                "coverage": coverage, "p_real": driver["p_real"]}

    if coverage < min_coverage:
        return {"decision": Decision.ESCALATE, "driver": None,
                "rule": f"coverage {coverage:.0%} below {min_coverage:.0%}; too little "
                        f"evidence to ship on",
                "coverage": coverage}

    return {"decision": Decision.SHIP, "driver": None,
            "rule": "no test is credibly a real defect and coverage is adequate",
            "coverage": coverage}


# --- slice 12: the explanation layer -----------------------------------------------------

def explain(records, verdict, probability=None):
    """Template-bound account of the BASIS for a verdict. It never asserts the verdict.

    Every field is filled from the Evidence records; nothing is composed. See
    design/12-slm-and-the-ledger.md -- the explainer states the basis, never the belief, so
    the account stays true even when the verdict is wrong.
    """
    usable = [r for r in records if r.state is State.OBSERVED and r.probability is not None]
    collapsed = collapse_correlated(records)
    survivors = {r.observer for r in collapsed}
    no_ev = [r for r in records if r.state is State.NO_EVIDENCE]

    basis = max(collapsed, key=_informativeness) if collapsed else None
    inert = [r.observer for r in usable if abs(r.probability - 0.5) < 0.01]
    suppressed = [{"observer": r.observer, "cause_group": r.cause_group}
                  for r in usable if r.observer not in survivors]

    spread = (max(r.probability for r in collapsed) - min(r.probability for r in collapsed)
              if len(collapsed) > 1 else 0.0)
    if not collapsed or no_ev and not usable:
        level = "THIN"
    elif spread > 0.4:
        level = "SPLIT"
    elif len(collapsed) < 2:
        level = "THIN"
    else:
        level = "CONFIDENT"

    out = {
        "basis": basis.observer if basis else None,
        "basis_probability": basis.probability if basis else None,
        "calibrated": basis.calibrated if basis else None,
        "corroborated_by": sorted(r.observer for r in collapsed
                                  if basis and r.observer != basis.observer
                                  and abs(r.probability - basis.probability) <= 0.1),
        "contradicted_by": sorted(r.observer for r in collapsed
                                  if basis and r.observer != basis.observer
                                  and abs(r.probability - basis.probability) > 0.1),
        "voices": len(collapsed),
        "suppressed": suppressed,
        "inert": sorted(inert),
        "no_evidence": sorted(r.observer for r in no_ev),
        "evidence_level": level,
    }
    # trace: every emitted field -> the record field it came from
    out["trace"] = {k: "Evidence." + v for k, v in {
        "basis": "observer", "basis_probability": "probability", "calibrated": "calibrated",
        "corroborated_by": "observer", "contradicted_by": "observer",
        "voices": "cause_group", "suppressed": "cause_group", "inert": "probability",
        "no_evidence": "state", "evidence_level": "state+probability",
    }.items()}
    return out
