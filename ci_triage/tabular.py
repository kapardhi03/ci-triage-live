"""Observer 1: a gradient-boosted tree over the tabular features, plus an evidence qualifier.

The qualifier is distributional distance from the training projects, NOT the model's own
confidence. A model on an unseen project does not know it is on an unseen project; it is
most confident exactly where it is least entitled to be. See design/07-tabular-and-the-pivot.md.
"""

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

FLAKY_SCORE, ABSTAIN = "FLAKY_SCORE", "ABSTAIN"


def make_model(seed=0):
    return HistGradientBoostingClassifier(random_state=seed, max_iter=200,
                                          early_stopping=False)


def make_calibrated(method="sigmoid", seed=0, cv=3):
    return CalibratedClassifierCV(make_model(seed), method=method, cv=cv)


class DistanceQualifier:
    """How far a project sits from the training distribution, in standardised feature space.

    Fitted on training rows only. Deliberately independent of the model: it never sees the
    model's output, the label, or anything the model produces.
    """

    def __init__(self):
        self.scaler = None
        self.centroids = None
        self.reference = None
        self.feature_names = None

    def fit(self, X, groups, feature_names=None):
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=np.nanmedian(np.where(np.isnan(X), np.nan, X)))
        self.scaler = StandardScaler().fit(X)
        Z = self.scaler.transform(X)
        groups = np.asarray(groups)
        self.centroids = np.vstack([Z[groups == g].mean(axis=0) for g in np.unique(groups)])
        # reference scale: how far training projects sit from each other
        d = [np.linalg.norm(self.centroids - c, axis=1) for c in self.centroids]
        pooled = np.concatenate([np.delete(x, i) for i, x in enumerate(d)])
        self.reference = float(np.percentile(pooled, 90)) or 1.0
        self.feature_names = list(feature_names) if feature_names is not None else None
        return self

    def distance(self, X):
        """Distance of these rows' centroid to the nearest training project centroid."""
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X)
        z = self.scaler.transform(X).mean(axis=0)
        return float(np.min(np.linalg.norm(self.centroids - z, axis=1)))

    def qualifier(self, X):
        """1.0 = indistinguishable from a training project, 0.0 = alien."""
        return float(np.clip(1.0 - self.distance(X) / self.reference, 0.0, 1.0))

    def dominant_features(self, X, top=3):
        """Which standardised features drive the distance. Makes the coupling observable."""
        X = np.nan_to_num(np.asarray(X, dtype=float))
        z = self.scaler.transform(X).mean(axis=0)
        nearest = self.centroids[np.argmin(np.linalg.norm(self.centroids - z, axis=1))]
        contrib = np.abs(z - nearest)
        order = np.argsort(contrib)[::-1][:top]
        names = self.feature_names or [f"f{i}" for i in range(len(contrib))]
        total = contrib.sum() or 1.0
        return [{"feature": names[i], "share": float(contrib[i] / total)} for i in order]


def observe(model, qualifier, X, threshold=0.5):
    """Emit a probability plus its qualifier, or ABSTAIN when the project is alien."""
    q = qualifier.qualifier(X)
    prob = model.predict_proba(X)[:, 1]
    evidence = {
        "distance": qualifier.distance(X),
        "reference": qualifier.reference,
        "dominant_distance_features": qualifier.dominant_features(X),
    }
    if q < threshold:
        return {"probability": None, "qualifier": q, "verdict": ABSTAIN,
                "evidence": {**evidence, "raw_score_mean": float(prob.mean())}}
    return {"probability": prob, "qualifier": q, "verdict": FLAKY_SCORE,
            "evidence": evidence}
