"""Experiment harness: specify a run so someone else gets the same number.

The split is the experiment. A random row-wise split lets a model score a test row using
what it learned about that row's project; holding out whole projects removes that route.
Which one is right is answered by deployment, not by which gives a nicer number --
see decisions/06-split-choice.md.

Splitting itself is sklearn's. This is the wiring, the reproducibility envelope, and the
refusal to average folds it has not disclosed.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut

LEDGER = Path("artifacts/results/test-set-access.log")


def make_split(name, n_splits=5, seed=0):
    """Named split strategies. The name travels into the run_id."""
    if name == "random_5fold":
        return KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    if name == "grouped_5fold":
        return GroupKFold(n_splits=n_splits)
    if name == "leave_one_project_out":
        return LeaveOneGroupOut()
    raise ValueError(f"unknown split: {name}")


def run_id(split, estimator, features, label, seed, data_digest):
    """Everything that can change a number is inside the hash."""
    payload = json.dumps({
        "split": split, "estimator": repr(estimator), "features": sorted(features),
        "label": label, "seed": seed, "data": data_digest,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def evaluate_split(X, y, groups, split_name, estimator_factory, scorer,
                   seed=0, n_splits=5):
    """Fit and score across folds. A fold that cannot be scored is reported, not dropped."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    groups = np.asarray(groups)
    splitter = make_split(split_name, n_splits=n_splits, seed=seed)

    folds, skipped = [], []
    for i, (tr, te) in enumerate(splitter.split(X, y, groups)):
        held = sorted(set(groups[te])) if split_name != "random_5fold" else None
        n_pos = int(y[te].sum())
        if len(np.unique(y[te])) < 2:
            skipped.append({
                "fold": i, "held_out": held, "n_test": len(te), "n_pos_test": n_pos,
                "reason": "AUC undefined: the test fold contains a single class",
            })
            continue
        model = estimator_factory()
        model.fit(X[tr], y[tr])
        prob = model.predict_proba(X[te])[:, 1]
        folds.append({
            "fold": i, "held_out": held, "n_train": len(tr), "n_test": len(te),
            "n_pos_test": n_pos, "auc": float(scorer(y[te], prob)),
        })

    aucs = [f["auc"] for f in folds]
    return {
        "split": split_name,
        "n_folds_evaluated": len(folds),
        "n_folds_skipped": len(skipped),
        "mean_auc": float(np.mean(aucs)) if aucs else None,
        "std_auc": float(np.std(aucs)) if aucs else None,
        "folds": folds,
        "skipped": skipped,
    }


def groups_are_disjoint(splitter, X, y, groups):
    """True iff no group appears on both sides of any fold. The phase invariant."""
    groups = np.asarray(groups)
    for tr, te in splitter.split(np.asarray(X), np.asarray(y), groups):
        if set(groups[tr]) & set(groups[te]):
            return False
    return True


def access_test_set(reason, run_id_, ledger=LEDGER):
    """The only route to the final test set. Logs first, returns after.

    Nothing here prevents a second call. The point is that the twelfth call is visible.
    """
    if not reason or not reason.strip():
        raise ValueError("test-set access requires a stated reason")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "run_id": run_id_,
             "reason": reason.strip()}
    with ledger.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def read_ledger(ledger=LEDGER):
    if not ledger.exists():
        return []
    return [json.loads(line) for line in ledger.read_text().splitlines() if line.strip()]
