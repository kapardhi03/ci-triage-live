# Phase 11

Scope: 202 `square-okhttp` cases (`sha256[:16] = 305d8ece8a0fa240`), base rate **0.495**
against deployment's 0.0316. Not comparable to `precomputed/fusion-comparison.json`.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | **A, B and C emit identical labels on 202/202 cases** — one decision rule, three probability shapes | artifacts/results/fusion.json |
| unknown | known | A 0.9554 / B 0.9554 / C 0.9554 accuracy; ECE 0.0435 / 0.0914 / 0.0446 | artifacts/results/fusion.json |
| unknown | known | D scores 0.9940 at **82.2% coverage** — and A, B, C all score **0.9940 on those same 166 cases** | artifacts/results/fusion.json |
| unknown | known | **D's advantage is entirely which cases it declines**, and it declines exactly the 36 where the lookup has no entry | experiments/11-fusion-comparison.md |
| unknown | known | D reproduces phase 09's `MessageLookup` result exactly (0.9940 on 166) | artifacts/results/fusion.json |
| unknown | known | **the tabular observer's maximum probability over 202 cases is 0.1609** — it cannot move any decision at a 0.5 cutoff | artifacts/results/fusion.json |
| unknown | known | slice 10's collapse leaves **2 distinct voices, never 3** (166 records de-duplicated; lookup wins the collapse 161/202) | artifacts/results/fusion.json |
| unknown | known | **fusion adds nothing** — the three-observer architecture reduces to the phase 09 lookup plus an abstention rule | ai-ledger/11-fusion-and-arbiter.md |
| unknown | known | JS divergence distinguishes what total variation cannot: JS(0.45,0.55)=0.0072 vs JS(0.05,0.15)=0.0209, both TV 0.10 | decisions/11-arbiter-rules.md |
| unknown | known | two observers can share a label and diverge sharply: 0.51 and 0.99 are both "flaky" | tests/test_fusion.py::test_same_label_can_hide_a_large_divergence |
| unknown | known | false consensus is detectable and **did not occur** here: 0 cases flagged | artifacts/results/fusion.json |
| unknown | known | **E is incomplete and unranked** — no API key, no SDK; predicted position recorded and never checked | artifacts/results/fusion.json |
| unknown | known | the rendered arbiter prompt (1,320 chars) contains no label, test name, class name, project, or other strategy output | decisions/11-arbiter-rules.md |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| accuracy `C > D > A > B` | **wrong** — `D > A = B = C`, the latter three tied exactly |
| calibration `B > D > A > C` | **wrong** — `D > A > C > B`; B predicted best, came last |
| **committed claim: the rankings nearly invert** | **refuted** — no ordering to invert; D tops both, A second in both |
| refutation 3: D's advantage vanishes with coverage | **fired** — 0.9940 for everyone on the same 166 |
| refutation 4: all strategies within noise | **fired, harder** — identical on 202/202 |
| E: 2nd on accuracy, near-worst on calibration | **never checked** — incomplete by design |

All kept unedited.

## Open

| Statement | Why it is still open |
|---|---|
| **the LLM arbiter was never measured** | The central question this phase is named for is unanswered. Not a failure of the experiment — a gap in it, and one no amount of reasoning about the other four strategies fills. |
| base rate 0.495 vs deployment 0.0316 | Every number is flattered. D's abstention economics in particular invert at 3.16%, where phase 07 measured abstention as a net loser. |
| the case set is one project | 202 tests, ~19 distinct failure messages. The effective sample is far smaller than 202. |
| `divergence_threshold = 0.1` was not derived | It sets D's coverage and therefore D's entire measured advantage. Chosen, not justified. |
| is the architecture worth keeping? | Three observers were built, three were matched by free alternatives, and fusion adds nothing over one of them. Phase 13 has to answer whether this system should exist in this form. |
| no arbiter rule was tested against a live model | The forbidden list is enforced by design and by prompt audit, not by an adversarial attempt to get a model to violate it. |

## Extension (2026-09-29): the arbiter, measured

| Was | Now | Statement | Evidence |
|---|---|---|---|
| **known-unknown** | **known** | **the LLM arbiter was measured.** `gpt-4o-mini`, temp 0, 202 calls, ~$0.023 | artifacts/results/fusion.json |
| unknown | known | it posts **acc 0.9904, ECE 0.0096** — read naively, the best calibration of any completed strategy | artifacts/results/fusion.json |
| unknown | known | **it is withdrawn anyway.** Both pre-registered abandonment conditions fired | experiments/11-fusion-comparison.md |
| unknown | known | **it ties the null control exactly**: 0.9904 vs 0.9904 on the same 104 covered cases | artifacts/results/fusion.json |
| unknown | known | **the ship-direction clamp fired on 49/202 = 24.3%** against a ~5% threshold | artifacts/results/arbiter-responses.json |
| unknown | known | **44 of those 49 were genuine real defects** — unclamped, ~1,760 engineer-hours of shipped bugs on 202 cases | artifacts/results/fusion.json |
| unknown | known | its raw output distribution is `AGREE_FLAKY` 121 / `ESCALATE` 49 / `AGREE_REAL_DEFECT` 32 — **it wants to say flaky** | artifacts/results/arbiter-responses.json |
| unknown | known | **half its reported 51.5% coverage is the guard, not its judgement** — 49 chosen escalations, 49 imposed refusals | artifacts/results/fusion.json |
| unknown | known | **no metric on the phase 02 ladder detects this.** The clamp rate is the only instrument that sees it, and it exists only because the rule was written first | ai-ledger/11-fusion-and-arbiter.md |
| assumed | **wrong** | the phase 11 inputs were **not** reproducible — they lived only in a scratchpad, contradicting the claim in `.ci-lab/interviews/13.md` | ai-ledger/11-fusion-and-arbiter.md |
| unknown | known | `ci_triage/evidence.py` rebuilds them from `data/raw/` and reproduces frozen hash `305d8ece8a0fa240` exactly | ci_triage/evidence.py |
| unknown | known | the pre-registered prediction (2nd on accuracy, near-worst on calibration) is **wrong** — and irrelevant, since withdrawal is on safety not rank | experiments/11-fusion-comparison.md |

### Still open after the extension

| Statement | Why |
|---|---|
| one model, one prompt, one temperature | A different model, or a prompt arguing harder for caution, might clamp less. Untested. |
| the clamp is a wrapper, not a model property | Nothing shows the arbiter *could* be made safe — only that this one, unguarded, was not. |
| 49.5% base rate, not deployment's 3.16% | The ship-direction rule matters **more** at 3.16%, but these numbers do not transfer. |
| not re-derivable | Temperature 0 and a pinned model reduce variance; they do not guarantee identical output. Stored responses make it auditable, not reproducible. |

## Extension 2 (2026-09-29): the cautious prompt

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | **the cautious prompt makes the arbiter a constant**: `ESCALATE` 202/202, coverage 0.0%, accuracy and ECE undefined | artifacts/results/fusion.json |
| unknown | known | clamp rate **21.3% → 0.0%** — the predicted band was hit **by total abstention** | experiments/11-fusion-comparison.md |
| unknown | known | the prediction's **number was right and its verdict was refuted**: nothing was fixed, the component stopped working | experiments/11-fusion-comparison.md |
| assumed | **wrong** | the interpretation rule measured only clamp rate with **no coverage floor**, so a degenerate policy satisfied it — the fourth check in this repo passable without the thing it checks being true, written during the phase about that failure mode | experiments/11-fusion-comparison.md |
| unknown | known | **the baseline is not stable**: three identical runs give 24.3%, 17.8%, 21.3% — mean 21.1%, sd 3.3, range 6.5 points | artifacts/results/fusion.json |
| assumed | **over-precise** | extension 1's headline 24.3% should be read as **~21% ± 3** | artifacts/results/fusion.json |
| unknown | known | **both failure modes are reachable from one sentence of prompt text**, and accuracy/ECE cannot tell them apart — excellent for the dangerous variant, undefined for the useless one | experiments/11-fusion-comparison.md |

### Still open

| Statement | Why |
|---|---|
| **"bad idea or badly prompted" is still unsettled** | Neither prompt yields a usable component: the unsafe one ships defects on ~21% of cases, the safe one does no work. The question the extension was written to answer is not answered. |
| a prompt between the two is untested | Nothing tried a middle wording, or a coverage floor stated in the instruction rather than only in the interpretation rule. |
| single-run LLM numbers here carry ±3 points | Any future arbiter comparison needs repeated runs, not one. |
| none of it is tested at 3.16% | These 202 cases are 49.5% positive. |
