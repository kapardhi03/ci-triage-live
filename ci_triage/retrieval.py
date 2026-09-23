"""Observer 3: retrieval. No training -- embed the failure text, look up neighbours, vote.

The bug this guards against is a single-class index. If every document carries the same
label, every vote returns that label and precision@k is 1.0 by construction -- a measurement
of the index's composition, not of retrieval. See decisions/09-index-contents.md.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors

MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SingleClassIndexError(ValueError):
    """Raised when an index carries only one label. Refusal, not a warning."""


def embed(texts, model_name=MODEL):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name).encode(
        list(texts), convert_to_numpy=True, normalize_embeddings=True,
        show_progress_bar=False)


def build_index(names, texts, labels, vectors=None, model_name=MODEL):
    """One document per test. Refuses a single-class corpus."""
    labels = np.asarray(labels, dtype=int)
    if len(np.unique(labels)) < 2:
        raise SingleClassIndexError(
            f"index carries one class only ({labels[0] if len(labels) else 'empty'}); "
            f"every vote would return it and precision@k would be 1.0 by construction")
    V = embed(texts, model_name) if vectors is None else np.asarray(vectors, dtype=float)
    nn = NearestNeighbors(metric="cosine").fit(V)
    return {"names": list(names), "labels": labels, "vectors": V, "nn": nn,
            "n_documents": len(names), "n_flaky": int(labels.sum()),
            "n_deterministic": int((labels == 0).sum())}


def query(index, vector, k=5, exclude_name=None):
    """Vote over the top-k neighbours. A query never retrieves its own document."""
    v = np.asarray(vector, dtype=float).reshape(1, -1)
    # ask for extra so the self-match can be dropped without shrinking k
    n_ask = min(k + 5, index["n_documents"])
    dist, idx = index["nn"].kneighbors(v, n_neighbors=n_ask)
    dist, idx = dist[0], idx[0]

    keep = [(d, i) for d, i in zip(dist, idx)
            if exclude_name is None or index["names"][i] != exclude_name][:k]
    if not keep:
        return None
    neighbours = [{"test": index["names"][i], "label": int(index["labels"][i]),
                   "distance": float(d)} for d, i in keep]
    distinct = len({n["test"] for n in neighbours})
    return {
        "probability": float(np.mean([n["label"] for n in neighbours])),
        "neighbours": neighbours, "k": len(neighbours), "n_distinct": distinct,
        "index_state": {k_: index[k_] for k_ in
                        ("n_documents", "n_flaky", "n_deterministic")},
    }


# --- what actually ships ----------------------------------------------------------------
#
# Phase 09 measured MiniLM embeddings + 5-NN at precision 0.9851 on square-okhttp, against
# a majority baseline of 0.5050. A single substring check scores 0.9851 -- identical to four
# decimals -- and an exact-message lookup scores 0.9940 where it has a match. The corpus has
# 19 distinct messages across 202 tests, so there is one real decision boundary and every
# method finds it. Retrieval is retained above as the measured control; the lookup is the
# component. See decisions/09-index-contents.md.

ABSTAIN = "ABSTAIN"


class MessageLookup:
    """Exact failure-message -> outcome lookup. No model, no index, nothing to go stale.

    Abstains on a message it has never seen, rather than guessing. A lookup with no entry
    has nothing to say, and phase 01 prices an abstain at ~1.5h against ~40h for a wrong
    'flaky' call.
    """

    def __init__(self):
        self.table = {}

    def fit(self, texts, labels):
        from collections import defaultdict
        seen = defaultdict(list)
        for t, y in zip(texts, labels):
            seen[t].append(int(y))
        self.table = {t: float(np.mean(v)) for t, v in seen.items()}
        return self

    def predict(self, text):
        if text not in self.table:
            return {"probability": None, "verdict": ABSTAIN,
                    "reason": "no entry for this failure message",
                    "n_entries": len(self.table)}
        p = self.table[text]
        return {"probability": p, "verdict": "FLAKY_SCORE",
                "reason": f"exact match on a message seen with mean label {p:.2f}",
                "n_entries": len(self.table)}
