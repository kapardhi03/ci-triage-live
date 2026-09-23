"""Tests for ci_triage.sequences — the circularity guard.

The load-bearing test is test_prefix_and_suffix_never_share_a_run. If a run appears in both
halves, the label is partly a function of the features and the AUC is inflated by
construction -- the exact failure this phase exists to avoid.
"""

import numpy as np
import pytest

from ci_triage.sequences import (
    build_dataset, control_score, make_example, prefix_suffix_disjoint,
)


# --- the phase invariant ---------------------------------------------------------------

def test_prefix_and_suffix_never_share_a_run():
    for n in (10, 201, 2001, 7905):
        for k in (5, 200, 2000):
            if n <= k:
                continue
            pre, suf = prefix_suffix_disjoint(list(range(n)), k)
            assert pre & suf == set(), f"run in both halves at n={n}, k={k}"
            assert pre | suf == set(range(n)), "runs were lost between the halves"
            assert len(pre) == k


def test_the_disjointness_check_can_actually_fail():
    """Break it deliberately, per TASK step 5. A check that cannot fail proves nothing."""
    def overlapping(sequence, k, overlap=3):
        n = len(sequence)
        return set(range(min(k, n))), set(range(k - overlap, n))

    pre, suf = overlapping(list(range(1000)), 200)
    assert pre & suf != set(), "the deliberately-broken version should overlap"
    assert len(pre & suf) == 3


def test_label_is_read_only_from_the_suffix():
    """The prefix must not influence the label. Same suffix, opposite prefixes."""
    k = 4
    a = make_example([1, 1, 1, 1] + [0, 1, 0], k)   # prefix all fail
    b = make_example([0, 0, 0, 0] + [0, 1, 0], k)   # prefix all pass
    assert a["label"] == b["label"] == 1

    c = make_example([1, 0, 1, 0] + [0, 0, 0], k)   # prefix flips, suffix does not
    assert c["label"] == 0, "label leaked from the prefix"


def test_label_is_the_suffix_flipping():
    k = 2
    assert make_example([0, 0, 1, 0], k)["label"] == 1      # suffix has both
    assert make_example([0, 0, 1, 1], k)["label"] == 0      # suffix all fail
    assert make_example([1, 1, 0, 0], k)["label"] == 0      # suffix all pass


# --- refusals ---------------------------------------------------------------------------

def test_short_sequence_is_refused_not_padded():
    """A padded prefix is a fabricated history, and history is the entire input."""
    assert make_example([0, 1, 0], 10) is None
    assert make_example([0, 1, 0], 3) is None, "k == len leaves an empty suffix"
    assert make_example([0, 1, 0, 1], 3) is not None


def test_build_dataset_drops_short_sequences_rather_than_padding():
    seqs = {"a": [0] * 300, "b": [0] * 50, "c": [0] * 100 + [1] * 200}
    X, y, names, _ = build_dataset(seqs, 200)
    assert names == ["a", "c"], "short sequence was padded instead of dropped"
    assert X.shape == (2, 200)


# --- the control --------------------------------------------------------------------------

def test_control_is_the_prefix_failure_count():
    X = np.array([[0, 0, 0], [1, 0, 1], [1, 1, 1]])
    assert list(control_score(X)) == [0.0, 2.0, 3.0]


def test_control_uses_only_the_prefix():
    """The control must be computable from X alone -- no access to the suffix or label."""
    seqs = {"t": [1, 0] * 100 + [0] * 500}
    X, y, _, _ = build_dataset(seqs, 200)
    assert control_score(X)[0] == 100
