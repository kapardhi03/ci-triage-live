# Phase 10

No model in this phase. The contract, and two facts that were measured rather than assumed.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| assumed | **known** | the three observers' inputs are **literally disjoint** — the intersection of their `Reads` is empty | ci_triage/contracts.py::input_overlap, tests/test_contracts.py |
| assumed | **known — violated** | disjoint inputs are **not** independent evidence: `ExecutionTime` predicts whether observer 3 sees the SSL `NoSuchMethodError` at **AUC 0.6987, p = 1.06e-06** | decisions/10-independence.md |
| unknown | known | that coupling (0.6987) is **stronger than observer 1's link to its own label** (0.6765) | decisions/10-independence.md |
| unknown | known | one JVM/SSL incompatibility drives both observer 1's dominant feature and observer 3's dominant message | docs/architecture.md |
| unknown | known | run-level and case-level are **different questions with different consumers**: "is this test flaky" vs "does the release ship" | docs/architecture.md |
| unknown | known | with 196 flaky + 1 real defect, a **mean says SHIP and a majority vote says SHIP** — both ship a ~40h bug to avoid a ~3h hold | tests/test_contracts.py::test_one_real_defect_among_196_flakes_holds_the_release |
| unknown | known | the case-level rule is **hold-if-any-credibly-real**, never a mean or a vote | ci_triage/contracts.py::case_level |
| unknown | known | correlated records must be **collapsed, not averaged** — averaging still lets one event contribute twice | decisions/10-independence.md |
| unknown | known | adding a 3rd, 4th and 5th correlated record leaves the result **identical** (voices 1, deduplicated 4) | tests/test_contracts.py::test_agreement_from_a_shared_cause_cannot_inflate_confidence |
| unknown | known | `NO_EVIDENCE` and `INDETERMINATE` are different findings; a uniform probability merges them | ci_triage/contracts.py::State |
| unknown | known | a probability without a `calibrated` flag is **refused**, not warned about | tests/test_contracts.py::test_probability_without_the_calibrated_flag_is_refused |
| unknown | known | five mutations are killed: de-dup removed, case-level→mean, case-level→majority vote, calibrated flag optional, `NO_EVIDENCE` merged | this session's mutation runs |
| unknown | known | **three observers built, three matched or beaten by a free alternative** — the contract is correct machinery around unproven components | ai-ledger/10-architecture-independence.md |

## Open

| Statement | Why it is still open |
|---|---|
| **`cause_group` is hand-assigned, not detected** | One correlation measured, on one project, between two of three observers. The contract enforces a grouping a human typed in. A design recomputing groupings from output covariance would be strictly better and was not built. |
| **observer 2's couplings were never computed** | No pairwise measurement involving the sequence observer exists. If it shares a cause with observer 3, the contract counts them twice and nothing would reveal it. |
| the 0.6987 coupling is from one project | `square-okhttp` only — the one project with both classes. Whether the coupling holds elsewhere is untested. |
| `credible = 0.5` and `min_coverage = 0.5` are defaults | Neither was derived from the cost table. Phase 11 sets thresholds; these are placeholders that currently decide real outcomes. |
| ESCALATE has never fired on real data | The path is tested on synthetic records only. |
| the contract is unvalidated end to end | No real observer output has been passed through it. Phase 11 is the first time it carries live evidence. |

## Extension (2026-09-29): deriving `cause_group` from measured coupling

| Was | Now | Statement | Evidence |
|---|---|---|---|
| known-unknown | **known** | **the named remedy does not work on this data.** Double-fault and Q were applied to all three pairs and both are degenerate | artifacts/results/coupling.json |
| unknown | known | **Q = 1.0000 on all three pairs** — arithmetic, not dependence: `N01 = 0` everywhere, so `N01·N10` vanishes | artifacts/results/coupling.json |
| unknown | known | `N01` ("A wrong, B right") is empty because **the weak observer's errors strictly contain the strong ones'** — nesting, which neither measure can express | experiments/14-derived-cause-groups.md |
| unknown | known | double-fault is computed from `N00`, which holds **1, 1 and 2 observations** | artifacts/results/coupling.json |
| unknown | known | the disagreement measure appeared to **invert** the hand-assignment (`lookup`/`sequence` never disagree on 166 cases) and **fails significance**: expected 2.0 under independence, observed 0, P = 0.135 | artifacts/results/coupling.json |
| unknown | known | **all three pairs are indistinguishable from independent** by every measure computable here | artifacts/results/coupling.json |
| unknown | known | the derived grouping (**all three merged**) is an artifact and **was not applied** | experiments/14-derived-cause-groups.md |
| unknown | known | **the phase 10 input-based measurement had more power than the literature's standard instruments** — it measures inputs, they measure errors, and these observers rarely err | experiments/14-derived-cause-groups.md |
| unknown | known | the prediction was refuted in a **fifth way none of the four recorded conditions anticipated**: the instrument is degenerate | experiments/14-derived-cause-groups.md |

### Still open

| Statement | Why |
|---|---|
| **`cause_group` is still hand-assigned** | The remedy was applied and does not work here. The hand-assignment stands by default, not by validation — nothing confirms it and nothing here can refute it. |
| observer 2's coupling is still unmeasured **in any usable way** | It was computed; the computation carries no information. |
| what would be needed | A corpus where observers are wrong often enough to populate the both-wrong cell — far more cases, or observers nearer 50% accuracy where these measures have power. Neither is available. |
| input-based coupling generalises? | The AUC 0.6987 measurement worked where error-based measures failed. Whether input-based coupling detection is generally the better instrument here is untested. |
