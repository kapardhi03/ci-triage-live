# Slice 02 — evaluation component

## Responsibility
Measure prediction quality by computing metrics over any (predictions, truth) pair.

## Reads
Predicted labels or probabilities from any source, and ground-truth labels. The cost
table from phase 01.

## Emits
Metric values: accuracy, ROC AUC, precision, recall, Brier score, expected calibration
error (with selectable binning), cost-weighted risk, and risk-coverage.

## Refuses
Does not produce predictions, choose thresholds, or decide what to do with its numbers.
It measures; it does not act.

## Constraint
Must produce identical measurements for identical (predictions, truth) inputs, regardless
of which source produced the predictions. Same inputs, same numbers, no special cases.

## Connects to
Depends on slice 01 (external contract — the cost table). Consumed by every later phase
that trains or evaluates a model (phases 07–13).
