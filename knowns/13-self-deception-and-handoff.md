# Phase 13

The last slice. No model. What moved is the split between failures that announce themselves
and failures that do not.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | slices **00, 01, 03, 10 are loud** — they throw, empty or crash, so the failure is its own symptom and needs no instrument | design/13-self-deception-and-handoff.md |
| unknown | known | slices **02, 04, 05, 06, 07, 08, 09, 11, 12 are silent** — each keeps emitting a plausible number and needs an invariant | design/13-self-deception-and-handoff.md |
| assumed | known | **three silent failures already happened here and none was caught by a passing test** — inverted cost mapping (02, five phases green), circular leak test (04), unsatisfiable criterion (08) | ai-ledger/13-self-deception-and-handoff.md |
| unknown | known | all three were caught by **deliberately trying to break something**, so mutation is part of the constraint, not a nicety | design/13-self-deception-and-handoff.md |
| unknown | known | every frozen constant in the instruments is **hardcoded in the test file**, independent of the module it grades | tests/test_invariants.py |
| unknown | known | five mutations kill the instruments: cost mapping inverted, de-dup removed, SPLIT never flagged, voice count pre-dedup, explanation fields lose provenance | this session's mutation runs |
| unknown | known | a skipped invariant reports **SKIPPED with a reason, never PASSED** — absence of evidence is not evidence, the phase 03 error | tests/test_invariants.py::_artifact |
| unknown | known | **execution time is a standard accepted predictor** in this literature, not treated as leakage by anyone | docs/prior-work.md |
| unknown | known | **typical rerun counts are ~20**; this corpus used 10,000, so its negative class is orders of magnitude cleaner than the field's norm | docs/prior-work.md |
| unknown | known | phase 03's argument would be **unrefuted on a normal dataset** — the phase 04 refutation is specific to N=10,000 | docs/prior-work.md |
| unknown | known | the cost-optimal threshold derivation in phase 07 is **textbook**, not novel | docs/prior-work.md |
| unknown | known | **named instruments exist for the correlation `cause_group` assigns by hand** — double-fault measure, Q statistic, disagreement measure, Kohavi-Wolpert variance | docs/prior-work.md |
| unknown | known | **independent work reproduces four of this repo's conclusions** on different detectors: models matching an always-flaky baseline, project-disjoint collapse, data leakage in published evaluations, detector collapse on rebuilt labels | docs/prior-work.md (arXiv 2607.09345) |
| unknown | known | that work states **"flakiness is not a static property of test code"** — the cause this repo reached only as a symptom | docs/prior-work.md |
| unknown | known | **KNOWNS.md: 185 established rows, 58 open** | KNOWNS.md |
| unknown | known | the explanation layer is now **minimally implemented** — `explain()` fills template slots from `Evidence` and every field traces to a record field | ci_triage/contracts.py, tests/test_invariants.py |

## Open

| Statement | Why it is still open |
|---|---|
| **the archives are not checksummed** | Zenodo publishes no per-file md5 for the `.tgz` files, so `fetch_archives.sh` verifies only that each is a readable gzip tar. A differing re-download would not be caught. |
| **some invariants grade recorded artifacts, not live re-runs** | `test_05` asserts Jaccard 1.000 from `infra.json`. A mis-parse that regenerated the artifact is caught; one that left it stale is not. The full re-run is ~55 s and is not wired in. |
| **`cause_group` is still hand-assigned** | The remedy is now named (double-fault, Q statistic) and cheap, and was not applied. No coupling involving observer 2 has ever been computed. |
| **the `ExecutionTime` leak is undecidable from this dataset** | The decisive fact — whether it was measured on runs including failures — is a question for the dataset authors, not a computation. |
| **the explanation layer has never been evaluated** | It is implemented and its invariants hold structurally. Whether it helps an engineer at 02:47, and whether its own alarm (explanations that start sounding smart) ever fires, is untested. |
| **the append-only evidence store is designed, not built** | Slice 13 specifies it; nothing implements it. Family 4.2 of the register predicts the failure it would prevent. |
| **Family 3.1 guards a mechanism this corpus never exercised** | Poisoned runs manufactured zero flaky labels here — the 36 truncated runs report no failures. The instrument is untested against a real instance. |
| **the system does not work** | Three observers matched or beaten by free alternatives; fusion adds nothing; the fine-tune was gated out; the shipped component is a dictionary lookup abstaining on 17.8% of cases. Recorded in every file rather than in none. |
