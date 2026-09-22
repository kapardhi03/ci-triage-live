# Experiment 07 (pre-registered) — is ExecutionTime partially label-derived?

**Written 2026-09-22, during phase 04, before any model exists.** Pre-registered here rather
than raised when phase 07 gets a disappointing number, so that it cannot be invented after
the fact to explain a result.

This is not phase 07's required experiment (`experiments/07-calibration-tradeoff.md`). It is
the one live question phase 04 knowingly deferred.

## Why it is open

The phase 04 leak scan flagged four columns above AUC 0.95 and they were excluded. The
strongest **surviving** feature is `ExecutionTime` at **AUC 0.7607** — the next best is
`hIndex...window100` at 0.6533. It sits alone, well clear of the pack, comfortably under the
0.95 guard but far above every other legitimate feature.

That gap is the reason for the doubt. A flaky test is often flaky *because* of a timeout, a
race, or a retry, and all three make a run take longer. If `ExecutionTime` was measured on
runs that include failures, then part of its signal is the outcome leaking backwards into
the feature — not perfectly, which is exactly why the AUC guard cannot see it.

A partial leak is more dangerous than a total one. A total leak announces itself at AUC
1.000 and gets caught. A partial leak inflates every downstream number by an unknown amount
and survives every test currently in the repo.

## The claim

**`ExecutionTime` carries outcome information, not only test-intrinsic cost. Some part of
its 0.76 comes from failing runs taking longer, and that part will not be available at
02:47 on a test that has not been run yet.**

## What would support it

- `ExecutionTime` is documented or observably derived from runs that include failures.
- Dropping it costs materially less held-out AUC than its standalone 0.76 implies — a
  hallmark of signal that duplicates the label rather than predicting it.
- Its advantage shrinks disproportionately under the grouped-by-project split in phase 06,
  relative to the other features.

## What would abandon it

- `ExecutionTime` is documented as measured on passing runs only, or on a separate profiling
  pass. The concern is then closed outright.
- It holds its contribution under the grouped split in step with the other features.
- Its distribution does not differ between flaky and non-flaky tests once project is
  controlled for — i.e. the 0.76 is a project effect, which is a different problem needing a
  different fix.

## What must not happen

This question must not be settled by whether the phase 07 model performs well. A leaking
feature makes a model look better, so "the number was good" is evidence for the claim, not
against it.

## Deferred consequence

If supported, `ExecutionTime` joins the exclusion list in `ci_triage/data.py` with reason
code `label_derived`, `artifacts/results/eda.json` is regenerated, and every result produced
before that point is restated. Recording that cost now, while it is cheap to accept.
