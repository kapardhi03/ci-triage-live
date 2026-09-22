# Phase 05

Scope: 2 of the 3 subset projects (`kevinsawicki-http-request`, `square-okhttp`), 15,813
runs. **Not** the 17-project reference; numbers here are not comparable to `precomputed/`.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | phase 03's "a flip is a proof" holds only if the run was real — the positive class had never been audited | decisions/05-infra-gate.md |
| unknown | known | five verdicts: TRUSTED, BUILD_FAILED, LOG_TRUNCATED, MASS_FAILURE, UNKNOWN; UNKNOWN derived the same way ABSTAIN was in phase 01 | design/05-infra-gate.md |
| unknown | known | precedence is BUILD_FAILED → LOG_TRUNCATED → MASS_FAILURE → TRUSTED, on **feasibility** first and cause-before-symptom second | decisions/05-infra-gate.md |
| unknown | known | on a truncated log the mass-failure fraction is **undefined, not approximate** — the denominator lives only on the Results lines, which are emitted last | decisions/05-infra-gate.md |
| unknown | known | the build end-marker is also at the end, so a truncated log cannot be distinguished from a process that died partway; the reason string says so | tests/test_infra.py::test_truncated_reason_admits_it_cannot_distinguish_truncation_from_death |
| unknown | known | Results lines are the ones **without** `Time elapsed`; summing all `Tests run:` lines double-counts (161+2+163=326 for a 163-test suite) | tests/test_infra.py::test_per_class_lines_are_not_summed_into_the_total |
| unknown | known | `square-okhttp` is a **5-module** build totalling 826 tests; reading the last summary alone would divide by a denominator several times too small | ai-ledger/05-infra-gate.md |
| unknown | known | `kevinsawicki` failure fractions are **bimodal**: 97.41% at exactly 0%, 2.59% at 7.98–9.20%, nothing between or above | artifacts/results/infra.json |
| unknown | known | 15 distinct tests ever fail there, in only **3 failure-set signatures**; 11 fail in 100% of failing runs; names cluster by function (query-param, SSL, proxy) | decisions/05-infra-gate.md |
| unknown | known | those failures are **uniformly scattered in run-id space** (2.3–2.9% per 1000-id block; mean gap 37.5 vs 38.6 expected) — correlated flakiness, not a precondition window | ai-ledger/05-infra-gate.md |
| unknown | known | the gate's deterministic set on okhttp (102 tests, from log text alone) **exactly equals** the CSV's never-passing set — intersection 102, Jaccard 1.000 | artifacts/results/infra.json |
| unknown | known | 36 of 7,908 okhttp runs are LOG_TRUNCATED: `total=127` of 826, median 14.7 KB vs ~507 KB healthy, and **zero** failing tests each | artifacts/results/infra.json |
| unknown | known | **headline: 15,813 runs gated, 36 rejected, 0 distinct failing tests lost.** Poisoned runs manufactured zero flaky labels in this subset | artifacts/results/infra.json |
| unknown | known | the motivating premise — poisoned runs marking unexecuted tests as failed — is **not demonstrated by this data** | ai-ledger/05-infra-gate.md |
| unknown | known | `kevinsawicki` archives cover run IDs **2095–9999 contiguously** (exactly 7,905); the ~2,095 missing runs are a prefix, not scattered loss | this session's scan |
| unknown | known | a verdict can be correct while its reason is fabricated; six mutations including a fabricated reason each kill a test | tests/test_infra.py |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| mass-failure threshold 30% | **untested** — max observed fraction 9.20%; every threshold from ~10% to 100% behaves identically |
| "a thin tail climbing up, then a gap" | **refuted** — bimodal, no tail, no catastrophes |
| okhttp: ~200 runs rejected | **refuted** — 36 |
| okhttp: ~300 distinct failing tests all-runs | **refuted** — 202 |
| okhttp: ~250 distinct failing tests trusted-runs | **refuted** — 202 |
| implied gap of ~50 manufactured tests | **refuted** — 0 |

All kept unedited.

## Open

| Statement | Why it is still open |
|---|---|
| **does gating discard real flakiness?** (TASK step 8) | Cannot be fully answered. In this subset the gate lost 0 tests, so the cost is unmeasured rather than shown to be zero. A project containing genuine run-wide failures would be needed, and none of the three subset projects has one. This is the strongest objection a reviewer can raise and it is open. |
| the 30% threshold is chosen, not validated | nothing in 15,813 runs exercises it |
| a fraction gate cannot prove a cluster shared one cause | 6947's 15-test cluster is coherent and reproducible, but "coherent" is inference, not proof |
| 15 flaky labels, plausibly 1 mechanism | over-counting handed to phase 10; not quantified |
| `kevinsawicki` CSV shows 18 flaky, archives show 15 ever failing | consistent with the missing 2,095-run prefix, but not verified — 3 tests' evidence is outside the archive |
| okhttp: 202 tests ever failed, only 100 are `IsFlaky` | the other 102 never passed; confirmed deterministic, but why they are broken on this revision is unexamined |
| the third subset project is ungated | `tootallnate-java-websocket` not yet run |
| no observer exists yet | this gate protects a pipeline that has not been built |
