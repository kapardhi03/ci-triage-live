"""Tests for ci_triage.retrieval.

Two invariants, both invisible in the metric: a single-class index makes precision@k 1.0 by
construction, and a query retrieving its own document scores itself with its own label.
"""

import numpy as np
import pytest

from ci_triage.retrieval import SingleClassIndexError, build_index, query


def toy_vectors(n, seed=0):
    rng = np.random.default_rng(seed)
    V = rng.normal(size=(n, 8))
    return V / np.linalg.norm(V, axis=1, keepdims=True)


@pytest.fixture
def index():
    names = [f"T.t{i}" for i in range(10)]
    labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
    return build_index(names, [""] * 10, labels, vectors=toy_vectors(10))


# --- the bug this phase is about --------------------------------------------------------

def test_single_class_index_is_refused():
    """If every document is flaky, every vote returns flaky and precision@k is 1.0."""
    for labels in ([1] * 6, [0] * 6):
        with pytest.raises(SingleClassIndexError):
            build_index([f"T.t{i}" for i in range(6)], [""] * 6, labels,
                        vectors=toy_vectors(6))


def test_two_class_index_is_accepted(index):
    assert index["n_flaky"] == 5 and index["n_deterministic"] == 5


def test_refusal_message_explains_the_consequence():
    with pytest.raises(SingleClassIndexError, match="by construction"):
        build_index(["a", "b"], ["", ""], [1, 1], vectors=toy_vectors(2))


# --- query leakage ----------------------------------------------------------------------

def test_a_query_cannot_retrieve_itself(index):
    """Checked, not assumed -- the self-match sits at distance 0 with the right label."""
    for i, name in enumerate(index["names"]):
        r = query(index, index["vectors"][i], k=5, exclude_name=name)
        assert name not in [n["test"] for n in r["neighbours"]], f"{name} retrieved itself"


def test_without_the_guard_the_query_does_retrieve_itself(index):
    """The guard must be capable of mattering, or the test above proves nothing."""
    r = query(index, index["vectors"][3], k=5, exclude_name=None)
    assert r["neighbours"][0]["test"] == index["names"][3]
    assert r["neighbours"][0]["distance"] == pytest.approx(0.0, abs=1e-9)


# --- distinct tests, not neighbours -----------------------------------------------------

def test_n_distinct_is_reported_beside_k(index):
    r = query(index, index["vectors"][0], k=5, exclude_name=index["names"][0])
    assert r["k"] == 5
    assert "n_distinct" in r and 1 <= r["n_distinct"] <= 5


def test_index_state_travels_with_every_answer(index):
    """The output is meaningless without knowing what was in the index."""
    r = query(index, index["vectors"][0], k=3, exclude_name=index["names"][0])
    assert r["index_state"]["n_flaky"] == 5
    assert r["index_state"]["n_deterministic"] == 5


def test_probability_is_the_neighbour_vote(index):
    r = query(index, index["vectors"][0], k=4, exclude_name=index["names"][0])
    expected = np.mean([n["label"] for n in r["neighbours"]])
    assert r["probability"] == pytest.approx(expected)


# --- the component that ships -----------------------------------------------------------

from ci_triage.retrieval import ABSTAIN, MessageLookup


def test_lookup_abstains_on_an_unseen_message():
    """A lookup with no entry has nothing to say. Guessing costs 40h; abstaining 1.5h."""
    m = MessageLookup().fit(["timeout waiting", "connection reset"], [1, 0])
    r = m.predict("something nobody has ever seen")
    assert r["verdict"] == ABSTAIN
    assert r["probability"] is None, "abstain must not also emit a probability"


def test_lookup_returns_the_seen_outcome():
    m = MessageLookup().fit(["a", "a", "b"], [1, 1, 0])
    assert m.predict("a")["probability"] == pytest.approx(1.0)
    assert m.predict("b")["probability"] == pytest.approx(0.0)


def test_lookup_averages_a_message_seen_with_both_labels():
    """An ambiguous message must report its ambiguity, not pick a side."""
    m = MessageLookup().fit(["x", "x"], [1, 0])
    assert m.predict("x")["probability"] == pytest.approx(0.5)


def test_lookup_needs_no_index_and_cannot_go_stale_silently():
    """The stateful dependency in design/09 disappears: the table IS the state."""
    m = MessageLookup().fit(["a"], [1])
    assert m.predict("a")["n_entries"] == 1
    assert m.predict("zzz")["verdict"] == ABSTAIN
