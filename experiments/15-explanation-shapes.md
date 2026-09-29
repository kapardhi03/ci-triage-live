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
