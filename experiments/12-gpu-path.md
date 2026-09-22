# Phase 12 — the no-GPU path, decided in advance

**Written 2026-09-22, during phase 05.** Recorded here rather than left in chat so the
route is in the repo before the phase that needs it. Nothing below is a result.

## The gate comes before the GPU

Phase 12 TASK steps 5–6 are a **pre-GPU stop gate**, not a preamble to fine-tuning. On one
frozen split, the majority baseline and TF-IDF-plus-linear-classifier are run and recorded
**before any GPU is provisioned**. The minimum result that would justify fine-tuning is
stated first. If neither the baseline comparison nor the available class balance leaves a
defensible path to that result, the phase stops there.

**A written no-fine-tune decision is a complete phase outcome, not a skipped phase.** Step 6
says so explicitly: if the gate does not pass, record the two baselines, the gate outcome,
and why no GPU run was warranted. That is the deliverable.

This matters because the temptation runs the other way — a GPU is available, so the
fine-tune happens, and the baseline gets written up afterwards as a formality. That is the
phase 04 licence-gate failure in a different costume: a gate performed in the wrong order
is not a gate.

## If no GPU: precomputed/slm-eval.json is the sanctioned route

`precomputed/README.md` states it directly: with no GPU, `slm-eval.json` is how phase 12
gets gated. The numbers get copied into my own results file **with a note that they are not
mine** — they are the original build's LoRA fine-tune over the **full 17-project archive**,
not my three-project subset. Any number of mine placed beside one of theirs carries that
scope difference in writing.

**Sealed until my hypothesis exists.** That file was opened during phase 05 while checking
references for this document, so its contents are known to the agent and not to me. Per
`precomputed/README.md`, the hypothesis in `experiments/12-finetune-vs-tfidf.md` gets
written first — claim, baseline, the number that means continue, the number that means stop
— and only then is the file read. The agent does not quote, paraphrase, hint at, or shade a
prediction toward those numbers before that point.

## What is done by hand regardless of hardware

Neither of these needs a GPU, and between them they are most of the lesson:

- **Step 1, the memory ledger.** Weights, gradients, optimiser state, activations for a 3B
  model at 16-bit, with the arithmetic shown, then the total and which GPU it implies.
  Step 2 then attacks each line — quantisation, frozen weights with a small adapter pair,
  recomputed activations — and redraws the ledger after each.
- **Step 4b, the distillation cost estimate.** One **fully rendered real prompt** — the
  actual string with real evidence in it, not a synthetic stub — token-counted, priced at a
  rate I can cite, multiplied by corpus size, with the number that would make me stop.

Also hardware-independent and easy to skip: the labeller corpus's class balance **is** the
majority baseline, and it is not 50%. It gets worked out and written down at step 4b, before
any comparison is interpreted.

## The real cost is the API calls, not the GPU

The distillation corpus is bought from a strong model, per call, in cash. A free notebook
does nothing about that. So the order is: price it (4b), decide whether the budget permits
it, and only then consider compute. If the budget does not permit it, step 4b says to record
the priced, unrun decision in `artifacts/results/distill-corpus.json` and use an existing or
precomputed labelled corpus for the gate.

## If the gate says go: Kaggle over Colab

- **Kaggle** — roughly 30 GPU-hours/week, a published quota. Predictable.
- **Free Colab** — may allocate no GPU at all, and may reclaim one mid-run. A tier that can
  refuse service is not a plan.

Mechanics if it comes to that: keep the repo local, upload only the distillation corpus,
bring back `slm.json`, and **record the notebook and the GPU type beside the numbers** — a
result whose hardware is unrecorded cannot be compared to anything later.

## Correction carried over

An earlier estimate in conversation — that phase 12's 95 minutes "becomes several hours" on
CPU — was overstated, and is corrected here rather than left to stand.

The phase is built so that **the fine-tune is its least important part**. The ledger
arithmetic, the distillation pricing, the class-balance calculation and the stop gate are
the phase; the fine-tune is a conditional appendix that may correctly never run. An estimate
that treats GPU wall-clock as the phase's cost has misread what the phase is for.
