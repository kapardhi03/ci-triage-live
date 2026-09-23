# Experiment 08 — does the sequence model beat a `sum()`?

**Written 2026-09-23, before any sequence model exists.** The control below was run first,
on purpose. Appended to after the model runs, never edited.

## The circularity, found before any code

`IsFlaky` is defined — and was verified empirically in phase 04 — as:

```
IsFlaky = (NumFailingRuns > 0) AND (NumPassingRuns > 0)
```

So a model handed a test's **full** run sequence and asked to predict `IsFlaky` is being
handed its own answer key. The label is a deterministic function of the input: *does this
sequence contain both a 0 and a 1?* A regex answers it. The AUC would be 1.0 by
construction, and an engineer would learn nothing, because the model has computed a
property of the input rather than predicted anything about the world.

**A reformulation that does not escape it.** The first attempt was to predict whether a
sequence is *interleaved* (`P P F P F P` — genuine non-determinism) or *blocked*
(`F F F F P P P P` — broken, then fixed). That distinction is real and important: both
satisfy `IsFlaky`, but only the first is flakiness, so **the label conflates two phenomena**.
As a learning task, though, it has the identical defect — "is this sequence interleaved" is
also a deterministic function of the sequence being fed in. Different function, same AUC 1.0.

The conflation finding is recorded as a property of the label; it is not the task.

## The formulation

**Prefix predicts suffix.** Features are the first `k` TRUSTED run outcomes for a test;
the label is whether the **remaining** runs contain both a pass and a fail. Features and
label share no run.

`k ∈ {200, 2000}`. The short prefix is the one that matters operationally: at 02:47 a test
may have 50 runs of history, not 2,000. A model that needs 2,000 prior runs is solving a
problem the engineer does not have.

**The question it answers for an engineer:** *given the history I already have for this
test, will it flip on me going forward?* Actionable — it decides whether to quarantine the
test now or leave it in the gate.

## Dataset decision

Tests that **never** fail are included. At 02:47 the observer does not get to pre-filter to
"tests that have historically failed"; it is handed a test. Excluding the never-failers
would be conditioning on the answer — a cousin of the phase 04 leak. It costs realism in
the other direction: 878 all-zero examples are trivially separable and will inflate every
AUC reported here. Both effects are stated rather than chosen away from.

Only slice 05 `TRUSTED` runs contribute an outcome, to either half.

## The control, run before the model existed

**Count the test's failures in the prefix.** No training, no parameters, one `sum()`.

| project | prefix | N | positives | rate | **control AUC** |
|---|---|---|---|---|---|
| `kevinsawicki-http-request` | 200 | 163 | 15 | 9.2% | **1.0000** |
| `kevinsawicki-http-request` | 2000 | 163 | 15 | 9.2% | **1.0000** |
| `square-okhttp` | 200 | 810 | 100 | 12.3% | **0.4967** |
| `square-okhttp` | 2000 | 810 | 20 | 2.5% | 0.7897 |
| `tootallnate-java-websocket` | 200 | 145 | 23 | 15.9% | 0.8478 |
| `tootallnate-java-websocket` | 2000 | 145 | 21 | 14.5% | **0.9992** |

Mean **0.9296** at prefix 2000, **0.7815** at prefix 200.

The control is at or near ceiling on two of three projects, and at **exactly chance**
(0.4967) on `square-okhttp` at prefix 200.

## Keep / throw away

The first criterion proposed was *"beat the control by 0.05 in every cell."* **Withdrawn as
unsatisfiable**: three of six cells have less headroom than the margin — kevinsawicki has
0.0000 at both prefix lengths and tootallnate/2000 has 0.0008. Run as stated it would drop
the model by arithmetic rather than by evidence, which is a predetermined outcome wearing
the costume of a test. The same structural flaw as the circular tests found in phases 04 and
07, relocated to the criterion.

**The criterion, decided before the model exists:**

> **Judge on `square-okhttp` at prefix 200 alone** — the only cell where the control is dead
> (0.4967, chance). **Keep the sequence model if its AUC there is ≥ 0.5467** (the control
> plus 0.05). **Throw it away otherwise.**
>
> The five saturated or near-saturated cells are excluded as uninformative, and that
> exclusion is declared here rather than discovered afterwards. They will still be reported.

This can fire against the model. There is no reading of "≥ 0.5467 on okhttp/200" that a
disappointing result can be argued into.

## Also required before the result is read

Raw AUC, calibrated AUC, **and the count of distinct calibrated probabilities**, per fold.
A calibrated AUC of exactly 0.5 means either a model ranking at chance or a model that has
collapsed to one constant output, and AUC alone cannot distinguish them.

## Scope

3 projects, not 25. A project-grouped split gives 3 folds. Not comparable to
`precomputed/sequence-eval.json` (17 projects) or to any phase 06/07 number.

---

## Result

*(appended after the run — empty at the time of writing)*
