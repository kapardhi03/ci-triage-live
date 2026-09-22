"""Tests for ci_triage.splits — a project on both sides of a fold is invisible and fatal."""

import json
import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from ci_triage.splits import (
    access_test_set, evaluate_split, groups_are_disjoint, make_split, read_ledger, run_id,
)


@pytest.fixture
def toy():
    rng = np.random.default_rng(0)
    groups = np.repeat([f"p{i}" for i in range(6)], 40)
    X = rng.normal(size=(240, 3))
    y = (rng.random(240) < 0.2).astype(int)
    return X, y, groups


# --- the phase invariant ---------------------------------------------------------------

def test_grouped_splits_never_leak_a_project(toy):
    X, y, groups = toy
    for name in ("grouped_5fold", "leave_one_project_out"):
        assert groups_are_disjoint(make_split(name, n_splits=3), X, y, groups), name


def test_random_split_does_leak_and_the_check_detects_it(toy):
    """The detector must be capable of failing, or it proves nothing above."""
    X, y, groups = toy
    assert not groups_are_disjoint(make_split("random_5fold"), X, y, groups)


def test_leave_one_project_out_holds_out_exactly_one_project(toy):
    X, y, groups = toy
    r = evaluate_split(X, y, groups, "leave_one_project_out", _lr, roc_auc_score)
    for f in r["folds"] + r["skipped"]:
        assert len(f["held_out"]) == 1


# --- disclosure ------------------------------------------------------------------------

def _lr():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))


def test_single_class_fold_is_reported_not_silently_dropped():
    """jimfs and commons-exec have zero positives. Averaging 23 while reporting 25 is a lie."""
    rng = np.random.default_rng(1)
    groups = np.repeat(["a", "b", "c"], 40)
    X = rng.normal(size=(120, 3))
    y = np.array([1, 0] * 20 + [1, 0] * 20 + [0] * 40)  # project c has no positives

    r = evaluate_split(X, y, groups, "leave_one_project_out", _lr, roc_auc_score)
    assert r["n_folds_skipped"] == 1
    assert r["skipped"][0]["held_out"] == ["c"]
    assert r["skipped"][0]["n_pos_test"] == 0
    assert "single class" in r["skipped"][0]["reason"]
    assert r["n_folds_evaluated"] == 2
    assert len(r["folds"]) == r["n_folds_evaluated"]


def test_mean_is_taken_only_over_evaluated_folds(toy):
    X, y, groups = toy
    r = evaluate_split(X, y, groups, "grouped_5fold", _lr, roc_auc_score, n_splits=3)
    assert r["mean_auc"] == pytest.approx(np.mean([f["auc"] for f in r["folds"]]))


# --- reproducibility envelope ----------------------------------------------------------

def test_run_id_changes_when_anything_that_changes_a_number_changes():
    base = dict(split="grouped_5fold", estimator="LR", features=["a", "b"],
                label="IsFlaky", seed=0, data_digest={"rows": 10})
    ref = run_id(**base)
    assert run_id(**{**base, "split": "random_5fold"}) != ref
    assert run_id(**{**base, "estimator": "GB"}) != ref
    assert run_id(**{**base, "features": ["a", "b", "c"]}) != ref
    assert run_id(**{**base, "label": "flaky"}) != ref
    assert run_id(**{**base, "seed": 1}) != ref
    assert run_id(**{**base, "data_digest": {"rows": 11}}) != ref
    assert run_id(**{**base, "features": ["b", "a"]}) == ref, "feature order must not matter"


# --- the test-set ledger ---------------------------------------------------------------

def test_test_set_access_is_logged_and_needs_a_reason(tmp_path):
    ledger = tmp_path / "access.log"
    with pytest.raises(ValueError):
        access_test_set("", "abc", ledger=ledger)
    assert not ledger.exists()

    access_test_set("final evaluation of the chosen model", "abc", ledger=ledger)
    access_test_set("second look", "abc", ledger=ledger)
    entries = read_ledger(ledger)
    assert len(entries) == 2, "repeat access must accumulate, not overwrite"
    assert entries[1]["reason"] == "second look"
    assert all("ts" in e and "run_id" in e for e in entries)
