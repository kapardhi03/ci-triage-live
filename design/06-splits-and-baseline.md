# Slice 06 — experiment harness

## Responsibility
Specify a run so that someone else gets the same number, and make selecting on the test set
visible rather than forbidden.

## Reads
`(X, y, groups)` from slice 04, a named split strategy, and an estimator factory. It never
reads raw CSVs, never re-derives features, and never sees the archives. If slice 04's
exclusion policy changes, every result produced here is stale by construction.

## Emits
A `RunResult` — the unit that makes a number reproducible:

```
{
  run_id:     hash of (split name, estimator repr, feature list, label, seed, data digest)
  split:      "random_5fold" | "leave_one_project_out" | "grouped_5fold"
  folds:      [ {fold, n_train, n_test, n_pos_test, auc, ...}, ... ]
  mean, std:  across evaluable folds
  skipped:    folds that could not be scored, each with a reason
  data_digest: rows, features, positives, and the source checksums from slice 04
}
```

`skipped` is not an error channel. `jimfs` and `commons-exec` have zero positives, so AUC is
undefined on those folds, and a harness that quietly averages 23 folds while reporting 25
has produced a number nobody can reproduce. A fold that could not be scored is reported as
such, with the reason.

## Refuses
It refuses to report a mean over folds whose count it has not disclosed.

It refuses to compute AUC on a fold containing a single class, rather than substituting 0.5
or dropping the fold silently.

**It refuses to hand over the final test set casually.** The test set is reachable only
through one function, which appends `(timestamp, run_id, caller's stated reason)` to an
append-only ledger before returning anything. Nothing prevents a second call. The point is
that the twelfth call is *visible* — a reviewer reading the ledger sees how many times the
test set was consulted and what was claimed each time.

That is the answer to "what stops a future me from selecting on the test set": nothing
stops it, and a design that claims to is lying. What this design does is make the count
un-hideable, so selection has to be argued for in public rather than performed quietly.
Model choice happens on validation folds, which carry no ledger and are meant to be reused.

## Constraint
**No group may appear on both sides of any fold.** A project leaking across the boundary is
invisible in the metrics — the number goes up, nothing looks wrong — and it invalidates
every claim the number supports. Checked per fold, over every fold, by
`tests/test_splits.py`, not by inspection.

Second constraint: the same `run_id` must produce the same numbers. Anything that changes a
result must be inside the hash — split, estimator, features, label, seed, data digest — so
that two results with equal `run_id` and unequal numbers is a detectable bug rather than a
mystery.

## Connects to
Depends on slice 04 (`X`, `y`, `groups`) and slice 02 (evaluation — it computes no metric of
its own, it calls the ruler). Consumed by slices 07–09, which must each report on the split
chosen here, and by slice 11, which compares fusion strategies and needs folds that can be
lined up across observers.
