"""Tests for ci_triage.data — the leak guard must be unbypassable.

The load-bearing test here is test_no_column_predicts_the_label_alone. The named-column
tests catch a regression in the list we already know about; that one catches a leak nobody
has thought of yet, which is the failure mode that actually ships.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

from ci_triage.data import EXCLUDED, LABEL, feature_matrix, load_joined

# Recorded in artifacts/results/eda.json from a real run. See decisions/04-dataset-choice.md.
EXPECTED_ROWS = 26134
EXPECTED_POSITIVES = 825
EXPECTED_PROJECTS = 25

pytestmark = pytest.mark.skipif(
    not (__import__("pathlib").Path("data/raw/test_features.csv").exists()),
    reason="data/raw not fetched — run scripts/fetch_raw.sh",
)


@pytest.fixture(scope="module")
def matrix():
    return feature_matrix()


def test_no_excluded_column_reaches_the_feature_matrix(matrix):
    """The invariant from design/04. Fails if any denied column comes back."""
    X, _, _, _ = matrix
    leaked = sorted(set(X.columns) & set(EXCLUDED))
    assert leaked == [], f"excluded columns present in X: {leaked}"


# Frozen independently of ci_triage.data.EXCLUDED, on purpose.
# test_no_excluded_column_reaches_the_feature_matrix is circular -- it grades X against
# EXCLUDED, so deleting an entry from EXCLUDED makes both sides agree and the test still
# passes. This list is the non-circular guard: to defeat it you have to edit the test,
# which is a reviewable act rather than an accident.
MUST_NEVER_APPEAR = (
    "IsFlaky",                      # the label itself
    "NumFailingRuns",               # IsFlaky is `both > 0`
    "NumPassingRuns",
    "FirstFailingRunID",            # AUC 1.000 alone
    "FirstPassingRunID",
    "UniqueFailingExceptionTypes",  # AUC 0.998
    "flaky",                        # the tool label -- a label, not a feature
    "flaky_source",                 # non-null exactly when `flaky` is 1
)


def test_label_and_its_bookkeeping_are_absent(matrix):
    """No label, no label-derived column, graded against a list this module owns.

    flaky_source is here despite scoring only 0.53 against IsFlaky. It is not a leak for
    this label, but it is another detector's output: at 02:47 on an unseen project nobody
    has run IDFlakies, so a model leaning on it cannot be deployed. Same reasoning as the
    dropped history columns -- availability, not correlation.
    """
    X, _, _, _ = matrix
    present = [c for c in MUST_NEVER_APPEAR if c in X.columns]
    assert present == [], f"forbidden columns reached the feature matrix: {present}"


def test_no_column_predicts_the_label_alone(matrix):
    """No surviving feature may separate the classes on its own.

    This is the test that catches a leak nobody listed. A real feature carries partial
    signal; a column computed from the label separates almost perfectly. The strongest
    legitimate feature here is ExecutionTime at ~0.76, so 0.95 leaves wide headroom while
    still failing loudly on anything label-derived (the four rerun columns score
    0.993-1.000).
    """
    X, y, _, _ = matrix
    offenders = []
    for col in X.columns:
        v = pd.to_numeric(X[col], errors="coerce")
        if v.notna().sum() == 0 or v.nunique() < 2:
            continue
        v = v.fillna(v.median())
        auc = roc_auc_score(y, v)
        auc = max(auc, 1 - auc)
        if auc > 0.95:
            offenders.append((col, round(auc, 4)))
    assert offenders == [], f"columns separating the label almost perfectly: {offenders}"


def test_the_guard_is_not_a_step_someone_can_skip():
    """There is no code path that returns features without passing the guard.

    feature_matrix is the only public function returning X, and load_joined -- the raw
    join -- deliberately still contains the leaking columns. If a future refactor makes
    the join the feature source, this test fails.
    """
    joined, _ = load_joined()
    assert "NumFailingRuns" in joined.columns, (
        "load_joined no longer carries raw columns; if it became the feature source, "
        "the guard in feature_matrix is now bypassable"
    )


def test_shape_matches_the_recorded_run(matrix):
    """Guards the join key. A silently broken join changes these numbers."""
    X, y, groups, manifest = matrix
    assert len(X) == EXPECTED_ROWS
    assert int(y.sum()) == EXPECTED_POSITIVES
    assert groups.nunique() == EXPECTED_PROJECTS
    assert manifest["positive_rate"] == pytest.approx(0.031568, abs=1e-5)


def test_label_is_the_rerun_label_not_the_tool_label(matrix):
    """825 rerun-proven positives, not the 203 the tools found. Fails if the label flips."""
    _, y, _, manifest = matrix
    assert manifest["label"] == "IsFlaky"
    assert int(y.sum()) == EXPECTED_POSITIVES
    assert int(y.sum()) > 700, "looks like the tool label (~203 positives) crept in"


def test_no_row_has_a_manufactured_label(matrix):
    """Rows with no rerun outcome are dropped, never defaulted to 0."""
    X, y, _, _ = matrix
    assert len(X) == len(y)
    assert y.notna().all()
    assert set(y.unique()) <= {0, 1}


def test_groups_are_projects_for_the_phase_06_split(matrix):
    """Phase 06 holds out whole projects, so groups must be project-level."""
    X, _, groups, _ = matrix
    assert len(groups) == len(X)
    assert groups.nunique() == EXPECTED_PROJECTS
    assert groups.isna().sum() == 0
