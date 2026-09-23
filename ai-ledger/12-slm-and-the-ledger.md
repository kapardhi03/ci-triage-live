# AI ledger — phase 12

## Rejected proposal

**Proposal:** Compute is free (1.92 GiB fits a Kaggle T4) and the corpus is ~$8. Nothing is
gated by budget, so run the fine-tune — it costs almost nothing and the result is a real
datapoint rather than an argument.

**Verdict:** Rejected.

**Reason:** "It's cheap" is not a reason to run an experiment whose outcome is already
determined. The TF-IDF baseline reached **0.9825** and the exact-message lookup **0.9975**,
with the paired gap (−0.0150) **inside fold noise** (SE 0.0155) and **0.0175** of headroom
to the ceiling. The keep-criterion required a noise-clearing gain over the baseline, and
there is no room for one.

The deeper reason is structural: **19 distinct messages across 202 tests.** An SLM's
advantage over TF-IDF is generalisation to unseen phrasings, and there are almost none here
— it would learn the same 19-way lookup, more expensively, with more capacity to overfit.

Running it anyway would have produced a number, and the number would have been evidence of
nothing. The gate exists precisely to stop at the point where affordability stops being the
question.

## Narrowed proposal

**Proposal:** Unseal `precomputed/slm-eval.json` and report the reference fine-tune beside
the baselines. It cannot change a recorded decision, and a table with an empty row looks
unfinished.

**Verdict:** Rejected — the builder's call, and the right one.

**Reason:** The pre-registered falsifier was *baseline below ~0.97*. It came in at 0.9825,
so by the rule written before the run the file stays shut. The gate fired on this project's
own evidence; reading reference numbers **after** a decision is recorded can only tempt a
retrofit, and an empty row that says "sealed, and here is why" is more informative than a
filled one from a different corpus.

Same shape as phase 11's `incomplete` row. A missing number with a stated reason is a
result; a borrowed number is not.

## What the builder got right before the run

The committed prediction — *"gate fires; TF-IDF lands ~0.98, within noise of the lookup; no
GPU"* — was **confirmed on both numbers**: 0.9825, gap −0.0150 against SE 0.0155.

More useful than the prediction: the builder named the baseline as **the ceiling rather than
a strawman**, in advance, and explained why the structure made that non-obvious. That framing
is what turned this from "run the fine-tune and see" into a gate that could fire.

## Correction the builder made, unprompted

An earlier turn described the gate prediction as "still standing from last turn." No such
prediction was in the record. The builder caught it and dated it to now rather than
backdating — *"inventing provenance for it would be a small version of exactly the
confidence-laundering phase 12 exists to prevent."*

Recorded because it is the same failure the phase's design forbids, caught in the phase's own
paperwork.

## What overturned an earlier expectation of mine

`experiments/12-gpu-path.md`, written during phase 05, stated: *"the real cost is the
distillation API calls, not the GPU. A free notebook does nothing about that."*

**Wrong on this corpus. It is neither.** Compute redraws to 1.92 GiB and the whole corpus
prices at ~$8.26. The claim was a reasonable generalisation about distillation economics and
it does not survive contact with a 202-case corpus. Left in place and corrected here rather
than edited.

## Estimated, not counted

Input tokens are **estimated at 677** from 1,895 characters at a conservative 2.8
chars/token. `messages.count_tokens` is the correct tool and requires credentials this
environment does not have. The estimate is deliberately dense so input prices are upper
bounds, and the rate table is cited from the `claude-api` skill **cached 2026-06-24** rather
than recalled. If either has drifted, the budget drifts with it. Stated rather than hidden.
