"""Slice 11: the decision layer. Five strategies, and the rules for comparing them.

Reads Evidence AFTER slice 10 has collapsed it by cause_group. Un-collapsed records let one
physical cause vote twice -- the coupling measured at AUC 0.6987 between observers 1 and 3.

A strategy that cannot run on every frozen case is `incomplete`: unranked, not a loss.
See experiments/11-fusion-comparison.md and decisions/11-arbiter-rules.md.
"""

import hashlib
import json

import numpy as np

from ci_triage.contracts import Evidence, State, Verdict, collapse_correlated

INCOMPLETE = "incomplete"


def js_divergence(p, q, eps=1e-12):
    """Jensen-Shannon divergence between two Bernoulli beliefs, in bits. Range [0, 1].

    Chosen over KL because observers have no privileged order (JS is symmetric; KL is not)
    and because KL is unbounded -- one observer at 0.0 against another at 1.0 gives infinity,
    which no ranking can use. JS is bounded, so divergences are comparable across pairs and
    a threshold on it means the same thing everywhere.

    Total variation was the other candidate; it is also symmetric and bounded but is linear
    in the gap, so it cannot distinguish disagreement near the extremes (0.05 vs 0.15) from
    disagreement in the middle (0.45 vs 0.55). Those are very different disagreements.
    """
    p, q = float(np.clip(p, eps, 1 - eps)), float(np.clip(q, eps, 1 - eps))
    m = 0.5 * (p + q)

    def kl(a, b):
        return a * np.log2(a / b) + (1 - a) * np.log2((1 - a) / (1 - b))

    return float(0.5 * kl(p, m) + 0.5 * kl(q, m))


def max_divergence(probs):
    """Largest pairwise JS divergence among the surviving observers."""
    vals = [p for p in probs if p is not None]
    if len(vals) < 2:
        return 0.0
    return max(js_divergence(a, b)
               for i, a in enumerate(vals) for b in vals[i + 1:])


def distinct_voices(records):
    """How many genuinely distinct opinions -- cause_groups, not records.

    Three records from one cause_group are one opinion. Reporting them as consensus is the
    false-consensus failure.
    """
    return len({r.cause_group for r in records if r.state is not State.NO_EVIDENCE})


def is_false_consensus(records):
    """True when records agree but are not distinct. Unanimity from one voice is not consensus."""
    usable = [r for r in records if r.state is State.OBSERVED and r.probability is not None]
    if len(usable) < 2:
        return False
    agree = max(r.probability for r in usable) - min(r.probability for r in usable) < 0.1
    return agree and distinct_voices(usable) < 2


# --- the strategies ----------------------------------------------------------------------

def _probs(records):
    c = collapse_correlated(records)
    return [r.probability for r in c
            if r.state is State.OBSERVED and r.probability is not None], c


def strategy_most_confident(records, **_):
    """A: the observer furthest from 0.5 wins."""
    p, c = _probs(records)
    if not p:
        return None
    return max(p, key=lambda x: abs(x - 0.5))


def strategy_mean(records, **_):
    """B: average the collapsed probabilities."""
    p, _ = _probs(records)
    return float(np.mean(p)) if p else None


def strategy_threshold(records, threshold=0.5, **_):
    """C: a fixed cutoff -- hard 0/1, no intermediate belief."""
    p, _ = _probs(records)
    if not p:
        return None
    return 1.0 if float(np.mean(p)) >= threshold else 0.0


def strategy_escalate_on_disagreement(records, divergence_threshold=0.1, **_):
    """D: agree -> use the mean; disagree -> ABSTAIN. Returns None when abstaining."""
    p, _ = _probs(records)
    if not p:
        return None
    if max_divergence(p) > divergence_threshold:
        return None            # ABSTAIN: a human decides
    return float(np.mean(p))


def strategy_llm_arbiter(records, client=None, **_):
    """E: hand it to a language model. Raises when no client is configured."""
    if client is None:
        raise RuntimeError(
            "no LLM client configured; this strategy is incomplete and must not be ranked")
    raise NotImplementedError("arbiter call not implemented")


STRATEGIES = {
    "A_most_confident": strategy_most_confident,
    "B_mean": strategy_mean,
    "C_threshold": strategy_threshold,
    "D_escalate_on_disagreement": strategy_escalate_on_disagreement,
    "E_llm_arbiter": strategy_llm_arbiter,
}


# --- comparison --------------------------------------------------------------------------

def freeze_cases(names):
    return hashlib.sha256("\n".join(names).encode()).hexdigest()[:16]


def evaluate_strategy(fn, per_case_records, labels, **kwargs):
    """Run one strategy over every frozen case. Abstentions are reported, not dropped."""
    preds, covered_idx = [], []
    for i, recs in enumerate(per_case_records):
        try:
            p = fn(recs, **kwargs)
        except (RuntimeError, NotImplementedError) as e:
            return {"status": INCOMPLETE, "reason": str(e)}
        if p is None:
            continue
        preds.append(p); covered_idx.append(i)
    y = np.asarray(labels)[covered_idx]
    p = np.asarray(preds)
    return {"status": "complete", "n_total": len(per_case_records),
            "n_covered": len(preds), "coverage": len(preds) / len(per_case_records),
            "y": y.tolist(), "p": p.tolist()}


def rank(results, key):
    """Rank only strategies that completed on every case. Incomplete ones are unranked."""
    ranked = {k: v for k, v in results.items()
              if v.get("status") == "complete" and v.get(key) is not None}
    order = sorted(ranked, key=lambda k: ranked[k][key],
                   reverse=(key == "accuracy"))
    return order, [k for k, v in results.items() if v.get("status") == INCOMPLETE]
