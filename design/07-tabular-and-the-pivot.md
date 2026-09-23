# Slice 07 — observer 1, tabular

## Responsibility
Emit a calibrated probability that this failure is flaky, together with an independent
qualifier saying how much the probability deserves to be believed.

## Reads
The 13 features surviving slice 04's exclusion policy, for the failing test, plus the
training fold defined by slice 06. Nothing else — not the label, not the raw archives, and
not any other observer's output. Slice 10 depends on observers not reading one another.

## Emits

```
{
  probability:  calibrated P(flaky), or null when abstaining
  qualifier:    [0,1] -- how far this project sits from the training distribution
  verdict:      FLAKY_SCORE | ABSTAIN
  evidence:     { raw_score, distance, distance_percentile, n_train_projects,
                  calibration_method, dominant_distance_features }
}
```

`qualifier` is **not** the model's confidence, and that distinction is the design.

A model on an unseen project does not know it is on an unseen project. It will output 0.92
for a test from a codebase it has never encountered, and it is most confident precisely
where it is least entitled to be. Gating abstention on the model's own probability would
abstain on the cases it is unsure about and wave through the cases it is wrong about —
circular, and backwards. The qualifier must therefore be computed from something outside
the model's output.

## Refuses
It emits `ABSTAIN` — probability `null` — when the qualifier falls below threshold: when
this project's feature distribution is far enough from every training project that the
model is extrapolating rather than predicting.

ABSTAIN is derived here, not declared, the same way it was derived in slice 01 and `UNKNOWN`
was in slice 05. It is not a rule that says "abstain on unseen projects" — every project is
unseen in deployment. It is the qualifier failing.

Phase 01's table is the argument: a wrong "flaky" costs ~40h because a defect ships, a wrong
"real defect" ~3h, an abstain ~1.5h. An observer that confidently extrapolates onto an alien
project is buying a 40h risk to avoid a 1.5h cost.

It also refuses to report a probability without its qualifier. A consumer that can read the
number without the caveat will read the number without the caveat.

## Constraint
**The model is never fitted on data that includes the held-out projects.** Invisible in the
metrics — the number simply goes up — and fatal to every claim built on it. Enforced by
`tests/test_tabular.py`, not by inspection.

**Second constraint: the qualifier may not be a function of the model's output.** A test
must fail if `qualifier` becomes derivable from `probability`, because that collapses the
design back into self-reported confidence.

## The coupling, stated before it is measured

Distance is computed on standardised features, since the 13 sit on wildly different scales
once the project-scale columns are gone. Even standardised, **`ExecutionTime` is expected to
dominate the distance metric** — it was the strongest surviving single feature at AUC 0.760,
and after slice 06 removed the project-scale columns it is more dominant, not less.

`ExecutionTime` is also the pre-registered leak suspect from
`experiments/07-execution-time-leak.md`, written during phase 04: a flaky test often runs
longer *because* it timed out or retried, so part of its signal may be the outcome leaking
backwards into the feature.

**If it leaks, it contaminates the model and the alien-project detector in the same
direction.** The observer would be confidently wrong, and the qualifier — the thing built to
catch confident wrongness — would be wrong in step with it, reporting the project as
familiar on the strength of the same contaminated column. A shared cause that disables its
own safeguard is the failure mode hardest to see from inside, and slice 10 exists because of
exactly this shape.

Recorded now so the measurement can contradict it. `dominant_distance_features` is emitted
so the coupling is observable per call rather than assumed.

## Connects to
Depends on slice 04 (features), slice 06 (split and harness), slice 02 (all metrics; it
computes none of its own). Consumed by slice 11 (fusion — which needs the qualifier to
discount this observer) and constrained by slice 10 (independence — this observer must not
read another's output, and its qualifier must not share a cause with its probability).
