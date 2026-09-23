"""Evaluation metrics for CI triage — the independent ruler."""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

# Cost table from phase 01 (engineer-hours).
#
# The label is IsFlaky: y == 1 means FLAKY, y == 0 means NOT flaky, i.e. a real defect.
# Getting this mapping backwards points the system at the wrong error -- it makes
# "call it flaky" look cheap, which is the 40h mistake. See decisions/02 (correction).
DEFAULT_COSTS = {
    "false_flaky": 40.0,   # y=0 (real defect) predicted 1 (flaky) -> bug ships
    "false_real": 3.0,     # y=1 (flaky) predicted 0 (real defect) -> needless hold
    "abstain": 1.5,        # engineer investigates manually
}


def constant_not_flaky(n):
    """Baseline: predict not-flaky for every input."""
    return np.zeros(n)


def ece(y_true, y_prob, n_bins=10, strategy="equal_width"):
    """Expected calibration error with selectable binning."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    n = len(y_true)
    if n == 0:
        return 0.0

    if strategy == "equal_width":
        bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
        bin_indices = np.digitize(y_prob, bin_edges[1:-1])
    elif strategy == "equal_freq":
        sorted_idx = np.argsort(y_prob)
        bin_indices = np.zeros(n, dtype=int)
        edges = np.array_split(sorted_idx, n_bins)
        for i, group in enumerate(edges):
            bin_indices[group] = i
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    ece_val = 0.0
    for b in range(n_bins):
        mask = bin_indices == b
        count = mask.sum()
        if count == 0:
            continue
        avg_confidence = y_prob[mask].mean()
        avg_accuracy = y_true[mask].mean()
        ece_val += (count / n) * abs(avg_accuracy - avg_confidence)
    return ece_val


def cost_weighted_risk(y_true, y_pred, costs=None):
    """Total expected cost from the phase 01 cost table."""
    costs = costs or DEFAULT_COSTS
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)
    if n == 0:
        return 0.0

    total = 0.0
    for yt, yp in zip(y_true, y_pred):
        if yp == -1:  # abstain
            total += costs["abstain"]
        elif yt == 0 and yp == 1:  # real defect called flaky -> bug ships
            total += costs["false_flaky"]
        elif yt == 1 and yp == 0:  # flaky called real defect -> needless hold
            total += costs["false_real"]
    return total / n


def risk_coverage(y_true, y_prob, thresholds=None, costs=None):
    """Risk vs. coverage as confidence threshold varies."""
    costs = costs or DEFAULT_COSTS
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    n = len(y_true)

    if thresholds is None:
        thresholds = np.linspace(0.0, 1.0, 21)

    results = []
    for t in thresholds:
        confidence = np.abs(y_prob - 0.5) * 2  # distance from 0.5, scaled to [0,1]
        mask = confidence >= t
        coverage = mask.sum() / n
        if coverage == 0:
            results.append({"threshold": t, "coverage": 0.0, "risk": 0.0})
            continue
        y_pred_covered = (y_prob[mask] >= 0.5).astype(int)
        risk = cost_weighted_risk(y_true[mask], y_pred_covered, costs)
        results.append({"threshold": t, "coverage": coverage, "risk": risk})
    return results


def evaluate(y_true, y_prob, y_pred=None, threshold=0.5, costs=None):
    """Run the full metric ladder on one set of predictions."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    if y_pred is None:
        y_pred = (y_prob >= threshold).astype(int)

    result = {
        "accuracy": accuracy_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred, zero_division=0.0),
        "precision": precision_score(y_true, y_pred, zero_division=0.0),
        "brier": brier_score_loss(y_true, y_prob),
        "ece_equal_width": ece(y_true, y_prob, strategy="equal_width"),
        "ece_equal_freq": ece(y_true, y_prob, strategy="equal_freq"),
        "cost_weighted_risk": cost_weighted_risk(y_true, y_pred, costs),
    }
    # ROC AUC needs both classes present
    if len(np.unique(y_true)) > 1 and len(np.unique(y_prob)) > 1:
        result["roc_auc"] = roc_auc_score(y_true, y_prob)
    else:
        result["roc_auc"] = None
    return result
