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

---

## Result (appended 2026-09-23; nothing above was edited)

| | LOPO AUC |
|---|---|
| with `ExecutionTime` (13 features) | **0.6765** ±0.163 |
| without `ExecutionTime` (12 features) | **0.5577** ±0.130 |
| cost of dropping it | **0.1188** |

**Inconclusive, leaning against the claim — and it surfaced something larger.**

The support condition was that dropping it would cost *materially less* held-out AUC than
its standalone 0.7607 implies, which is what signal duplicating the label looks like. The
opposite happened: it holds its contribution under the grouped split, and removing it
collapses the model to 0.5577 — barely above chance. That matches the second **abandon**
condition ("it holds its contribution under the grouped split in step with the other
features"), except it does not hold in step with them, it carries nearly all of it.

**Why this is not a clean refutation.** A leak present in both training and test folds
transfers perfectly well; the test data is contaminated too. So this measurement cannot
separate "real transferable signal" from "a leak that is uniformly present." The decisive
evidence remains the one thing the dataset does not ship: whether `ExecutionTime` was
measured on runs that include failures. Still open.

**The larger finding.** The tabular observer is effectively a single feature. Twelve of the
thirteen columns together score 0.5577. Whatever phases 08–11 build has to carry information
`ExecutionTime` does not already contain, and the independence question slice 10 asks is
sharper than expected: three observers are only three observers if they do not all reduce
to the same column.

Also confirmed as designed: `ExecutionTime` drives **39.4%** of the alien-project distance
metric — three times the next feature. The coupling recorded in `design/07` before
measurement holds. If it does leak, the observer and its own safeguard fail together.
