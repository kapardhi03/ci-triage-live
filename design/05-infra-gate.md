# Slice 05 — trust gate

## Responsibility
Decide whether a single run's test outcomes may contribute evidence at all.

## Reads
One run archive, and nothing else: the `maven.log` found inside it. No CSV, no label, no
other run. The gate must not be able to consult the answer it is helping to produce.

It additionally receives, per project, a **deterministic-exclusion set** computed once from
all runs, so that tests which fail in nearly every archived run do not inflate any single
run's failure fraction.

## Emits
A verdict record per run:

```
{
  run:      the run id
  verdict:  TRUSTED | BUILD_FAILED | LOG_TRUNCATED | MASS_FAILURE | UNKNOWN
  reason:   a string quoting or counting what was actually observed
  evidence: { modules, total, failed, fraction, excluded_deterministic,
              has_build_marker, bytes }
}
```

`reason` is the point of this slice. A future engineer asking why 400 runs vanished reads
the reason, not the verdict. It must be derived from the text observed in that log —
never from the verdict it accompanies, and never phrased to imply a finding the gate did
not make.

Also emits, per project, the exclusion set itself, so later phases consume the recorded
decision instead of re-parsing 6.5 GB of archives.

## Refuses
It refuses to compute a mass-failure fraction on a truncated log. This is a feasibility
refusal, not a preference: the denominator (`total`) appears only on the Results summary
lines, which Maven emits last; tail-truncation removes them. The numerator is then partial
with no bound on how partial, because the line that would have bounded it is the line that
was cut. `failed / total` is undefined, not approximate, and any improvised denominator
makes the verdict depend on where the log happened to be cut rather than on what the run did.

It refuses to assert truncation it cannot demonstrate. The build end-marker sits at the
bottom of the log too, so it dies in the same cut. A log with no Results summary and no
end-marker is ambiguous between "the archiver truncated this" and "the process died
partway", and the reason string says so rather than picking one.

It refuses to emit `TRUSTED` for a run it could not parse. Absence of evidence of a problem
is not evidence of a sound run — the same error phase 03 found in `not flaky`.

## Constraint
**The reason must match what was found.** A verdict can be correct while its audit trail is
fabricated, and that bug passes every test which only checks verdicts. Each verdict's reason
is constructed from the counts and markers actually extracted from that log, and the test
suite asserts the correspondence, not merely the verdict.

Second constraint, from the data: **every module summary contributes to the total.**
`square-okhttp` emits 5 Results lines summing to 826 tests; reading only the last treats one
module as the whole build and divides the failure count by a denominator several times too
small, which trips `MASS_FAILURE` on healthy runs. Results lines are the ones *without*
`Time elapsed` — the lines with it are per-test-class and double-count if summed.

## Precedence
`BUILD_FAILED` → `LOG_TRUNCATED` → `MASS_FAILURE` → `TRUSTED`, with `UNKNOWN` as fallback.

Ordered by **feasibility first, cause before symptom second**. A run that never compiled
matches both `BUILD_FAILED` and `MASS_FAILURE`; `BUILD_FAILED` tells the engineer no tests
ran, while `MASS_FAILURE` would tell them many tests failed, which is false and sends them
hunting a test problem that does not exist. `LOG_TRUNCATED` outranks `MASS_FAILURE` for the
stronger reason above: on a truncated log the mass-failure check cannot be performed at all.

## Connects to
Depends on nothing earlier in code; it reads raw archives directly. Consumed by slice 06
(splits — only trusted runs may contribute), and by slices 07–09 (every observer). Its
over-counting finding — one shared fixture producing 15 correlated flaky labels — is handed
to slice 10, which exists to stop observers treating shared evidence as independent.
