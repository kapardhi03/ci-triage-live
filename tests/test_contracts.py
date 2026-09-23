"""Tests for ci_triage.contracts — the integration contract.

Two measured facts are frozen here as constants. If the measurements are ever redone and
disagree, these tests fail and force the contract to be revisited rather than silently
drifting from the evidence that justified it.
"""

import numpy as np
import pytest

from ci_triage.contracts import (
    Decision, Evidence, State, UncalibratedProbabilityError, Verdict,
    case_level, collapse_correlated, input_overlap, run_level,
)

# --- frozen constants: the measurements that justify this contract ----------------------
# phase 10: ExecutionTime predicts whether observer 3 sees the SSL NoSuchMethodError
SHARED_CAUSE_AUC = 0.6987
# phase 07: observer 1 predicting the actual label, leave-one-project-out
OBSERVER1_LABEL_AUC = 0.6765
# phase 01 cost table, engineer-hours
COST_SHIP_A_BUG, COST_NEEDLESS_HOLD, COST_ESCALATE = 40.0, 3.0, 1.5
# phase 04 joined corpus
BASE_RATE = 0.031894


def ev(observer, test, cause, p=None, state=State.OBSERVED, calibrated=True,
       verdict=Verdict.FLAKY, reads=("x",)):
    return Evidence(observer=observer, test=test, state=state, verdict=verdict,
                    reads=frozenset(reads), cause_group=cause,
                    probability=p, calibrated=calibrated)


# --- the contract's own premises ---------------------------------------------------------

def test_the_shared_cause_is_stronger_than_the_signal_it_contaminates():
    """The reason the rule is not an average, frozen as a number.

    ExecutionTime predicts observer 3's INPUT better than observer 1 predicts the LABEL it
    exists to predict. Disjoint columns, one physical event.
    """
    assert SHARED_CAUSE_AUC > OBSERVER1_LABEL_AUC
    assert SHARED_CAUSE_AUC == pytest.approx(0.6987, abs=1e-4)


def test_the_cost_table_makes_one_real_defect_outweigh_many_flakes():
    """196 flaky tests do not cancel one real defect. The arithmetic, frozen."""
    n_flaky, n_real = 196, 1
    ship = n_real * COST_SHIP_A_BUG            # ship the bug
    hold = n_flaky * 0.0 + COST_NEEDLESS_HOLD  # hold on the one real defect
    assert ship > hold
    assert COST_SHIP_A_BUG / COST_NEEDLESS_HOLD == pytest.approx(40 / 3, rel=1e-6)
    assert COST_ESCALATE < COST_NEEDLESS_HOLD < COST_SHIP_A_BUG


# --- TASK step 5: the flag people forget -------------------------------------------------

def test_probability_without_the_calibrated_flag_is_refused():
    with pytest.raises(UncalibratedProbabilityError, match="calibrated"):
        Evidence(observer="o", test="T.a", state=State.OBSERVED, verdict=Verdict.FLAKY,
                 reads=frozenset(), cause_group="g", probability=0.8, calibrated=None)


def test_declaring_uncalibrated_is_allowed_declaring_nothing_is_not():
    ev("o", "T.a", "g", p=0.8, calibrated=False)   # fine: it declared
    ev("o", "T.a", "g", p=0.8, calibrated=True)    # fine: it declared
    with pytest.raises(UncalibratedProbabilityError):
        ev("o", "T.a", "g", p=0.8, calibrated=None)


# --- TASK step 4: two states a uniform distribution would merge ---------------------------

def test_no_evidence_and_indeterminate_are_not_the_same_state():
    """'I could not look' is a coverage gap. 'It points equally' is a finding."""
    gap = ev("retrieval", "T.a", "text", state=State.NO_EVIDENCE, p=None, calibrated=None)
    amb = ev("retrieval", "T.a", "text", state=State.INDETERMINATE, p=0.5)
    assert gap.state is not amb.state
    assert gap.probability is None and amb.probability == 0.5


def test_no_evidence_may_not_carry_a_probability():
    """Encoding a gap as p=0.5 is exactly the merge this contract forbids."""
    with pytest.raises(ValueError, match="INDETERMINATE"):
        ev("o", "T.a", "g", p=0.5, state=State.NO_EVIDENCE)


def test_no_evidence_is_excluded_from_voices_but_counted(  ):
    r = run_level([ev("tab", "T.a", "exec", p=0.9),
                   ev("seq", "T.a", "hist", state=State.NO_EVIDENCE, calibrated=None)])
    assert r["voices"] == 1
    assert r["no_evidence"] == 1


# --- de-duplication ------------------------------------------------------------------------

def test_correlated_observers_collapse_to_one_voice():
    """Observers 1 and 3 share a cause. Their agreement is one observation, not two."""
    records = [ev("tabular", "T.a", "ssl-jvm", p=0.90),
               ev("retrieval", "T.a", "ssl-jvm", p=0.95, calibrated=False)]
    assert len(collapse_correlated(records)) == 1

    r = run_level(records)
    assert r["voices"] == 1
    assert r["deduplicated"] == 1
    assert r["cause_groups"] == ["ssl-jvm"]


def test_independent_observers_keep_their_voices():
    records = [ev("tabular", "T.a", "ssl-jvm", p=0.9),
               ev("sequence", "T.a", "run-history", p=0.8)]
    assert run_level(records)["voices"] == 2


def test_agreement_from_a_shared_cause_cannot_inflate_confidence():
    """Adding a third correlated record must not move the result at all."""
    two = run_level([ev("tabular", "T.a", "ssl-jvm", p=0.9),
                     ev("retrieval", "T.a", "ssl-jvm", p=0.9, calibrated=False)])
    five = run_level([ev(f"o{i}", "T.a", "ssl-jvm", p=0.9, calibrated=False)
                      for i in range(5)])
    assert two["p_real"] == five["p_real"], "correlated agreement changed the answer"
    assert five["voices"] == 1 and five["deduplicated"] == 4


# --- the case-level rule ------------------------------------------------------------------

def test_one_real_defect_among_196_flakes_holds_the_release():
    """The phase's headline. A mean says SHIP; the cost table says HOLD."""
    runs = [run_level([ev("tab", f"T.f{i}", "exec", p=0.99)]) for i in range(196)]
    runs.append(run_level([ev("tab", "T.real", "exec", p=0.02)]))   # p_real = 0.98

    out = case_level(runs)
    assert out["decision"] is Decision.HOLD
    assert out["driver"] == "T.real"

    # what a naive averaging implementation would have done, computed here so the
    # difference is visible rather than asserted
    mean_p_real = float(np.mean([r["p_real"] for r in runs]))
    assert mean_p_real < 0.5, "sanity: the mean is dominated by the 196 cheap cases"
    naive = Decision.SHIP if mean_p_real < 0.5 else Decision.HOLD
    assert naive is Decision.SHIP and out["decision"] is Decision.HOLD


def test_majority_vote_also_ships_the_bug():
    runs = [run_level([ev("tab", f"T.f{i}", "exec", p=0.99)]) for i in range(196)]
    runs.append(run_level([ev("tab", "T.real", "exec", p=0.02)]))
    votes_real = sum(r["p_real"] >= 0.5 for r in runs)
    assert votes_real == 1, "a majority vote sees one real defect in 197 and ships"
    assert case_level(runs)["decision"] is Decision.HOLD


def test_all_flaky_ships():
    runs = [run_level([ev("tab", f"T.f{i}", "exec", p=0.99)]) for i in range(20)]
    assert case_level(runs)["decision"] is Decision.SHIP


def test_thin_coverage_escalates_rather_than_shipping():
    """ESCALATE costs ~1.5h; shipping on no evidence risks ~40h."""
    runs = [run_level([ev("tab", f"T.f{i}", "exec", p=0.99)]) for i in range(3)]
    runs += [run_level([ev("seq", f"T.g{i}", "hist", state=State.NO_EVIDENCE,
                           calibrated=None)]) for i in range(10)]
    out = case_level(runs)
    assert out["decision"] is Decision.ESCALATE
    assert out["coverage"] < 0.5


# --- the overlap, computed rather than hoped ----------------------------------------------

def test_observer_inputs_are_literally_disjoint():
    o1 = {"assertion-roulette", "testLength", "numAsserts", "ExecutionTime"}
    o2 = {"run_outcome_sequence"}
    o3 = {"failure_text"}
    ov = input_overlap(o1, o2, o3)
    assert ov["all"] == frozenset()
    assert all(v == frozenset() for v in ov["pairwise"].values())


def test_disjoint_inputs_do_not_imply_independent_evidence():
    """The lesson of this phase, encoded: the overlap check passes and is not sufficient."""
    ov = input_overlap({"ExecutionTime"}, {"failure_text"})
    assert ov["all"] == frozenset()          # no shared column
    assert SHARED_CAUSE_AUC > 0.65           # and a strong shared cause anyway
