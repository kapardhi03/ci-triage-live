"""Observer 2: a test's run history as a sequence.

The circularity this guards against: IsFlaky is "both a pass and a fail were observed", so
a model given the whole sequence and asked to predict IsFlaky computes a property of its own
input. Here the features are the first k TRUSTED runs and the label is read from the rest,
so features and label share no run. See design/08-sequence-observer.md.
"""

import json
from pathlib import Path

import numpy as np

PREFIX_LENGTHS = (200, 2000)


def make_example(sequence, k):
    """Split one test's outcome sequence into (prefix, label) sharing no run.

    label = 1 iff the suffix contains both a pass and a fail, i.e. the test flips later.
    Returns None when the prefix cannot be filled -- a padded prefix is a fabricated
    history, and history is this observer's entire input.
    """
    if len(sequence) <= k:
        return None
    prefix, suffix = sequence[:k], sequence[k:]
    label = int(0 in suffix and 1 in suffix)
    return {"prefix": list(prefix), "suffix_len": len(suffix), "label": label,
            "prefix_len": k, "n_failures_in_prefix": int(sum(prefix))}


def build_dataset(sequences, k):
    """sequences: {test_name: [0/1, ...]} -> (X, y, names, meta)."""
    X, y, names, meta = [], [], [], []
    for name in sorted(sequences):
        ex = make_example(sequences[name], k)
        if ex is None:
            continue
        X.append(ex["prefix"]); y.append(ex["label"]); names.append(name)
        meta.append({"n_failures_in_prefix": ex["n_failures_in_prefix"],
                     "suffix_len": ex["suffix_len"]})
    return np.array(X, dtype=np.float32), np.array(y, dtype=int), names, meta


def control_score(X):
    """The control: count failures in the prefix. No training, no parameters."""
    return np.asarray(X, dtype=float).sum(axis=1)


def prefix_suffix_disjoint(sequence, k):
    """The phase invariant: no run may appear in both halves of the same example.

    Returns the index sets so a test can assert on them rather than trust a boolean.
    """
    n = len(sequence)
    prefix_idx = set(range(min(k, n)))
    suffix_idx = set(range(k, n))
    return prefix_idx, suffix_idx


def load_project(path):
    d = json.loads(Path(path).read_text())
    return d["project"], d["sequences"], d["n_trusted_runs"]


# --- the model -------------------------------------------------------------------------

def train_gru(X_tr, y_tr, X_te, hidden=16, epochs=30, seed=0, lr=0.01):
    """A small GRU over the outcome sequence. torch is imported here, not at module load."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    # subsample long prefixes to keep the sequence tractable: stride to <= 200 steps
    def shape(A):
        A = np.asarray(A, dtype=np.float32)
        if A.shape[1] > 200:
            stride = A.shape[1] // 200
            A = A[:, ::stride][:, :200]
        return torch.tensor(A).unsqueeze(-1)

    xtr, xte = shape(X_tr), shape(X_te)
    ytr = torch.tensor(np.asarray(y_tr, dtype=np.float32))

    model = nn.Sequential()
    gru = nn.GRU(input_size=1, hidden_size=hidden, batch_first=True)
    head = nn.Linear(hidden, 1)
    params = list(gru.parameters()) + list(head.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    pos_weight = torch.tensor(max((len(ytr) - ytr.sum()) / max(ytr.sum(), 1), 1.0))
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    for _ in range(epochs):
        opt.zero_grad()
        out, _ = gru(xtr)
        logits = head(out[:, -1, :]).squeeze(-1)
        loss = loss_fn(logits, ytr)
        loss.backward(); opt.step()

    with torch.no_grad():
        out, _ = gru(xte)
        return torch.sigmoid(head(out[:, -1, :]).squeeze(-1)).numpy()
