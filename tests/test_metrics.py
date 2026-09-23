"""Tests for ci_triage.metrics — the ruler must be honest."""

import numpy as np
import pytest
from ci_triage.metrics import (
    constant_not_flaky,
    cost_weighted_risk,
    ece,
    evaluate,
    risk_coverage,
)


# --- Toy data: ~3% positive rate ---
Y_TRUE = np.array([0]*97 + [1]*3, dtype=float)
Y_CONST = constant_not_flaky(100)


def test_constant_high_accuracy_zero_recall():
    """The constant baseline scores high on accuracy AND zero on recall."""
    result = evaluate(Y_TRUE, Y_CONST)
    assert result["accuracy"] == pytest.approx(0.97)
    assert result["recall"] == 0.0


def test_constant_cost_is_not_zero():
    """Always predicting not-flaky still incurs cost: every missed defect ships."""
    risk = cost_weighted_risk(Y_TRUE, Y_CONST)
    assert risk > 0.0


def test_perfect_model_zero_cost():
    """A perfect predictor has zero cost-weighted risk."""
    risk = cost_weighted_risk(Y_TRUE, Y_TRUE)
    assert risk == 0.0


def test_ece_identical_inputs_identical_outputs():
    """Same (predictions, truth) must give the same ECE regardless of call order."""
    y_true = [0, 0, 0, 1, 1]
    y_prob = [0.1, 0.2, 0.3, 0.8, 0.9]
    ece1 = ece(y_true, y_prob, n_bins=5, strategy="equal_width")
    ece2 = ece(y_true, y_prob, n_bins=5, strategy="equal_width")
    assert ece1 == ece2


def test_ece_equal_width_flatters_imbalanced():
    """Equal-width bins hide miscalibration when every prediction lands in one bin.

    A model that outputs the 3% base rate for every case falls entirely into the
    first equal-width bin, where average confidence equals average accuracy by
    construction. Equal-width reports exactly 0.0 -- perfect calibration for a
    model that has learned nothing. Equal-frequency splits the ties and reports
    a non-zero number. Fails if equal-width ever stops reporting the flattering
    value, which would mean the binning changed underneath us.
    """
    y_prob_low = np.full(100, 0.03)  # predicts base rate for everything
    ece_ew = ece(Y_TRUE, y_prob_low, n_bins=10, strategy="equal_width")
    ece_ef = ece(Y_TRUE, y_prob_low, n_bins=10, strategy="equal_freq")
    assert ece_ew == pytest.approx(0.0, abs=1e-9)
    assert ece_ef > 0.01
    assert ece_ef > ece_ew


def test_ece_alone_prefers_the_useless_model():
    """Calibration without discrimination: ECE ranks a useless model above a perfect one.

    The base-rate model catches zero flaky tests and costs 1.2h/build. The perfect
    ranker catches all of them and costs 0. Equal-width ECE scores the useless one
    better. This test is the reason ECE may never be read on its own -- if it ever
    fails, either the metric changed or the trap stopped being real.
    """
    useless = np.full(100, 0.03)
    rng = np.random.default_rng(0)
    perfect = np.where(
        Y_TRUE == 1, rng.uniform(0.6, 0.9, 100), rng.uniform(0.0, 0.2, 100)
    )

    r_useless = evaluate(Y_TRUE, useless)
    r_perfect = evaluate(Y_TRUE, perfect)

    # ECE alone picks the wrong model
    assert r_useless["ece_equal_width"] < r_perfect["ece_equal_width"]
    # every metric that looks at discrimination or cost picks the right one
    assert r_useless["recall"] == 0.0 and r_perfect["recall"] == 1.0
    assert r_useless["cost_weighted_risk"] > r_perfect["cost_weighted_risk"]


def test_constant_model_auc_is_undefined_not_good():
    """A single-valued predictor cannot be ranked, so AUC must be None, not 0.5 or 1.0."""
    assert evaluate(Y_TRUE, constant_not_flaky(100))["roc_auc"] is None
    assert evaluate(Y_TRUE, np.full(100, 0.03))["roc_auc"] is None


def test_cost_table_asymmetry_is_enforced():
    """The ~13x asymmetry from phase 01 must show up in the numbers, not just the docstring.

    Missing a real defect (calling it flaky) ships a bug: ~40h. Holding a release on a
    flaky test: ~3h. If someone flattens the cost table, the ruler stops measuring the
    objective this system was built for, and this test fails.
    """
    # IsFlaky semantics: y == 1 is FLAKY, y == 0 is NOT flaky, i.e. a real defect.
    y_true = np.array([0, 1])         # one real defect, one flaky test
    ship_the_bug = np.array([1, 1])   # called the real defect flaky -> ships -> 40h
    needless_hold = np.array([0, 0])  # called the flaky test a real defect -> hold -> 3h

    cost_miss = cost_weighted_risk(y_true, ship_the_bug)
    cost_hold = cost_weighted_risk(y_true, needless_hold)

    assert cost_miss > cost_hold
    assert cost_miss / cost_hold == pytest.approx(40.0 / 3.0, rel=1e-6)


def test_the_expensive_error_is_calling_a_real_defect_flaky():
    """Direction check the old asymmetry test could not make.

    y=0 is a real defect. Predicting 1 (flaky) ships the bug: 40h. The inverse error --
    y=1 predicted 0 -- merely holds a release: 3h. An inverted table makes "call it
    flaky" look cheap, which points the system at exactly the mistake phase 01 priced
    highest. This test fails if the mapping flips.
    """
    assert cost_weighted_risk(np.array([0]), np.array([1])) == 40.0
    assert cost_weighted_risk(np.array([1]), np.array([0])) == 3.0


def test_abstain_is_cheap_but_not_free():
    """ABSTAIN must cost more than a correct call and less than a needless hold.

    Phase 01: if abstaining cost more than holding, the system would never use it;
    if it cost nothing, the system would abstain on everything.
    """
    y_true = np.array([0, 0])
    cost_abstain = cost_weighted_risk(y_true, np.array([-1, -1]))
    cost_correct = cost_weighted_risk(y_true, np.array([0, 0]))
    cost_hold = cost_weighted_risk(y_true, np.array([1, 1]))

    assert cost_correct == 0.0
    assert cost_correct < cost_abstain < cost_hold


def test_risk_coverage_returns_points():
    """Risk-coverage produces results at each threshold."""
    rc = risk_coverage(Y_TRUE, np.full(100, 0.03))
    assert len(rc) > 0
    assert all("coverage" in r and "risk" in r for r in rc)


def test_evaluate_deterministic():
    """Calling evaluate twice on the same inputs produces identical results."""
    r1 = evaluate(Y_TRUE, Y_CONST)
    r2 = evaluate(Y_TRUE, Y_CONST)
    for key in r1:
        assert r1[key] == r2[key], f"{key} differs between calls"
