# Slice 08 — observer 2, sequence

## Responsibility
Predict, from a test's history of run outcomes, whether that test will flip in future runs.

## Reads
One test's ordered sequence of pass/fail outcomes over the **first k TRUSTED runs** of its
project, k ∈ {200, 2000}. Nothing else.

It does not read the 13 tabular features, any other observer's output, the `IsFlaky` label,
or any run outside the prefix.

## What it reads that observer 1 does not

Observer 1 reads 13 static per-test properties — test smells, length, assert count, covered
lines, `ExecutionTime`. It has **no access to run history at all**; the temporal dimension
is absent from its inputs entirely.

Observer 2 reads only the temporal dimension and none of the static properties. **The input
sets are disjoint — zero shared columns.** That is a stronger independence claim than slice
10 usually gets, and it is worth stating that disjoint inputs are not the same as
independent evidence: both could still be driven by one underlying cause. Slice 10 tests
that; this slice can only guarantee the inputs do not overlap.

## Emits

```
{
  probability:  calibrated P(this test flips in the suffix)
  raw_score:    the uncalibrated model output
  n_distinct:   how many distinct calibrated probabilities the fold produced
  prefix_len:   k
  evidence:     { n_failures_in_prefix, prefix_len, project }
}
```

`n_distinct` is emitted because a calibrated AUC of exactly 0.5 means two different things —
a model that ranks at chance, or a model that has collapsed to a single constant output —
and the two are indistinguishable from AUC alone.

## Refuses
It refuses to score a test whose prefix is shorter than k. A padded prefix is a fabricated
history, and this observer's entire input is history.

It refuses to emit a probability without `n_distinct`, for the reason above.

It refuses to read any run the slice 05 gate did not mark `TRUSTED`. One poisoned run in a
prefix injects noise into the features and, if it fell in the suffix, into the label — the
same run corrupting both halves at once.

## Constraint
**No run may appear in both the prefix and the suffix of the same example.**

This is the phase's circularity guard. `IsFlaky` is defined as *"both a pass and a fail were
observed"*, so a model given the whole sequence and asked to predict `IsFlaky` is being
handed its own answer key: the label is a deterministic function of the input and the AUC
is 1.0 by construction. Splitting the sequence at k makes features and label share no run.

`tests/test_sequences.py` asserts the disjointness per example, and the check is broken
deliberately once to confirm it fails.

## Connects to
Depends on slice 05 (only TRUSTED runs contribute an outcome) and on the archives directly;
it does not read slice 04's feature matrix. Consumed by slice 11 (fusion). Its independence
from observer 1 is slice 10's to test, not this slice's to assert.

## Scope limit, stated up front
Three projects have archives: `kevinsawicki-http-request`, `square-okhttp`,
`tootallnate-java-websocket`. This observer therefore lives on **3 projects, not 25**, and
a project-grouped split gives **3 folds**. Every number it produces rests on a far narrower
base than phase 07's, and must be reported that way.
