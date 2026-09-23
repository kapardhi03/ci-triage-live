"""Tests for ci_triage.tabular — observer 1.

Two invariants carry this file. The model must never be fitted on rows from the held-out
projects, which is invisible in the metrics and fatal to every claim built on them. And the
qualifier must not be a function of the model's output, because that collapses the design
back into self-reported confidence -- the exact thing design/07 rejects.
"""

import numpy as np
import pytest
from sklearn.model_selection import LeaveOneGroupOut

from ci_triage.tabular import (
    ABSTAIN, FLAKY_SCORE, DistanceQualifier, make_model, observe,
)


@pytest.fixture
def toy():
    rng = np.random.default_rng(0)
    groups = np.repeat([f"p{i}" for i in range(5)], 60)
    X = rng.normal(size=(300, 4))
    # project p4 is deliberately alien: shifted far in feature 0
    X[groups == "p4", 0] += 12.0
    y = (rng.random(300) < 0.25).astype(int)
    return X, y, groups


# --- the phase invariant ---------------------------------------------------------------

def test_model_never_sees_the_held_out_project(toy):
    """A row from the held-out project reaching the fit is invisible in the metrics."""
    X, y, groups = toy
    for tr, te in LeaveOneGroupOut().split(X, y, groups):
        held = set(groups[te])
        assert not (set(groups[tr]) & held), f"held-out project leaked into training: {held}"
        assert len(held) == 1


def test_qualifier_is_fitted_without_the_held_out_project(toy):
    """The qualifier is part of the observer, so it inherits the same constraint.

    A qualifier fitted on all projects would consider every project familiar, including
    the one it is supposed to flag as alien.
    """
    X, y, groups = toy
    tr = groups != "p4"

    honest = DistanceQualifier().fit(X[tr], groups[tr])
    leaked = DistanceQualifier().fit(X, groups)          # fitted on everything

    assert honest.qualifier(X[~tr]) < leaked.qualifier(X[~tr]), (
        "a qualifier fitted on the held-out project cannot detect it as alien"
    )


# --- the qualifier is not the model's confidence ---------------------------------------

def test_qualifier_does_not_depend_on_the_model(toy):
    """Same rows, two differently-fitted models, identical qualifier.

    If this fails, the qualifier has become a function of model output and the design's
    central distinction is gone.
    """
    X, y, groups = toy
    tr = groups != "p4"
    q = DistanceQualifier().fit(X[tr], groups[tr])

    m1 = make_model(seed=0).fit(X[tr], y[tr])
    m2 = make_model(seed=7).fit(X[tr], 1 - y[tr])   # deliberately trained on flipped labels

    o1 = observe(m1, q, X[~tr])
    o2 = observe(m2, q, X[~tr])
    assert o1["qualifier"] == o2["qualifier"]


def test_alien_project_abstains_and_familiar_one_does_not(toy):
    """ABSTAIN is derived from the qualifier failing, not declared for unseen projects."""
    X, y, groups = toy
    tr = groups != "p4"
    q = DistanceQualifier().fit(X[tr], groups[tr])
    m = make_model().fit(X[tr], y[tr])

    alien = observe(m, q, X[groups == "p4"])
    assert alien["verdict"] == ABSTAIN
    assert alien["probability"] is None, "abstain must not also emit a probability"

    familiar = observe(m, q, X[groups == "p1"])
    assert familiar["verdict"] == FLAKY_SCORE
    assert familiar["probability"] is not None


def test_probability_is_never_emitted_without_its_qualifier(toy):
    """A consumer that can read the number without the caveat will do exactly that."""
    X, y, groups = toy
    tr = groups != "p4"
    q = DistanceQualifier().fit(X[tr], groups[tr])
    m = make_model().fit(X[tr], y[tr])
    for proj in ("p1", "p4"):
        out = observe(m, q, X[groups == proj])
        assert "qualifier" in out and out["qualifier"] is not None
        assert "dominant_distance_features" in out["evidence"]


def test_dominant_distance_features_are_reported(toy):
    """design/07 predicts ExecutionTime dominates. Emitting it makes the coupling checkable."""
    X, y, groups = toy
    tr = groups != "p4"
    q = DistanceQualifier().fit(X[tr], groups[tr], ["f0", "f1", "f2", "f3"])
    top = q.dominant_features(X[groups == "p4"])
    assert top[0]["feature"] == "f0", "the deliberately-shifted feature should dominate"
    assert 0.0 <= top[0]["share"] <= 1.0
