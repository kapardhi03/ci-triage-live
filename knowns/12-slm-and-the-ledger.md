# Phase 12

Scope: `square-okhttp` failure text — 202 cases, **19 distinct messages**, 10 test classes,
base rate 0.4950. One project. Not comparable to `precomputed/` (17 projects).

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | a 3B model at 16-bit needs **37.47 GiB** to fully fine-tune — weights 5.59, gradients 5.59, **optimiser 22.35**, activations 3.94 | decisions/12-memory-ledger.md |
| unknown | known | **the optimiser is the largest line**, 4× the weights; "a 3B model needs ~6 GB" is wrong by 6× before activations | decisions/12-memory-ledger.md |
| unknown | known | quantisation attacks **weights only** (5.59→1.40) and does nothing for the optimiser | decisions/12-memory-ledger.md |
| unknown | known | LoRA's saving is **not in the weights** — it attacks gradients + optimiser (27.94→0.047); the base stays resident for the forward pass | decisions/12-memory-ledger.md |
| unknown | known | checkpointing attacks **activations** (3.94→0.47) and is the only line that costs compute back (~+30%) | decisions/12-memory-ledger.md |
| unknown | known | redrawn: **1.92 GiB, a 20× reduction** — fits a free Kaggle T4 eight times over | decisions/12-memory-ledger.md |
| unknown | known | one **real** rendered prompt is 1,895 chars ≈ **677 input tokens**; all 202 cases cost **~$8.26** with Opus 5 at modest thinking | experiments/12-distillation-cost.md |
| unknown | known | **neither cost line binds.** The phase-05 claim that API calls, not the GPU, are the real cost is **overturned on this corpus** | ai-ledger/12-slm-and-the-ledger.md |
| unknown | known | **TF-IDF char-ngram + linear: 0.9825 ±0.0300**; exact-message lookup **0.9975 ±0.0050** | artifacts/results/slm.json |
| unknown | known | paired gap TF-IDF − lookup is **−0.0150 against SE 0.0155 — inside fold noise**; headroom to ceiling **0.0175** | artifacts/results/slm.json |
| unknown | known | **the gate fired. No GPU provisioned, no fine-tune, recorded as a complete decision** | experiments/12-finetune-vs-tfidf.md |
| unknown | known | the reason is **evidence, not affordability**: 19 distinct messages means an SLM learns the same 19-way lookup more expensively with more room to overfit | ai-ledger/12-slm-and-the-ledger.md |
| assumed | known | **the majority baseline is 0.2474 — worse than chance**, not the 0.4950 raw base rate; grouped splitting on homogeneous test classes makes the training majority mispredict whole folds (one fold scores 0.000) | artifacts/results/distill-corpus.json |
| unknown | known | the explanation layer **states the basis, never the belief** — it reports what was observed so the account stays true even when the verdict is wrong | design/12-slm-and-the-ledger.md |
| unknown | known | `precomputed/slm-eval.json` **stayed sealed** — the falsifier did not fire, and no number from it appears anywhere in this phase | artifacts/results/slm.json |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| the gate fires | **confirmed** |
| TF-IDF lands ~0.98 | **confirmed** — 0.9825 |
| within noise of the lookup | **confirmed** — gap −0.0150, SE 0.0155 |
| no GPU provisioned | **confirmed** |
| falsifier: baseline below ~0.97 | did not fire; file stays sealed |
| (unpredicted) majority baseline ≈ 0.50 | **wrong** — 0.2474, worse than chance |

## Open

| Statement | Why it is still open |
|---|---|
| **the explanation layer was never built or measured** | `design/12` specifies it in full and nothing implements it. The gate fired on the classification task the SLM would have been distilled for; whether a template-bound explainer helps an engineer at 02:47 is untested. |
| **"no fine-tune" is scoped to this corpus** | One project, 19 messages, 202 cases. It does **not** mean SLM distillation never helps for CI explanation. Hundreds of distinct, novel-phrased messages would make generalisation a real task and lower TF-IDF's ceiling. |
| token counts are estimated, not counted | `messages.count_tokens` needs credentials this environment lacks. 2.8 ch/tok is conservative, so input prices are upper bounds — but the estimate may be wrong. |
| the rate table is cached 2026-06-24 | Cited rather than recalled, and it may have drifted. Every price moves with it. |
| the prediction that explanations will be unimpressive | `design/12` records it; nothing has generated an explanation to check it against. The stated alarm — explanations that start sounding smart — has never been watched for. |
| 19 messages may be an artifact of one machine | The dominant signature is a JVM/SSL incompatibility on the host that produced these archives. A different environment might have a far richer message vocabulary, which would change this phase's conclusion. |

## Extension (2026-09-29): the explanation layer, evaluated

| Was | Now | Statement | Evidence |
|---|---|---|---|
| **known-unknown** | **known** | **the explanation layer was evaluated.** 202 cases produce **8 distinct shapes**, threshold < 10 — `design/12`'s prediction that the explanations would be unimpressive **holds** | artifacts/results/explanations.json |
| unknown | known | two shapes cover **78%**; `voices` is **2 in every case**; `tabular` is suppressed in **166 of 202** | artifacts/results/explanations.json |
| assumed | **wrong** | **`THIN` was unreachable.** Keyed on surviving voices, which never fell below 2, so the refusal `design/12` called load-bearing never executed — and the 36 thinnest cases were narrated as `SPLIT` or `CONFIDENT` | experiments/15-explanation-shapes.md |
| unknown | known | **the fix created the same defect elsewhere**: firing `THIN` on `NO_EVIDENCE` made `SPLIT` unreachable and discarded disagreement on 34 cases, which the design also forbids | experiments/15-explanation-shapes.md |
| unknown | known | **the root cause was the type, not the ordering.** Thinness and disagreement are independent; one enum forces the first-checked branch to shadow the other. Replaced with two booleans | ci_triage/contracts.py, design/12 |
| unknown | known | **34 of 202 cases are both thin and split** — the case a single enum could not represent | artifacts/results/explanations.json |
| unknown | known | this is the **sixth and seventh** instance of a check that is green while being wrong, and the seventh was introduced while fixing the sixth | experiments/15-explanation-shapes.md |

### Still open

| Statement | Why |
|---|---|
| **the measure is weak, and was known to be before the run** | A template-bound explainer cannot generate free text, so "sounding smart" is structurally impossible for it. The alarm was written for a model-backed explainer, which phase 12 gated out. |
| usefulness is untested | Shape count measures variety. Whether any of this helps an engineer at 02:47 needs engineers. |
| no model-backed explainer exists | `design/12` specified one; phase 12's gate stopped it. The alarm it was written for has never had anything to fire against. |
