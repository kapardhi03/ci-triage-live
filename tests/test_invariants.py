"""Slice 13 — the instruments.

Loud slices (00, 01, 03, 10) announce their own failures: they throw, return empty, or
crash. They need no instrument here.

Silent slices keep emitting a plausible number. Each one below has an invariant that fires
on the failure the slice cannot self-report.

Three of these failures already happened in this repository and NONE was caught by a
passing test -- the inverted cost mapping (02, five phases green), the circular leak test
(04, green either way), and the unsatisfiable keep criterion (08, would have dropped the
model by arithmetic). All three were found by deliberately trying to break something.

Every frozen constant below is hardcoded HERE, independent of the module it grades. A test
that grades code against a number that code computed is the circular failure again.
"""

import json
import pathlib

import numpy as np
import pytest

from ci_triage.contracts import (
    Evidence, State, Verdict, collapse_correlated, explain,
)
from ci_triage.metrics import cost_weighted_risk
from ci_triage.retrieval import ABSTAIN, MessageLookup, SingleClassIndexError, build_index
from ci_triage.splits import groups_are_disjoint, make_split

RESULTS = pathlib.Path("artifacts/results")


def _artifact(name):
    p = RESULTS / name
    if not p.exists():
        pytest.skip(f"SKIPPED: {p} not present -- regenerate it; a skip is not a pass")
    return json.loads(p.read_text())


# --- 02 evaluation: the inverted cost mapping -------------------------------------------

def test_02_cost_of_the_expensive_error_exceeds_the_cheap_one():
    """Frozen from phase 01, graded against hardcoded costs, not the mapping under test.

    IsFlaky: y=1 is flaky, y=0 is a real defect. Calling a real defect flaky ships the bug
    (~40h). Calling a flaky test a real defect holds the release (~3h). Inverted, the table
    makes "call it flaky" look cheap -- it aims the system at the expensive mistake, and it
    passed every test for five phases.
    """
    SHIP_A_BUG, NEEDLESS_HOLD = 40.0, 3.0

    ship = cost_weighted_risk(np.array([0]), np.array([1]))
    hold = cost_weighted_risk(np.array([1]), np.array([0]))

    assert ship == SHIP_A_BUG, "a real defect called flaky must cost the expensive number"
    assert hold == NEEDLESS_HOLD
    assert ship > hold
    assert ship / hold == pytest.approx(40 / 3, rel=1e-9)


# --- 04 ingestion: the circular leak test ------------------------------------------------

FORBIDDEN_IN_FEATURES = (
    "IsFlaky", "NumFailingRuns", "NumPassingRuns", "FirstFailingRunID",
    "FirstPassingRunID", "UniqueFailingExceptionTypes", "flaky", "flaky_source",
)


def test_04_no_forbidden_column_reaches_the_feature_matrix():
    """Graded against a list this file owns, not against the module's own EXCLUDED dict.

    The original version compared X.columns to ci_triage.data.EXCLUDED, so deleting an
    entry made both sides agree and the test stayed green.
    """
    eda = _artifact("eda.json")
    present = [c for c in FORBIDDEN_IN_FEATURES if c in eda["features"]]
    assert present == [], f"forbidden columns in the feature matrix: {present}"


def test_04_an_unexcluded_leak_would_be_detected():
    """The guard must be capable of failing, or the test above proves nothing."""
    pretend_features = list(_artifact("eda.json")["features"]) + ["NumFailingRuns"]
    present = [c for c in FORBIDDEN_IN_FEATURES if c in pretend_features]
    assert present == ["NumFailingRuns"], "the check cannot detect a reintroduced leak"


# --- 05 trust gate: a mis-parse still returns a verdict ----------------------------------

def test_05_gate_deterministic_set_matches_ground_truth():
    """Frozen cross-check: the gate derived 102 always-failing tests from maven.log text
    alone; test_results.csv defines the same set independently. Jaccard 1.000.

    This grades the recorded artifact, not a live re-run -- a mis-parse that regenerated
    the artifact would still be caught, a mis-parse that left it stale would not.
    """
    v = _artifact("infra.json")["validation"]
    assert v["gate_found"] == 102 and v["csv_found"] == 102
    assert v["intersection"] == 102
    assert v["gate_only"] == 0 and v["csv_only"] == 0
    assert v["jaccard"] == 1.0


# --- 06 splits: a leaky split still yields an AUC ----------------------------------------

def test_06_no_project_spans_a_grouped_split():
    rng = np.random.default_rng(0)
    groups = np.repeat([f"p{i}" for i in range(6)], 30)
    X, y = rng.normal(size=(180, 3)), (rng.random(180) < 0.3).astype(int)
    for name in ("grouped_5fold", "leave_one_project_out"):
        assert groups_are_disjoint(make_split(name, n_splits=3), X, y, groups), name


def test_06_a_random_split_does_leak_and_the_detector_says_so():
    rng = np.random.default_rng(0)
    groups = np.repeat([f"p{i}" for i in range(6)], 30)
    X, y = rng.normal(size=(180, 3)), (rng.random(180) < 0.3).astype(int)
    assert not groups_are_disjoint(make_split("random_5fold"), X, y, groups)


def test_06_zero_positive_folds_are_skipped_not_scored():
    """jimfs and commons-exec carry no positives. Averaging 23 while reporting 25 is a lie."""
    b = _artifact("baseline.json")["splits"]["leave_one_project_out"]
    assert b["n_folds_evaluated"] == 23
    assert b["n_folds_skipped"] == 2
    assert len(b["folds"]) == b["n_folds_evaluated"]
    for s in b["skipped"]:
        assert s["n_pos_test"] == 0 and "single class" in s["reason"]


# --- 07 observer 1: a broken observer still emits probabilities --------------------------

OBSERVER1_MAX_PROBABILITY = 0.1609   # frozen, phase 11, over the 202 frozen cases


def test_07_tabular_observer_never_crosses_the_decision_threshold():
    """It ranks at AUC 0.678 and never exceeds 0.1609, so it cannot flip a verdict alone.

    If this ever fails the observer has changed materially and every claim that it is inert
    -- including phase 11's conclusion that fusion runs over two voices -- must be redone.
    """
    o = _artifact("fusion.json")["observers"]["tabular"]
    assert o["max"] == pytest.approx(OBSERVER1_MAX_PROBABILITY, abs=1e-4)
    assert o["max"] < 0.5, "observer 1 crossed the threshold; it is no longer inert"


def test_07_removing_the_inert_observer_flips_no_verdict():
    recs = [
        Evidence("tabular", "T.a", State.OBSERVED, Verdict.FLAKY,
                 frozenset({"ExecutionTime"}), "ssl-jvm", probability=0.09, calibrated=True),
        Evidence("lookup", "T.a", State.OBSERVED, Verdict.FLAKY,
                 frozenset({"text"}), "ssl-jvm", probability=1.0, calibrated=False),
    ]
    with_it = explain(recs, Verdict.FLAKY)["basis"]
    without = explain(recs[1:], Verdict.FLAKY)["basis"]
    assert with_it == without == "lookup"


# --- 08 observer 2: the unsatisfiable criterion ------------------------------------------

def test_08_keep_criterion_is_satisfiable_where_it_is_applied():
    """A criterion that cannot fire is not a test. 'Beat the control by 0.05 in every cell'
    was unsatisfiable in 3 of 6 cells -- kevinsawicki sat at 1.0000, tootallnate/2000 at
    0.9992. Any margin rule must be checked against the headroom before it is adopted.
    """
    MARGIN = 0.05
    controls = {"kevinsawicki|200": 1.0000, "kevinsawicki|2000": 1.0000,
                "okhttp|200": 0.4967, "okhttp|2000": 0.7897,
                "tootallnate|200": 0.8478, "tootallnate|2000": 0.9992}
    satisfiable = {k: (1.0 - v) >= MARGIN for k, v in controls.items()}
    assert sum(satisfiable.values()) == 3, "headroom changed; revisit the criterion"
    assert satisfiable["okhttp|200"] is True, "the decision cell must be satisfiable"
    assert satisfiable["kevinsawicki|200"] is False


def test_08_the_decision_cell_criterion_fired_against_the_model():
    s = _artifact("sequence.json")["criterion_preregistered"]
    assert s["fired"] is True and s["verdict"] == "THROW AWAY"
    assert s["result"] < s["threshold"]


# --- 09 observer 3: silently answering cases it should decline ---------------------------

def test_09_lookup_abstains_rather_than_guessing():
    m = MessageLookup().fit(["known message"], [1])
    r = m.predict("a message nobody has ever seen")
    assert r["verdict"] == ABSTAIN
    assert r["probability"] is None, "abstain must not also emit a probability"


def test_09_accuracy_is_never_reported_without_coverage():
    s = _artifact("retrieval.json")["shipped_component"]
    assert "coverage" in s and "precision_on_covered" in s
    assert 0.0 < s["coverage"] < 1.0
    assert s["n_abstained"] > 0


def test_09_single_class_index_is_refused():
    with pytest.raises(SingleClassIndexError):
        build_index(["a", "b"], ["", ""], [1, 1],
                    vectors=np.eye(2))


# --- 11 fusion: identical strategies wearing three names ---------------------------------

def test_11_voice_count_is_post_deduplication():
    recs = [Evidence(f"o{i}", "T.a", State.OBSERVED, Verdict.FLAKY,
                     frozenset({f"r{i}"}), "ssl-jvm", probability=0.9, calibrated=False)
            for i in range(5)]
    assert len(collapse_correlated(recs)) == 1
    assert explain(recs, Verdict.FLAKY)["voices"] == 1
    assert len(explain(recs, Verdict.FLAKY)["suppressed"]) == 4


def test_11_correlated_agreement_cannot_inflate_confidence():
    two = [Evidence("a", "T.a", State.OBSERVED, Verdict.FLAKY, frozenset(), "g", probability=0.9, calibrated=False),
           Evidence("b", "T.a", State.OBSERVED, Verdict.FLAKY, frozenset(), "g", probability=0.9, calibrated=False)]
    five = two + [Evidence(f"c{i}", "T.a", State.OBSERVED, Verdict.FLAKY, frozenset(), "g",
                           probability=0.9, calibrated=False) for i in range(3)]
    assert explain(two, Verdict.FLAKY)["voices"] == explain(five, Verdict.FLAKY)["voices"] == 1


def test_11_strategies_that_agree_on_every_case_are_reported_as_such():
    f = _artifact("fusion.json")["identical_decisions"]
    assert f["A_vs_B"] == "202/202"
    assert "one decision rule" in f["verdict"]


# --- 12 explanation: a fluent account of a wrong verdict ---------------------------------

def test_12_every_explanation_field_traces_to_a_record_field():
    """Structural, because correctness cannot be checked at emit time."""
    recs = [Evidence("lookup", "T.a", State.OBSERVED, Verdict.FLAKY,
                     frozenset({"text"}), "ssl-jvm", probability=1.0, calibrated=False)]
    out = explain(recs, Verdict.FLAKY)
    untraced = set(out) - {"trace"} - set(out["trace"])
    assert untraced == set(), f"fields with no record provenance: {untraced}"
    assert all(v.startswith("Evidence.") for v in out["trace"].values())


def test_12_thin_and_split_evidence_are_flagged_as_such():
    one_voice = [Evidence("lookup", "T.a", State.OBSERVED, Verdict.FLAKY,
                          frozenset(), "g", probability=1.0, calibrated=False)]
    assert explain(one_voice, Verdict.FLAKY)["evidence_level"] == "THIN"

    split = one_voice + [Evidence("seq", "T.a", State.OBSERVED, Verdict.FLAKY,
                                  frozenset(), "h", probability=0.0, calibrated=False)]
    assert explain(split, Verdict.FLAKY)["evidence_level"] == "SPLIT"


def test_12_explanation_never_asserts_the_verdict():
    """The whole structural protection: it states the basis, never the belief."""
    recs = [Evidence("lookup", "T.a", State.OBSERVED, Verdict.FLAKY,
                     frozenset(), "g", probability=1.0, calibrated=False)]
    out = explain(recs, Verdict.FLAKY)
    assert "verdict" not in out
    blob = json.dumps(out).lower()
    for word in ("because", "therefore", "proves", "indicates that"):
        assert word not in blob, f"the explanation argued the conclusion: {word!r}"
