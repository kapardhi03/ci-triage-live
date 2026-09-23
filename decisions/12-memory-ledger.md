# Decision 12 — the memory ledger, and what it says to rent

Done by hand, before any hardware is considered. This arithmetic is the part that transfers:
knowing **which line each technique attacks** is the difference between choosing LoRA and
repeating that LoRA is good.

Model: 3 billion parameters, 16-bit. Assumed shape ≈ 28 layers, hidden 3072. Batch 1,
sequence 2048.

## Step 1 — the four lines

| line | size | arithmetic |
|---|---|---|
| **weights** | **5.59 GiB** | 3e9 params × 2 bytes |
| **gradients** | **5.59 GiB** | 3e9 × 2 bytes — one gradient per parameter |
| **optimiser state** | **22.35 GiB** | 3e9 × 4 bytes × 2 — Adam keeps `m` and `v`, in fp32 |
| **activations** | **3.94 GiB** | 1 × 2048 × 3072 × 28 × 2 bytes × ~12 stored tensors/layer |
| | | |
| **TOTAL** | **37.47 GiB** | |
| *(+ fp32 master weights)* | *(48.6 GiB)* | *+11.2 GiB, kept by most mixed-precision setups* |

**Optimiser state is the biggest line** — four times the weights. That is the thing worth
noticing: the intuition that "the model is 3B so it needs ~6 GB" is wrong by a factor of six
before activations are counted, and it is wrong because of the optimiser, not the model.

**What it implies:** 37.5 GiB does not fit an A100 **40GB** — there is nothing left for
fragmentation, the CUDA context, or a batch above 1. It needs an **A100 or H100 80GB**.

## Step 2 — attack a line

Each technique reduces exactly one line. That mapping is the lesson.

| technique | line attacked | before → after | factor |
|---|---|---|---|
| **4-bit quantisation** (NF4) | **weights** | 5.59 → **1.40** GiB | 4× |
| **LoRA**, frozen base, rank 16 | **gradients** | 5.59 → **0.009** GiB | 588× |
| **LoRA**, frozen base, rank 16 | **optimiser** | 22.35 → **0.038** GiB | 588× |
| **gradient checkpointing** | **activations** | 3.94 → **0.47** GiB | 8× |

Three things this makes explicit that "use QLoRA" does not:

- **Quantisation does nothing for the optimiser**, which is the largest line. Quantising a
  fully fine-tuned 3B model still needs ~32 GiB.
- **LoRA's saving is not in the weights.** The base model stays resident in full for the
  forward pass. LoRA attacks gradients and optimiser state, which is why it is worth 28 GiB
  and quantisation is worth 4.
- **Checkpointing buys memory with compute** — roughly +30% training time to recompute
  activations rather than store them. The only line with a price tag in the other currency.

### The redrawn ledger

| line | size |
|---|---|
| weights (4-bit) | 1.397 GiB |
| gradients (adapter only) | 0.009 GiB |
| optimiser (adapter only) | 0.038 GiB |
| activations (checkpointed) | 0.472 GiB |
| **TOTAL** | **1.92 GiB** |

**37.47 → 1.92 GiB. A factor of 20.**

## What to rent: nothing

1.92 GiB fits a **free Kaggle T4 (16 GiB)** with eight times the headroom, and would fit a
free Colab T4 too. The decision recorded in `experiments/12-gpu-path.md` during phase 05
stands, and now has arithmetic behind it rather than preference: Kaggle over Colab for the
published ~30 h/week quota, since a tier that may allocate no GPU at all is not a plan.

**But the ledger is not what decides this phase.** `experiments/12-gpu-path.md` recorded the
point in advance: *the real cost is the distillation API calls, not the GPU. A free notebook
does nothing about that.* The memory arithmetic says compute is free; the pricing in
`experiments/12-distillation-cost.md` is what decides whether anything runs at all, and the
pre-GPU stop gate decides whether it should.

## Step 3 — should this model decide, or explain?

**Explain. It is barred from deciding, and phase 11 is the evidence.**

Phase 11 measured what happens when arbitration is handed to a language model: **nothing was
measured**, because no client was configured — and that unranked row is itself the finding.
The system had to keep working with the most capable component simply absent, and it did,
because the LLM was never load-bearing.

The stronger argument is from what the verdicts actually are. The shipped decision comes from
a dictionary lookup with 82.2% coverage. A model permitted to *decide* would be overriding a
hash-table hit with generated text, which is the confidence-laundering `design/12` forbids. A
model permitted only to *explain* states the basis — and when the basis is "one dictionary
entry matched," it says so.
