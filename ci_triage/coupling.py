"""Derive `cause_group` from measured coupling instead of assigning it by hand.

Phase 10 assigned observers 1 and 3 the same cause_group from one AUC measurement, and
`.ci-lab/interviews/10.md` conceded that the contract enforces a grouping rather than
detecting one. `docs/prior-work.md` named the standard instruments; this applies them.

Two pairwise measures over hard predictions:

  double-fault  -- fraction of cases where BOTH observers are wrong. Kuncheva's motivation
                   is exactly this case: simultaneous errors matter more than simultaneous
                   correctness, because two observers driven by one cause fail together.
  Q statistic   -- (N11*N00 - N01*N10) / (N11*N00 + N01*N10). Q ~ 0 independent, Q -> 1
                   strongly correlated. Normalises for how often each is right, which raw
                   double-fault does not.

    uv run python -m ci_triage.coupling
"""

import json
from itertools import combinations
from pathlib import Path

import numpy as np

INPUTS = Path("artifacts/results/fusion-inputs.json")
OUT = Path("artifacts/results/coupling.json")
Q_THRESHOLD = 0.5          # decisions/10: convention, not derivation. See experiments/14.


def contingency(correct_a, correct_b):
    """N11 both right, N00 both wrong, N10/N01 one right."""
    a, b = np.asarray(correct_a, bool), np.asarray(correct_b, bool)
    return (int((a & b).sum()), int((a & ~b).sum()),
            int((~a & b).sum()), int((~a & ~b).sum()))


def double_fault(correct_a, correct_b):
    n11, n10, n01, n00 = contingency(correct_a, correct_b)
    total = n11 + n10 + n01 + n00
    return n00 / total if total else None


def q_statistic(correct_a, correct_b):
    n11, n10, n01, n00 = contingency(correct_a, correct_b)
    num, den = n11 * n00 - n01 * n10, n11 * n00 + n01 * n10
    return num / den if den else None


def derive_groups(pairs, threshold=Q_THRESHOLD):
    """Union observers whose Q exceeds the threshold. Transitive by construction."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), m in pairs.items():
        parent.setdefault(a, a)
        parent.setdefault(b, b)
        if m["q"] is not None and m["q"] > threshold:
            parent[find(a)] = find(b)
    groups = {}
    for obs in parent:
        groups.setdefault(find(obs), []).append(obs)
    return {f"derived-{i}": sorted(v) for i, v in enumerate(sorted(groups.values()))}


def main():
    d = json.loads(INPUTS.read_text())
    y = np.array(d["labels"])
    probs = {"tabular": d["p_tab"], "sequence": d["p_seq"], "lookup": d["p_look"]}

    pairs = {}
    for a, b in combinations(sorted(probs), 2):
        both = [i for i in range(len(y))
                if probs[a][i] is not None and probs[b][i] is not None]
        ca = [(probs[a][i] >= 0.5) == bool(y[i]) for i in both]
        cb = [(probs[b][i] >= 0.5) == bool(y[i]) for i in both]
        n11, n10, n01, n00 = contingency(ca, cb)
        pairs[(a, b)] = {"n": len(both), "n11": n11, "n10": n10, "n01": n01, "n00": n00,
                         "double_fault": double_fault(ca, cb), "q": q_statistic(ca, cb),
                         "acc_a": float(np.mean(ca)), "acc_b": float(np.mean(cb))}

    print(f"{'pair':<22} {'n':>4} {'acc A':>7} {'acc B':>7} {'double-fault':>13} {'Q':>8}  coupled?")
    for (a, b), m in pairs.items():
        q = m["q"]
        mark = "YES" if q is not None and q > Q_THRESHOLD else "no"
        print(f"  {a + '/' + b:<20} {m['n']:>4} {m['acc_a']:>7.4f} {m['acc_b']:>7.4f} "
              f"{m['double_fault']:>13.4f} {q:>8.4f}  {mark}")

    derived = derive_groups(pairs)
    hand = {"ssl-jvm": ["lookup", "tabular"], "run-history": ["sequence"]}
    hand_sets = sorted(sorted(v) for v in hand.values())
    derived_sets = sorted(sorted(v) for v in derived.values())
    agree = hand_sets == derived_sets

    print(f"\n  hand-assigned : {hand_sets}")
    print(f"  derived (Q>{Q_THRESHOLD}): {derived_sets}")
    print(f"  {'AGREE -- the hand-assignment was correct' if agree else 'DISAGREE -- a recorded conclusion changes'}")

    OUT.write_text(json.dumps(
        {"threshold_q": Q_THRESHOLD, "frozen_cases": len(y),
         "pairs": {f"{a}|{b}": m for (a, b), m in pairs.items()},
         "hand_assigned": hand_sets, "derived": derived_sets, "agree": agree}, indent=2) + "\n")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()
