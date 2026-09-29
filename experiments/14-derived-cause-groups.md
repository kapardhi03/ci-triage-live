# Experiment 14 — derive `cause_group` instead of assigning it

**Written 2026-09-29, before anything was computed.** Closes the #2 open item in
`KNOWNS.md`.

## The deficiency being fixed

`.ci-lab/interviews/10.md` conceded it unprompted:

> *"`cause_group` is a hand-assigned string. You measured one correlation, decided observers
> 1 and 3 share a cause, and typed the same label onto both. The contract does not *detect*
> correlated evidence — it enforces a grouping a human guessed."*

And `docs/prior-work.md`, from the doubt-first search, named the remedy: the **double-fault
measure** and the **Q statistic** are the standard instruments for exactly this, computable
from outputs already stored. They were not applied. This applies them.

**No coupling involving observer 2 has ever been computed at all.** If the sequence observer
shares a cause with either of the others, the contract currently counts them twice and
nothing would reveal it.

## What is computed

Both measures, all three pairs, on the same frozen 202 cases (`305d8ece8a0fa240`):

- **Double-fault** — the fraction of cases where *both* observers are wrong. Kuncheva's
  motivation is precisely this case: *"it is more important to detect when simultaneous
  errors are being committed than when both classifiers are correct."*
- **Q statistic** — `(N11·N00 − N01·N10) / (N11·N00 + N01·N10)`. Q ≈ 0 independent,
  Q → 1 strongly correlated. Normalises for how often each observer is right, which raw
  double-fault does not.

The lookup abstains on 36 of 202, so each pair is computed on its own overlap and the `n`
for each pair is reported rather than averaged away.

## The threshold

> **Q > 0.5 means the same `cause_group`.**

A convention rather than a derivation, and recorded as one. Substantial positive dependence
is the usual reading of Q > 0.5; Q > 0.8 is strong. The 40:3 cost asymmetry argues for
catching coupling early rather than late, so the lower of the two conventional bars is taken.

## The prediction

1. **`tabular` / `lookup` is the most-coupled pair.** This is the hand-assigned grouping and
   the only one with a prior measurement behind it — `ExecutionTime` predicts the lookup's
   input at AUC 0.6987, p = 1.06e-06.
2. **`sequence` is independent of both.** Q below 0.5 against `tabular` and against
   `lookup`.

If both hold, the hand-assignment was correct and phase 11's two-voice fusion stands.

## What would refute it

| outcome | consequence |
|---|---|
| `sequence` couples to either observer at Q > 0.5 | **phase 11 ran over the wrong number of voices.** Its fusion result needs revisiting, and the contract has been double-counting. |
| `tabular`/`lookup` falls below Q 0.5 | The hand-assigned grouping was wrong in the other direction — the contract has been *over*-collapsing, suppressing a genuine second voice. |
| all three pairs above 0.5 | Every observer shares a cause; the architecture's independence claim collapses entirely. |
| all three below 0.5 | No grouping is justified, `collapse_correlated` is a no-op, and phase 10's central finding was an artifact of a single AUC measurement. |

Any of these changes a recorded conclusion, which is what makes the experiment worth running
rather than a confirmation.

## Scope

202 cases, one project, 49.5% base rate. Q and double-fault are computed on hard predictions
at a 0.5 threshold, so they inherit that threshold's arbitrariness. A pair can be coupled in
belief while disagreeing in label, and these measures would not see it.

---

## Result

*(appended after the run — empty at the time of writing)*
