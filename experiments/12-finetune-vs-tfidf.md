# Experiment 12 — does the fine-tune beat the boring baseline?

**Written 2026-09-23, before the gate was run and before `precomputed/slm-eval.json` was
unsealed.** Appended to after, never edited.

## 1. The claim being tested

That fine-tuning an SLM on these explanations produces a classifier **meaningfully better
than a cheap lexical baseline on this corpus**.

I expect this claim to be false, and it is stated as the thing I am trying to **falsify by
finding a baseline that already matches it** — not the thing I am hoping to confirm.

## 2. The baseline — the cheapest thing that could work

**TF-IDF character n-grams into a linear classifier, on the failure message.**

This baseline is almost insultingly strong here, and the structure is what makes that
non-obvious until you see it: the corpus has **19 distinct messages across 202 tests**. The
label is very nearly a function of the message string. That is not a hard classification
problem — it is a lookup with a thin lexical smear on top, which is exactly why phase 09's
TF-IDF + 5-NN already reached **0.9851** and the exact-message lookup reached **0.9940**.

The baseline is not a strawman to be beaten. **It is the ceiling, and two free methods have
already reached it.**

## 3. The number that would make me keep going (provision a GPU)

The fine-tuned SLM must beat the TF-IDF baseline by a margin that **clears fold noise** on
the frozen split: mean gain over baseline exceeding the standard error of the paired
per-fold differences — the same noise-adjusted rule used since the sequence observer in
phase 08. It must clear it on the metric that survives the base-rate problem, not on this
slice's flattering numbers.

Given the baseline sits at 0.985–0.994, this is **real but nearly unreachable by
construction**: there is under 1.5 points of headroom above TF-IDF and under 0.6 above the
lookup. You cannot beat 0.994 by a noise-clearing margin when the ceiling is 1.0.

## 4. The number that would make me stop

> **If baseline accuracy ≥ ~0.98 and its gap to the exact-message lookup is inside fold
> noise, the gate fires: no fine-tune, recorded as a complete decision.**

If the cheap lexical method already captures essentially all the signal the message string
carries, fine-tuning is refuted before it runs, because there is no headroom for a GPU to
buy.

### Why I expect the stop — stated so it is falsifiable

19 distinct messages means this classification task is almost entirely **memorisation of a
tiny message vocabulary**. A fine-tuned SLM's advantage over TF-IDF is supposed to be
*generalisation to unseen phrasings* — but with 19 messages and an exact lookup already at
0.994, there are almost no unseen phrasings to generalise to. The SLM would be learning the
same 19-way lookup, more expensively, with more capacity to overfit.

**This is not "the GPU is too costly."** The memory ledger showed 1.92 GiB fits a free T4,
and the distillation pricing came in at **~$8 for all 202 cases** with Opus 5. Nothing here
is gated by budget. The gate fires on **evidence** — the harder place to stop, because the
honest reason is not *we cannot afford it* but *we measured that it would not help*.

## The committed prediction, dated 2026-09-23

**The gate fires.** TF-IDF baseline lands ~0.98, within noise of the 0.994 lookup, the SLM
has no headroom to clear, no GPU is provisioned, and this is recorded as a **complete
no-fine-tune outcome**.

**Falsifier:** if the baseline comes in **below ~0.97**, I am wrong about the headroom, and
`precomputed/slm-eval.json` gets unsealed to see whether the SLM reaches into that gap.

## Scope that must ride with the stop decision

This conclusion is scoped to **this data**: one project's failure text, 19 distinct
messages, 202 cases.

**"No fine-tune" here means "no fine-tune is justified by the evidence on this corpus" — not
"SLM distillation never helps for CI explanation."** A corpus with hundreds of distinct,
novel-phrased messages could flip it, because then generalisation over lexical variety is a
real task and TF-IDF's ceiling would sit lower. Stated so the stop is defensible and does
not inflate into a universal claim it cannot support.

## Provenance note

An earlier turn referred to this gate prediction as "still standing from last turn." No such
prediction sits in the earlier record. It is dated **now**, not backdated — inventing
provenance for a prediction would be a small version of exactly the confidence-laundering
this phase exists to prevent.

---

## Result

*(appended after the run — empty at the time of writing)*

**Appended 2026-09-23 after the run. Nothing above this line was edited.**

## The gate fired

Frozen split: `GroupKFold(n_splits=5)` grouped by test class. 202 cases, 19 distinct
messages, 10 classes, base rate 0.4950.

| method | mean | std | per-fold |
|---|---|---|---|
| majority baseline | **0.2474** | 0.1441 | 0.344, 0.231, 0.000, 0.233, 0.429 |
| **TF-IDF char-ngram + linear** | **0.9825** | 0.0300 | 0.989, 0.923, 1.000, 1.000, 1.000 |
| exact-message lookup | **0.9975** | 0.0050 | 0.988, 1.000, 1.000, 1.000, 1.000 |

**Stop-criterion, both conditions met:**

```
baseline accuracy 0.9825  >=  0.98                    YES
paired gap (TF-IDF - lookup)  mean -0.0150  SE 0.0155
|gap| <= SE  ->  inside fold noise                    YES

headroom above TF-IDF to the 1.0 ceiling:  0.0175
```

**Prediction confirmed on both numbers.** Predicted "TF-IDF lands ~0.98, within noise of the
lookup" — measured 0.9825, gap −0.0150 against SE 0.0155.

**No GPU provisioned. No fine-tune. Recorded as a complete decision.**

## The unpredicted result: the majority baseline is worse than chance

**0.2474, not ~0.50.** Under `GroupKFold` by test class the held-out class is homogeneous —
every `HttpOverSpdy3Test.*` is deterministic — so the training majority systematically
mispredicts the *entire* held-out fold. One fold scores **0.000**.

This is a grouped-splitting artifact on a 10-class vocabulary, and it cuts both ways: read
alone, "baseline 0.247" suggests a hard task when the opposite is true, while "base rate
0.495" understates how structured the corpus is. Both are recorded in
`artifacts/results/distill-corpus.json`.

## Why the gate fired on evidence rather than cost

Neither cost line binds:

- **compute:** the memory ledger redrew a 37.47 GiB full fine-tune down to **1.92 GiB** with
  4-bit quantisation, LoRA and gradient checkpointing — a free Kaggle T4 has eight times
  that headroom;
- **data:** one real rendered prompt at 677 input tokens prices all 202 cases at **~$8.26**
  with Opus 5 at modest thinking.

So the phase-05 expectation — *"the real cost is the distillation API calls, not the GPU"* —
is **overturned. On this corpus it is neither.** The honest reason to stop is not *we could
not afford it* but *we measured that it would not help*, which is the harder thing to write
down and the whole point of the gate.

## `precomputed/slm-eval.json` stays sealed

The falsifier — baseline below ~0.97 — did not fire, so by the pre-registered rule the file
is not opened. The gate fired on this project's own evidence, and reading the reference
numbers after a decision is recorded could only tempt a retrofit. No number from it appears
anywhere in this phase, and nothing of this project's was substituted from it.

## Scope, restated so the stop does not inflate

**"No fine-tune" means no fine-tune is justified by the evidence on this corpus** — one
project's failure text, 19 distinct messages, 202 cases. It does **not** mean SLM
distillation never helps for CI explanation. A corpus with hundreds of distinct,
novel-phrased messages could flip it, because then generalisation over lexical variety is a
real task and TF-IDF's ceiling would sit lower.
