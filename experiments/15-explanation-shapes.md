# Experiment 15 — are the explanations unimpressive?

**Written 2026-09-29, before anything was run.** Closes the last open item from `knowns/12`:
the explanation layer is implemented and never evaluated.

## Why correctness cannot be the measure

`design/12` forbids the explainer from asserting the verdict — it states the basis, never
the belief. **Nothing in an explanation can be right or wrong**, by construction. That is
the design's central protection: an account that only reports what was observed stays true
even when the verdict underneath it is false.

So the evaluation has to test something else, and the design already committed to a claim:

> *"Most of this system's explanations will be unimpressive, and that is correct. 'A
> dictionary matched a known error string' is exactly what happened. An explanation layer
> doing its job makes the system sound as modest as it actually is.*
>
> *If the explanations start sounding smart, that is the alarm. It means the model has begun
> generating reasoning the observers never did."*

Recorded in `design/12` before any model ran. This tests it.

## The measure

**Distinct explanation shapes across the frozen 202 cases.**

A *shape* is the structure of the account, ignoring specific probabilities: which observer
is the basis, whether it is calibrated, who corroborated, who contradicted, how many voices
survived, who was suppressed, who was inert, and the evidence level. Two cases with the same
shape are telling the engineer the same story about different numbers.

## The threshold

> **Under 10 distinct shapes = unimpressive. The prediction holds.**
>
> **10 or more = the explanations are varied, and the alarm in `design/12` should be
> examined rather than dismissed.**

Recorded as a chosen number. For calibration: 19 distinct failure messages, 3 observers,
3 evidence levels — the combinatorial ceiling is low by construction, so a result near 200
would be surprising and near 5 would be the strong form of the prediction.

## What each outcome means, fixed in advance

| shapes | verdict |
|---|---|
| **< 10** | **Prediction holds.** The explanations are as modest as the system, which is the design working. |
| 10–30 | Varied but bounded. Worth reading a sample to check whether the variety is real structure or noise in the probabilities. |
| > 30 | **The alarm condition.** Either the system has more structure than the rest of this repository suggests, or the shape definition is too fine-grained and is counting numbers as narrative. |

## What it will not prove

- **Not that the explanations are useful.** Shape count measures variety, not usefulness.
  Whether any of this helps an engineer at 02:47 needs engineers, and there are none here.
- **Not that the alarm could fire.** This explainer is template-bound and cannot generate
  free text, so "sounding smart" is structurally impossible for it. The alarm was written
  for a *model-backed* explainer, which `design/12` specified and phase 12 gated out. A low
  shape count is therefore weak evidence — the design forbids the failure it is checking for.

That second limitation is the important one and is stated before the result rather than
discovered after it.

---

## Result

*(appended after the run — empty at the time of writing)*

**Appended 2026-09-29 after the run. Nothing above this line was edited.**

## The result: 8 shapes from 202 cases — the prediction holds

Threshold was **< 10**. Measured **8**. Two shapes cover **78%** of cases.

| n | basis | voices | suppressed | thin | split |
|---|---|---|---|---|---|
| 95 | `lookup` | 2 | `tabular` | false | false |
| 63 | `sequence` | 2 | `tabular` | false | false |
| 26 | `sequence` | 2 | — | **true** | **true** |
| 8 | `tabular` | 2 | — | **true** | **true** |
| 5 | `sequence` | 2 | `lookup` | false | false |
| 3 | `lookup` | 2 | `tabular` | false | false |
| 1+1 | `sequence` | 2 | — | **true** | false |

`design/12` predicted this before any model ran:

> *"Most of this system's explanations will be unimpressive, and that is correct. 'A
> dictionary matched a known error string' is exactly what happened."*

**It is.** 202 cases produce eight accounts, `voices` is **2 in every single case**, and
`tabular` is suppressed in **166 of 202** — which is phase 11's finding appearing in the
explanation layer rather than the fusion table.

## The finding that outranks the shape count

**`THIN` was unreachable.** The first implementation keyed `evidence_level` on surviving
voices, and `tabular` and `sequence` always carry probabilities in different `cause_group`s,
so the count was never below 2. The branch `design/12` called load-bearing —

> *"It refuses to hide thin evidence... an uncovered case must say 'no observer had a
> confident signal'. A system that explains its confident hits and its coin-flips in the
> same fluent register is the dangerous one."*

— **never executed on real evidence.** The 36 cases where the lookup has no entry at all were
narrated as `SPLIT`, and two of them as `CONFIDENT`.

### The fix created the same defect elsewhere

Making `THIN` fire on `NO_EVIDENCE` as well:

```
before:  CONFIDENT 168 | SPLIT 34 | THIN  0     <- THIN unreachable
after:   CONFIDENT 166 | SPLIT  0 | THIN 36     <- SPLIT unreachable
```

**34 cases are both** — an observer is silent *and* the survivors disagree sharply. Reporting
only `THIN` discards the disagreement, which is the other refusal `design/12` states:

> *"It refuses to smooth disagreement. Where observers split, the split is shown, not
> resolved into a unanimous-sounding story."*

### The root cause was the type, not the ordering

Thinness and disagreement are **independent properties**. A case can be neither, either, or
both. A single enum forces whichever branch is checked first to shadow the other, so every
ordering silently disables one of the two refusals.

Replaced with two booleans. `design/12` amended, and
`tests/test_invariants.py::test_12_thin_and_split_are_independent_fields` asserts the
both-at-once case that an enum cannot represent.

| implementation | shapes | unreachable |
|---|---|---|
| enum, keyed on voices | 8 | **`THIN`** |
| enum, `THIN` checked first | 7 | **`SPLIT`** |
| **two booleans** | **8** | **none** |

## Why this counts as the seventh instance

Five checks in this repository were green while being wrong. This is the sixth — a branch
that could not execute — and the fix was the seventh, introduced by me while repairing the
sixth, and caught only because the shape count was re-run rather than assumed.

## What the result does not prove

**The measure is weak, and this was stated before the run.** A template-bound explainer
cannot generate free text, so "sounding smart" is structurally impossible for it. The alarm
in `design/12` was written for a *model-backed* explainer, which phase 12 gated out. A low
shape count confirms the prediction about *this* explainer while the failure mode it guards
against was never reachable.

**Nothing here says the explanations are useful.** Shape count measures variety. Whether any
of it helps an engineer at 02:47 needs engineers, and there are none in this project.
