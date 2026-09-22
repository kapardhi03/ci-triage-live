# Slice 03 — ground-truth source

## Responsibility
Serve a label together with the provenance needed to discount it.

## Reads
The label column as published, and the metadata describing how it was produced: the
procedure, the rerun count N, the commit the reruns ran against, and the date.

## Emits
A label record, never a bare value:

```
{
  label:            flaky | not_flaky
  basis:            observed_flip | no_flip_observed
  reruns:           N          (null if unrecorded)
  detectable_floor: ~1/N       (null if N unrecorded)
  commit:           the SHA the reruns ran against
  observed_on:      date
  trust:            proof | bound
}
```

`basis` and `trust` are the fields that matter. `observed_flip` is a proof — identical code
produced two outcomes and someone witnessed it. `no_flip_observed` is a bound — a search
that ran out of budget. A consumer that cannot see the difference will treat the second as
the first, which is the failure this slice exists to prevent.

## Refuses
It refuses to emit `trust: proof` for any label whose basis is `no_flip_observed`,
at any N. No rerun count converts absence of evidence into evidence.

Where N is unrecorded it emits the label with `reruns: null` and
`detectable_floor: null` rather than substituting a default. A missing sample size is
reported as missing, never as a guess.

## Constraint
A negative label may never be emitted as `trust: proof`. Equivalently: nothing downstream
may consume a label without also consuming its basis. A label with no recorded sample size
is a number with no error bar, and must arrive visibly missing rather than silently
complete.

## Connects to
Consumed by slice 04 (ingestion, which builds the feature matrix) and by slice 02
(evaluation — precision computed against `no_flip_observed` negatives is a bound, not a
point value). Depends on nothing earlier; this is where the data enters the system.
Refreshed by the targeted-rerun procedure recorded in experiments/03-rerun-bias.md.
