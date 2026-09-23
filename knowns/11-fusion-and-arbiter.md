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
