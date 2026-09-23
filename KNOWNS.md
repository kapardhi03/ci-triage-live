# KNOWNS

Assembled from `knowns/00`–`knowns/13`. Every row's evidence column names a file or a
command; nothing here is asserted without one.

**The known-unknowns table is longer than it is comfortable for it to be. That is the
point.** A short one would mean the register was dishonest, not that the system was
understood.

## What moved (201 rows)

| Phase | Was | Now | Statement | Evidence |
|---|---|---|---|---|
| 00 | unknown | known | the decision is ship / hold / investigate the 09:00 release | PROBLEM.md |
| 00 | unknown | known | the actor is the on-call release engineer | PROBLEM.md |
| 00 | unknown | known | shipping a real bug costs more than delaying a good release | PROBLEM.md |
| 00 | unknown | known | the system reports a likely cause and confidence; the human makes the ship/hold call | design/00-start-here.md |
| 00 | unknown | known | the system abstains when evidence is too weak instead of guessing | design/00-start-here.md |
| 00 | unknown | known-unknown | what confidence threshold counts as "too weak" — rough intuition only, not derived yet | — |
| 00 | unknown | known-unknown | how test history and logs actually get turned into a cause judgment | — |
| 00 | unknown | known-unknown | how different signals (test history, system logs, network logs) get combined into one confidence number | — |
| 01 | unknown | known | four outputs: real defect, flaky, infrastructure, abstain — each triggers a different engineer action | decisions/01-output-space.md |
| 01 | unknown | known | ABSTAIN is derived from the case where evidence is too thin to call any of the three causes | decisions/01-output-space.md |
| 01 | unknown | known | false "flaky" costs ~40h (bug ships); false "real defect" costs ~3h (needless hold); asymmetry is ~13x | decisions/01-output-space.md |
| 01 | unknown | known | ABSTAIN costs ~1.5h — cheap but not free; must sit below wrong-hold or the system won't use it | decisions/01-output-space.md |
| 01 | unknown | known | objective is minimize total expected cost, not accuracy | decisions/01-output-space.md |
| 01 | unknown | known | accuracy is rejected because it treats every mistake as equal | ai-ledger/01-decision-and-cost.md |
| 01 | known-unknown | known-unknown | exact cost numbers are guesses — need real incident data to calibrate | — |
| 01 | known-unknown | known-unknown | confidence threshold for ABSTAIN vs. committing to a label — not derived yet | — |
| 01 | known-unknown | known-unknown | how to measure whether the system's confidence is trustworthy (calibration) | — |
| 02 | unknown | known | evaluation is a separate component, not a model method, so every model is scored by identical code — this is what makes phase 07's control a control | design/02-measurement.md, decisions/02-metric-ladder.md |
| 02 | unknown | known | at a 3% positive rate the constant "never flaky" model scores 0.97 accuracy and 0.0 recall on the same input | tests/test_metrics.py::test_constant_high_accuracy_zero_recall |
| 02 | unknown | known | equal-width ECE reports **0.000** for a model that predicts the base rate for every case; equal-frequency reports **0.042** on the same array | decisions/02-metric-ladder.md |
| 02 | unknown | known | equal-width bins carve the probability axis, equal-frequency bins carve the samples — under imbalance all predictions land in one equal-width bin where confidence equals accuracy by construction | decisions/02-metric-ladder.md |
| 02 | unknown | known | **ECE alone selects the useless model**: base-rate model ECE 0.000 vs perfect ranker ECE 0.105, while recall is 0.0 vs 1.0 and cost is 1.20 vs 0.00 | decisions/02-metric-ladder.md, tests/test_metrics.py::test_ece_alone_prefers_the_useless_model |
| 02 | unknown | known | calibration must never be read without a discrimination metric beside it | ai-ledger/02-measurement.md |
| 02 | unknown | known | the constant and base-rate models have ROC AUC = None, not 0.5 — a single-valued predictor cannot be ranked at all | tests/test_metrics.py::test_constant_model_auc_is_undefined_not_good |
| 02 | unknown | known | cost-weighted risk for both useless models is 1.20 engineer-hours/build; a perfect model is 0.00 | decisions/02-metric-ladder.md |
| 02 | assumed | known | the phase 01 cost asymmetry was **not** enforced by any test until this phase — flattening 40h to 3h left the suite green | ai-ledger/02-measurement.md |
| 02 | unknown | known | the suite is mutation-checked: symmetric costs, free abstain, abstain-costlier-than-hold, and equal_freq-collapsed-to-equal_width each fail exactly one test | this session's mutation runs |
| 02 | known-unknown | known-unknown | equal-frequency ECE is tie-order dependent when probabilities are identical (0.042 vs 0.048 by positive placement) — it is *not flattering*, but it is not *correct* on a single-valued predictor either | decisions/02-metric-ladder.md |
| 02 | known-unknown | known-unknown | every number above is from a 100-row hand-typed toy array; nothing has touched real CI data yet | — |
| 02 | known-unknown | known-unknown | how many ECE bins is right for the real dataset — 10 is a default, not a decision | — |
| 02 | known-unknown | known-unknown | the abstain threshold is still not derived; risk–coverage can now measure it but has not chosen it | — |
| 02 | known-unknown | known-unknown | whether the ~40h / ~3h / ~1.5h guesses survive contact with real incident data | knowns/01-decision-and-cost.md |
| 02 | known | **wrong** | "cost-weighted risk for both useless models is 1.20 engineer-hours/build" — the cost mapping was inverted against `IsFlaky`; the corrected figure is **0.09** | decisions/02-metric-ladder.md (correction) |
| 02 | unknown | known | an inverted cost table does not merely misreport magnitude — it makes "call it flaky" look cheap and points the system at the 40h error | decisions/02-metric-ladder.md (correction) |
| 02 | assumed | known | the phase 02 asymmetry test encoded the same misreading in its comments, so it passed while being wrong — the circular-test failure again | tests/test_metrics.py |
| 02 | unknown | known | direction is now pinned: `y=0` predicted `1` charges 40h, `y=1` predicted `0` charges 3h; flipping the mapping fails two tests | tests/test_metrics.py::test_the_expensive_error_is_calling_a_real_defect_flaky |
| 03 | assumed | known | no human judged these tests; every label is the output of a rerun procedure | decisions/03-label-procedure.md |
| 03 | unknown | known | `flaky` means a pass and a fail were witnessed on identical code — a proof | decisions/03-label-procedure.md |
| 03 | unknown | known | `not flaky` means N runs elapsed without a flip — absence of evidence at a sample size, not a property of the test | decisions/03-label-procedure.md |
| 03 | unknown | known | the label error is **one-directional**: a deterministic test cannot acquire a `flaky` mark, so contamination runs only into the negative class | experiments/03-rerun-bias.md |
| 03 | unknown | known | N reruns buys "not flakier than ~1-in-N", never "not flaky" — P(catch) = 1-(1-p)^N | decisions/03-label-procedure.md |
| 03 | unknown | known | at N=100, a genuine 1-in-500 race is mislabelled `not flaky` ~82% of the time | decisions/03-label-procedure.md (arithmetic, not measurement) |
| 03 | unknown | known | the hidden positives are systematically the **rare** flakes — frequent ones were caught, so the contamination sits in the hard cases | experiments/03-rerun-bias.md |
| 03 | unknown | known | certifying 1-in-500 across a 25-project corpus ≈ $2,000; certifying 1-in-5,000 ≈ $60,000 and ~5,200 days serial CI | decisions/03-label-procedure.md (costed on stated guesses) |
| 03 | unknown | known | no finite N finishes the job — every budget buys a threshold, never a proof; and the label is stale on the next commit | decisions/03-label-procedure.md |
| 03 | unknown | known | measured **precision is a lower bound**; measured **recall is an overestimate** (denominator holds only easily-caught flakes) — biased in opposite, known directions | experiments/03-rerun-bias.md |
| 03 | unknown | known | constraint carried into lab 05: **a false positive is a candidate, not a verdict** — FPs are sampled and reran before counting against a model | experiments/03-rerun-bias.md |
| 03 | unknown | known | model FPs are the cheapest search instrument for bad labels; the model that cannot be trusted is also how the labels get fixed | experiments/03-rerun-bias.md |
| 03 | unknown | known | dropping the negative class from selection was rejected — ~97% of rows discarded to avoid a few-percent error | ai-ledger/03-ground-truth.md |
| 03 | **known-unknown** | **known-unknown** | **N is not known.** Every number in this phase is conditional on it. Phase 04 must find the recorded rerun count; if unrecorded, that absence is the finding | decisions/03-label-procedure.md |
| 03 | known-unknown | known-unknown | the true flaky rate is higher than the published positive rate — direction predicted, magnitude unknown | experiments/03-rerun-bias.md |
| 03 | known-unknown | known-unknown | whether model-flagged FPs flip more often than random `not flaky` rows — the claim's main refutation condition, untested | experiments/03-rerun-bias.md |
| 03 | known-unknown | known-unknown | whether any reverse-direction error exists (labels merged across differing commits or environments) — would break the one-way claim | experiments/03-rerun-bias.md |
| 03 | known-unknown | known-unknown | the dataset's licence — not checked; phase 04 is a hard gate before any row is loaded | labs/04-data-and-licence/ |
| 04 | unknown | known | FlakeFlagger (Zenodo 4450723) is **CC-BY-4.0** — usable, attribution obligatory | decisions/04-dataset-choice.md |
| 04 | unknown | known | IDoFT has **no licence at all** — no LICENSE file, no badge, only a citation request | decisions/04-dataset-choice.md, ai-ledger/04 |
| 04 | assumed | known | **empty ≠ unrestricted**: copyright is automatic, so no licence means all rights reserved; GitHub ToS grants view/fork only | ai-ledger/04-data-and-licence.md |
| 04 | **known-unknown** | **known** | **N = 10,000.** 26,034 of 26,765 tests were run exactly 10,000 times (some 20k/30k, a tail fewer) — phase 03's central open unknown, closed | derived from `NumFailingRuns + NumPassingRuns` |
| 04 | assumed | known | `IsFlaky` is exactly `NumFailingRuns > 0 AND NumPassingRuns > 0` — all 828 flaky rows flipped, **zero** non-flaky rows did | scan of test_results.csv |
| 04 | unknown | known | the join key is `(suffix-matched project, lowercase(Test with '#'→'.'))` — neither project nor test name matches across files as published | ci_triage/data.py, artifacts/results/eda.json |
| 04 | unknown | known | joined shape: **26,134 rows, 825 positives, 3.1568%, 25 projects, 21 features** | artifacts/results/eda.json |
| 04 | unknown | known | two candidate labels disagree on **904 tests**; **763 of 825** rerun-proven flaky tests (92%) are invisible to the tool label | cross-tab, decisions/04-dataset-choice.md |
| 04 | unknown | known | `IsFlaky` (rerun-observed) chosen as ground truth over `flaky` (tool-labelled) | decisions/04-dataset-choice.md |
| 04 | unknown | known | four label-derived columns found by single-column AUC scan: `FirstFailingRunID` (**1.000**), `UniqueFailingExceptionTypes` (0.998), `NumFailingRuns` (0.994), `NumPassingRuns` (0.993) | leak scan, this session |
| 04 | unknown | known | the general method: a leaking column is one that could not exist before the answer was known, and shows up as a single column separating the classes almost perfectly | tests/test_data.py::test_no_column_predicts_the_label_alone |
| 04 | unknown | known | `hIndex...window5` takes 1.8 distinct values per project with 89.0% of rows at the project mode — a project identifier in numeric costume | constancy measurement, this session |
| 04 | unknown | known | the 8 history features require git history the dataset does not ship (Project_Info.csv = 24 rows of URL+SHA, one revision each) | artifacts/results/eda.json, design/04 |
| 04 | unknown | known | exclusion policy: 4 rerun columns + `flaky` + `flaky_source` + `window5` + `window10` dropped; 6 history columns kept | design/04-data-and-licence.md |
| 04 | unknown | known | strongest surviving feature is `ExecutionTime` at AUC 0.76; everything else ≤0.65 | leak scan |
| 04 | assumed | known | a leak test graded against the module's own exclusion list is **circular** and passes when an entry is deleted | ai-ledger/04-data-and-licence.md |
| 04 | unknown | known | row accounting: 469 results rows dropped (3 unmapped projects), 8 case-folding collisions, 485 feature rows unjoined | artifacts/results/eda.json |
| 05 | unknown | known | phase 03's "a flip is a proof" holds only if the run was real — the positive class had never been audited | decisions/05-infra-gate.md |
| 05 | unknown | known | five verdicts: TRUSTED, BUILD_FAILED, LOG_TRUNCATED, MASS_FAILURE, UNKNOWN; UNKNOWN derived the same way ABSTAIN was in phase 01 | design/05-infra-gate.md |
| 05 | unknown | known | precedence is BUILD_FAILED → LOG_TRUNCATED → MASS_FAILURE → TRUSTED, on **feasibility** first and cause-before-symptom second | decisions/05-infra-gate.md |
| 05 | unknown | known | on a truncated log the mass-failure fraction is **undefined, not approximate** — the denominator lives only on the Results lines, which are emitted last | decisions/05-infra-gate.md |
| 05 | unknown | known | the build end-marker is also at the end, so a truncated log cannot be distinguished from a process that died partway; the reason string says so | tests/test_infra.py::test_truncated_reason_admits_it_cannot_distinguish_truncation_from_death |
| 05 | unknown | known | Results lines are the ones **without** `Time elapsed`; summing all `Tests run:` lines double-counts (161+2+163=326 for a 163-test suite) | tests/test_infra.py::test_per_class_lines_are_not_summed_into_the_total |
| 05 | unknown | known | `square-okhttp` is a **5-module** build totalling 826 tests; reading the last summary alone would divide by a denominator several times too small | ai-ledger/05-infra-gate.md |
| 05 | unknown | known | `kevinsawicki` failure fractions are **bimodal**: 97.41% at exactly 0%, 2.59% at 7.98–9.20%, nothing between or above | artifacts/results/infra.json |
| 05 | unknown | known | 15 distinct tests ever fail there, in only **3 failure-set signatures**; 11 fail in 100% of failing runs; names cluster by function (query-param, SSL, proxy) | decisions/05-infra-gate.md |
| 05 | unknown | known | those failures are **uniformly scattered in run-id space** (2.3–2.9% per 1000-id block; mean gap 37.5 vs 38.6 expected) — correlated flakiness, not a precondition window | ai-ledger/05-infra-gate.md |
| 05 | unknown | known | the gate's deterministic set on okhttp (102 tests, from log text alone) **exactly equals** the CSV's never-passing set — intersection 102, Jaccard 1.000 | artifacts/results/infra.json |
| 05 | unknown | known | 36 of 7,908 okhttp runs are LOG_TRUNCATED: `total=127` of 826, median 14.7 KB vs ~507 KB healthy, and **zero** failing tests each | artifacts/results/infra.json |
| 05 | unknown | known | **headline: 15,813 runs gated, 36 rejected, 0 distinct failing tests lost.** Poisoned runs manufactured zero flaky labels in this subset | artifacts/results/infra.json |
| 05 | unknown | known | the motivating premise — poisoned runs marking unexecuted tests as failed — is **not demonstrated by this data** | ai-ledger/05-infra-gate.md |
| 05 | unknown | known | `kevinsawicki` archives cover run IDs **2095–9999 contiguously** (exactly 7,905); the ~2,095 missing runs are a prefix, not scattered loss | this session's scan |
| 05 | unknown | known | a verdict can be correct while its reason is fabricated; six mutations including a fabricated reason each kill a test | tests/test_infra.py |
| 06 | unknown | known | deployment sees **unseen projects**, so leave-one-project-out is the reported split | decisions/06-split-choice.md |
| 06 | unknown | known | random 5-fold **0.7621**, grouped 5-fold 0.6060, LOPO **0.6490** on 21 features — gap **0.1131** | artifacts/results/baseline.json |
| 06 | unknown | known | the random split's std is **0.0127** against LOPO's **0.1295** — it reports a falsely *stable* number, not only a falsely high one | artifacts/results/baseline.json |
| 06 | unknown | known | fold-to-fold agreement under a random split comes from every fold containing the same projects; real cross-project performance varies enormously | decisions/06-split-choice.md |
| 06 | unknown | known | dropping the 8 project-scale features costs the random split **0.005** and gains LOPO **+0.039** — the fingerprint of a project identifier in disguise | experiments/06-split-comparison.md |
| 06 | unknown | known | the base-rate mechanism is **supported**: the gap collapses 38.8% (0.1131 → 0.0692) when those features go | experiments/06-split-comparison.md |
| 06 | unknown | known | **phase 04's history-column decision is reversed.** All 8 project-scale features excluded, matrix is now **13 features** | ci_triage/data.py, artifacts/results/eda.json |
| 06 | unknown | known | the git-history dependency accepted into the phase 00 boundary in phase 04 is **cancelled** | decisions/06-split-choice.md |
| 06 | unknown | known | **reported baseline: LOPO AUC 0.6878 ± 0.1299** over 23 evaluable folds, 13 features | artifacts/results/baseline.json |
| 06 | unknown | known | majority baseline is **96.84% accurate with AUC 0.500** — phase 02's lesson on real data | artifacts/results/baseline.json |
| 06 | unknown | known | `jimfs` and `commons-exec` have **zero positives**, so LOPO has 23 evaluable folds, not 25 | artifacts/results/baseline.json |
| 06 | unknown | known | the positive rate spans ~4,000× by project (`alluxio` 62.0% → `assertj-core` 0.016%), and `assertj-core` is 24% of rows with 1 positive | this session's scan |
| 06 | unknown | known | a project on both sides of a fold is invisible in the metrics and fatal to the claim; checked per fold, and the detector is proven capable of failing | tests/test_splits.py |
| 06 | unknown | known | **0.6878 is the number later phases must beat**, not 0.7569 | decisions/06-split-choice.md |
| 07 | unknown | known | GBT calibrated scores **0.6781 ±0.159** LOPO — **worse** than phase 06's logistic regression at 0.6878 | artifacts/results/tabular.json |
| 07 | unknown | known | calibration moved AUC **+0.0016** (sigmoid) and **−0.0116** (isotonic); both monotonic, so ties and the internal refit are doing the work, not the mapping | experiments/07-calibration-tradeoff.md |
| 07 | unknown | known | ECE improved only 6.6% (equal-width) and 2.5% (equal-frequency) — "much better" was refuted | experiments/07-calibration-tradeoff.md |
| 07 | unknown | known | **cost-weighted risk halved, 0.5440 → 0.2708**, while AUC and ECE barely moved | artifacts/results/tabular.json |
| 07 | unknown | known | **the model IS the constant baseline**: both cost 0.0957 h/row to four decimals | artifacts/results/tabular.json |
| 07 | unknown | known | the cost-optimal threshold from the phase 01 table is **p > 0.930**; the calibrated model's maximum probability over 25,867 rows is **0.2362** | decisions/07-the-pivot.md |
| 07 | unknown | known | **no threshold beats the constant**, calibrated or uncalibrated; the best found flags zero rows | artifacts/results/tabular.json |
| 07 | unknown | known | the uncalibrated model's **top-10 most confident predictions are 0/10 correct**; precision peaks at 10% against a 93% requirement | artifacts/results/tabular.json |
| 07 | unknown | known | **the pivot to abstention is refuted**: abstention costs 1.5h/row to avoid 0.0957h/row; optimal qualifier threshold is 0.00 | decisions/07-the-pivot.md |
| 07 | unknown | known | an **oracle** qualifier saves **2.7%**, abstaining on one project (`alluxio`) — the ceiling, not the qualifier, is the limit | artifacts/results/tabular.json |
| 07 | unknown | known | qualifier correlates weakly and correctly: Spearman vs cost **−0.357**, vs AUC **+0.323** | artifacts/results/tabular.json |
| 07 | unknown | known | **the observer is effectively one feature**: dropping `ExecutionTime` takes LOPO from 0.6765 to **0.5577** | experiments/07-execution-time-leak.md |
| 07 | unknown | known | `ExecutionTime` drives **39.4%** of the alien-project distance — the coupling predicted in design/07 before measurement holds | design/07, tests/test_tabular.py |
| 07 | assumed | **wrong** | phase 02's `cost_weighted_risk` had the cost mapping **inverted** against `IsFlaky`, making "call it flaky" look cheap — the 40h error | ai-ledger/07, decisions/02 (correction) |
| 07 | unknown | known | a qualifier fitted on all projects cannot detect the held-out one as alien | tests/test_tabular.py::test_qualifier_is_fitted_without_the_held_out_project |
| 08 | unknown | known | predicting `IsFlaky` from a full run sequence is **circular** — the label is *"does this list contain both a 0 and a 1"*, computable by regex, AUC 1.0 by construction | experiments/08-heuristic-control.md |
| 08 | unknown | known | **`IsFlaky` conflates two phenomena**: `P P F P F P` (non-determinism) and `F F F F P P P P` (broken then fixed) both satisfy it; only the arrangement separates them | ai-ledger/08-sequence-observer.md |
| 08 | unknown | known | "interleaved vs blocked" is **also circular** as a task — the label is a function of the sequence fed in | experiments/08-heuristic-control.md |
| 08 | unknown | known | prefix-predicts-suffix is circularity-free and answers an actionable question: *given this history, will the test flip going forward?* | design/08-sequence-observer.md |
| 08 | unknown | known | **the control — a `sum()` over the prefix — scores 1.0000 on kevinsawicki at both prefix lengths and 0.9992 on tootallnate/2000**; mean 0.9296 at k=2000 | artifacts/results/sequence.json |
| 08 | unknown | known | the control sits at **exactly chance (0.4967)** on okhttp/200, the only cell where anything was at stake | artifacts/results/sequence.json |
| 08 | unknown | known | **the GRU never beats the control: 0 wins, 2 ties, 4 losses** across six cells | artifacts/results/sequence.json |
| 08 | unknown | known | the pre-registered criterion required 0.5467 on okhttp/200; the model scored **0.4975**. **Withdrawn** | experiments/08-heuristic-control.md |
| 08 | unknown | known | in the decision cell the control's 95% CI is **[0.4647, 0.5331]** — contains 0.5. **Neither predictor beats chance there** | artifacts/results/sequence.json |
| 08 | unknown | known | a calibrated AUC of 0.5000 with **`n_distinct` = 1** means the model collapsed to a constant, not that it ranks at chance — AUC alone cannot tell them apart | artifacts/results/sequence.json |
| 08 | unknown | known | the GRU's raw AUC on kevinsawicki/200 is **0.0000** — perfectly inverted, not random; monotonic calibration flattened it to a constant rather than un-inverting it | artifacts/results/sequence.json |
| 08 | unknown | known | observer 2's inputs are **disjoint** from observer 1's — zero shared columns — but disjoint inputs are not independent evidence | design/08-sequence-observer.md |
| 08 | assumed | known | a keep/throw criterion can itself be circular: "beat the control by 0.05 in every cell" was unsatisfiable in 3 of 6 cells by arithmetic | ai-ledger/08-sequence-observer.md |
| 08 | unknown | known | the same structural flaw — a check whose reference derives from the thing it checks — has now appeared **three times** (phases 04, 07, 08), caught each time only by trying to break it | ai-ledger/08-sequence-observer.md |
| 09 | unknown | known | retrieval keeps what weights discard: at 3.16% positives the gradient is dominated by the majority class and rare cases average into the noise floor; an index compresses nothing | decisions/09-index-contents.md |
| 09 | unknown | known | MiniLM embeddings + 5-NN score **0.9851** against a **0.5050** majority baseline, leave-one-class-out | artifacts/results/retrieval.json |
| 09 | unknown | known | **a single substring check scores 0.9851 — identical to four decimals** | artifacts/results/retrieval.json |
| 09 | unknown | known | TF-IDF char-ngrams + 5-NN also score 0.9851; exact-message lookup scores **0.9940** where it matches | artifacts/results/retrieval.json |
| 09 | unknown | known | **100 of 102 deterministic tests share one failure message** (`NoSuchMethodError: setSNIServerNames`) | artifacts/results/retrieval.json |
| 09 | unknown | known | the corpus holds **19 distinct messages across 202 tests** — the effective sample size is ~19, not 202 | artifacts/results/retrieval.json |
| 09 | unknown | known | the same message appears under **both** labels: one flaky test shares the deterministic cluster's text | decisions/09-index-contents.md |
| 09 | unknown | known | **the shipped component is `MessageLookup`**: 82.2% coverage, **0.9940 precision on covered**, 36 abstentions | artifacts/results/retrieval.json |
| 09 | unknown | known | abstaining on an unseen message removes the stateful-dependency problem entirely — the table is the state, and no stale neighbour is silently returned | ai-ledger/09-retrieval-observer.md |
| 09 | unknown | known | indexing the test/class name would leak: every `HttpOverSpdy3Test.*` is deterministic, so class membership recovers the label without reading the failure | decisions/09-index-contents.md |
| 09 | unknown | known | a single-class index makes precision@k **1.0 by construction**; the observer refuses rather than warns | tests/test_retrieval.py::test_single_class_index_is_refused |
| 09 | unknown | known | without the self-exclusion guard a query retrieves **itself at distance 0** with its own label | tests/test_retrieval.py::test_without_the_guard_the_query_does_retrieve_itself |
| 09 | unknown | known | **cross-project retrieval is not performable in either direction** and is recorded unscored | artifacts/results/retrieval.json |
| 09 | unknown | known | **three phases, three free alternatives, zero wins for the trained component** (07 tie, 08 loss, 09 tie) | ai-ledger/09-retrieval-observer.md |
| 10 | assumed | **known** | the three observers' inputs are **literally disjoint** — the intersection of their `Reads` is empty | ci_triage/contracts.py::input_overlap, tests/test_contracts.py |
| 10 | assumed | **known — violated** | disjoint inputs are **not** independent evidence: `ExecutionTime` predicts whether observer 3 sees the SSL `NoSuchMethodError` at **AUC 0.6987, p = 1.06e-06** | decisions/10-independence.md |
| 10 | unknown | known | that coupling (0.6987) is **stronger than observer 1's link to its own label** (0.6765) | decisions/10-independence.md |
| 10 | unknown | known | one JVM/SSL incompatibility drives both observer 1's dominant feature and observer 3's dominant message | docs/architecture.md |
| 10 | unknown | known | run-level and case-level are **different questions with different consumers**: "is this test flaky" vs "does the release ship" | docs/architecture.md |
| 10 | unknown | known | with 196 flaky + 1 real defect, a **mean says SHIP and a majority vote says SHIP** — both ship a ~40h bug to avoid a ~3h hold | tests/test_contracts.py::test_one_real_defect_among_196_flakes_holds_the_release |
| 10 | unknown | known | the case-level rule is **hold-if-any-credibly-real**, never a mean or a vote | ci_triage/contracts.py::case_level |
| 10 | unknown | known | correlated records must be **collapsed, not averaged** — averaging still lets one event contribute twice | decisions/10-independence.md |
| 10 | unknown | known | adding a 3rd, 4th and 5th correlated record leaves the result **identical** (voices 1, deduplicated 4) | tests/test_contracts.py::test_agreement_from_a_shared_cause_cannot_inflate_confidence |
| 10 | unknown | known | `NO_EVIDENCE` and `INDETERMINATE` are different findings; a uniform probability merges them | ci_triage/contracts.py::State |
| 10 | unknown | known | a probability without a `calibrated` flag is **refused**, not warned about | tests/test_contracts.py::test_probability_without_the_calibrated_flag_is_refused |
| 10 | unknown | known | five mutations are killed: de-dup removed, case-level→mean, case-level→majority vote, calibrated flag optional, `NO_EVIDENCE` merged | this session's mutation runs |
| 10 | unknown | known | **three observers built, three matched or beaten by a free alternative** — the contract is correct machinery around unproven components | ai-ledger/10-architecture-independence.md |
| 11 | unknown | known | **A, B and C emit identical labels on 202/202 cases** — one decision rule, three probability shapes | artifacts/results/fusion.json |
| 11 | unknown | known | A 0.9554 / B 0.9554 / C 0.9554 accuracy; ECE 0.0435 / 0.0914 / 0.0446 | artifacts/results/fusion.json |
| 11 | unknown | known | D scores 0.9940 at **82.2% coverage** — and A, B, C all score **0.9940 on those same 166 cases** | artifacts/results/fusion.json |
| 11 | unknown | known | **D's advantage is entirely which cases it declines**, and it declines exactly the 36 where the lookup has no entry | experiments/11-fusion-comparison.md |
| 11 | unknown | known | D reproduces phase 09's `MessageLookup` result exactly (0.9940 on 166) | artifacts/results/fusion.json |
| 11 | unknown | known | **the tabular observer's maximum probability over 202 cases is 0.1609** — it cannot move any decision at a 0.5 cutoff | artifacts/results/fusion.json |
| 11 | unknown | known | slice 10's collapse leaves **2 distinct voices, never 3** (166 records de-duplicated; lookup wins the collapse 161/202) | artifacts/results/fusion.json |
| 11 | unknown | known | **fusion adds nothing** — the three-observer architecture reduces to the phase 09 lookup plus an abstention rule | ai-ledger/11-fusion-and-arbiter.md |
| 11 | unknown | known | JS divergence distinguishes what total variation cannot: JS(0.45,0.55)=0.0072 vs JS(0.05,0.15)=0.0209, both TV 0.10 | decisions/11-arbiter-rules.md |
| 11 | unknown | known | two observers can share a label and diverge sharply: 0.51 and 0.99 are both "flaky" | tests/test_fusion.py::test_same_label_can_hide_a_large_divergence |
| 11 | unknown | known | false consensus is detectable and **did not occur** here: 0 cases flagged | artifacts/results/fusion.json |
| 11 | unknown | known | **E is incomplete and unranked** — no API key, no SDK; predicted position recorded and never checked | artifacts/results/fusion.json |
| 11 | unknown | known | the rendered arbiter prompt (1,320 chars) contains no label, test name, class name, project, or other strategy output | decisions/11-arbiter-rules.md |
| 12 | unknown | known | a 3B model at 16-bit needs **37.47 GiB** to fully fine-tune — weights 5.59, gradients 5.59, **optimiser 22.35**, activations 3.94 | decisions/12-memory-ledger.md |
| 12 | unknown | known | **the optimiser is the largest line**, 4× the weights; "a 3B model needs ~6 GB" is wrong by 6× before activations | decisions/12-memory-ledger.md |
| 12 | unknown | known | quantisation attacks **weights only** (5.59→1.40) and does nothing for the optimiser | decisions/12-memory-ledger.md |
| 12 | unknown | known | LoRA's saving is **not in the weights** — it attacks gradients + optimiser (27.94→0.047); the base stays resident for the forward pass | decisions/12-memory-ledger.md |
| 12 | unknown | known | checkpointing attacks **activations** (3.94→0.47) and is the only line that costs compute back (~+30%) | decisions/12-memory-ledger.md |
| 12 | unknown | known | redrawn: **1.92 GiB, a 20× reduction** — fits a free Kaggle T4 eight times over | decisions/12-memory-ledger.md |
| 12 | unknown | known | one **real** rendered prompt is 1,895 chars ≈ **677 input tokens**; all 202 cases cost **~$8.26** with Opus 5 at modest thinking | experiments/12-distillation-cost.md |
| 12 | unknown | known | **neither cost line binds.** The phase-05 claim that API calls, not the GPU, are the real cost is **overturned on this corpus** | ai-ledger/12-slm-and-the-ledger.md |
| 12 | unknown | known | **TF-IDF char-ngram + linear: 0.9825 ±0.0300**; exact-message lookup **0.9975 ±0.0050** | artifacts/results/slm.json |
| 12 | unknown | known | paired gap TF-IDF − lookup is **−0.0150 against SE 0.0155 — inside fold noise**; headroom to ceiling **0.0175** | artifacts/results/slm.json |
| 12 | unknown | known | **the gate fired. No GPU provisioned, no fine-tune, recorded as a complete decision** | experiments/12-finetune-vs-tfidf.md |
| 12 | unknown | known | the reason is **evidence, not affordability**: 19 distinct messages means an SLM learns the same 19-way lookup more expensively with more room to overfit | ai-ledger/12-slm-and-the-ledger.md |
| 12 | assumed | known | **the majority baseline is 0.2474 — worse than chance**, not the 0.4950 raw base rate; grouped splitting on homogeneous test classes makes the training majority mispredict whole folds (one fold scores 0.000) | artifacts/results/distill-corpus.json |
| 12 | unknown | known | the explanation layer **states the basis, never the belief** — it reports what was observed so the account stays true even when the verdict is wrong | design/12-slm-and-the-ledger.md |
| 12 | unknown | known | `precomputed/slm-eval.json` **stayed sealed** — the falsifier did not fire, and no number from it appears anywhere in this phase | artifacts/results/slm.json |
| 13 | unknown | known | slices **00, 01, 03, 10 are loud** — they throw, empty or crash, so the failure is its own symptom and needs no instrument | design/13-self-deception-and-handoff.md |
| 13 | unknown | known | slices **02, 04, 05, 06, 07, 08, 09, 11, 12 are silent** — each keeps emitting a plausible number and needs an invariant | design/13-self-deception-and-handoff.md |
| 13 | assumed | known | **three silent failures already happened here and none was caught by a passing test** — inverted cost mapping (02, five phases green), circular leak test (04), unsatisfiable criterion (08) | ai-ledger/13-self-deception-and-handoff.md |
| 13 | unknown | known | all three were caught by **deliberately trying to break something**, so mutation is part of the constraint, not a nicety | design/13-self-deception-and-handoff.md |
| 13 | unknown | known | every frozen constant in the instruments is **hardcoded in the test file**, independent of the module it grades | tests/test_invariants.py |
| 13 | unknown | known | five mutations kill the instruments: cost mapping inverted, de-dup removed, SPLIT never flagged, voice count pre-dedup, explanation fields lose provenance | this session's mutation runs |
| 13 | unknown | known | a skipped invariant reports **SKIPPED with a reason, never PASSED** — absence of evidence is not evidence, the phase 03 error | tests/test_invariants.py::_artifact |
| 13 | unknown | known | **execution time is a standard accepted predictor** in this literature, not treated as leakage by anyone | docs/prior-work.md |
| 13 | unknown | known | **typical rerun counts are ~20**; this corpus used 10,000, so its negative class is orders of magnitude cleaner than the field's norm | docs/prior-work.md |
| 13 | unknown | known | phase 03's argument would be **unrefuted on a normal dataset** — the phase 04 refutation is specific to N=10,000 | docs/prior-work.md |
| 13 | unknown | known | the cost-optimal threshold derivation in phase 07 is **textbook**, not novel | docs/prior-work.md |
| 13 | unknown | known | **named instruments exist for the correlation `cause_group` assigns by hand** — double-fault measure, Q statistic, disagreement measure, Kohavi-Wolpert variance | docs/prior-work.md |
| 13 | unknown | known | **independent work reproduces four of this repo's conclusions** on different detectors: models matching an always-flaky baseline, project-disjoint collapse, data leakage in published evaluations, detector collapse on rebuilt labels | docs/prior-work.md (arXiv 2607.09345) |
| 13 | unknown | known | that work states **"flakiness is not a static property of test code"** — the cause this repo reached only as a symptom | docs/prior-work.md |
| 13 | unknown | known | **KNOWNS.md: 185 established rows, 58 open** | KNOWNS.md |
| 13 | unknown | known | the explanation layer is now **minimally implemented** — `explain()` fills template slots from `Evidence` and every field traces to a record field | ci_triage/contracts.py, tests/test_invariants.py |

## What remains unknown (66 rows)

| Phase | Statement | Why it is still open |
|---|---|---|
| 04 | whether keeping 6 history columns was right | phase 06's held-out-project gap is the test; revisit if it stays large |
| 04 | the 80% mode-share threshold is a chosen number | no natural break in the gradient; written down so it can be argued with |
| 04 | the git-history dependency is unbuilt | accepted into the phase 00 boundary, not yet designed or costed |
| 04 | 469 + 485 rows excluded by the join | not investigated per-project; a systematic loss in one project would bias `groups` |
| 04 | 8 case-folding collisions kept-first | arbitrary tie-break; unexamined whether the discarded twin differed in label |
| 04 | `ExecutionTime` at AUC 0.76 is suspiciously strong | not yet established whether it is a real signal or an artifact of how long failing tests run |
| 04 | no model has been trained | every number here describes data, not performance |
| 05 | **does gating discard real flakiness?** (TASK step 8) | Cannot be fully answered. In this subset the gate lost 0 tests, so the cost is unmeasured rather than shown to be zero. A project containing genuine run-wide failures would be needed, and none of the three subset projects has one. This is the strongest objection a reviewer can raise and it is open. |
| 05 | the 30% threshold is chosen, not validated | nothing in 15,813 runs exercises it |
| 05 | a fraction gate cannot prove a cluster shared one cause | 6947's 15-test cluster is coherent and reproducible, but "coherent" is inference, not proof |
| 05 | 15 flaky labels, plausibly 1 mechanism | over-counting handed to phase 10; not quantified |
| 05 | `kevinsawicki` CSV shows 18 flaky, archives show 15 ever failing | consistent with the missing 2,095-run prefix, but not verified — 3 tests' evidence is outside the archive |
| 05 | okhttp: 202 tests ever failed, only 100 are `IsFlaky` | the other 102 never passed; confirmed deterministic, but why they are broken on this revision is unexamined |
| 05 | the third subset project is ungated | `tootallnate-java-websocket` not yet run |
| 05 | no observer exists yet | this gate protects a pipeline that has not been built |
| 06 | **61% of the gap is unexplained** | Removing project-scale features closed 38.8%. Project identity travels by a route not yet named. The prime suspect is test-level features correlating with project, but nothing has been measured. Carried to phase 07. |
| 06 | the deployment question was answered **after** seeing the numbers | TASK step 2 requires the reverse order. Phase 00 had not fixed the deployment context. The decision is contaminated and disclosed as such; the argument does not appear to depend on the numbers, but that is unauditable. |
| 06 | LOPO std is 0.1299 — folds disagree violently | A mean over 23 wildly varying folds may not be the right summary. Per-project results are recorded in `baseline.json` but not analysed. |
| 06 | 8 of 25 projects have <5 positives | Their folds are near-meaningless individually yet weighted equally in the mean. An alternative weighting has not been considered. |
| 06 | logistic regression is a floor, not a model | Phase 07 builds the real tabular observer. Whether the gap behaves the same under a stronger model is unknown — a higher-capacity model may memorise projects *harder*. |
| 06 | the test-set ledger has never been used | It records access; nothing has accessed it yet. Its value is untested. |
| 07 | **the `ExecutionTime` leak is unresolved** | A leak present in both train and test transfers fine, so strong cross-project contribution is consistent with both readings. Decisive evidence is whether it was measured on runs including failures — the dataset does not ship it. |
| 07 | the 40/3/1.5 cost numbers dominate every result here | Flagged as guesses in `knowns/01`. **Deliberately not revisited** — changing them because the model looks bad is the dishonest option. Any change must be argued from the organisation, not the metric. |
| 07 | 61% of the phase 06 split gap is still unexplained | Carried forward untouched; this phase added no evidence either way. |
| 07 | can the observer contribute **in combination**? | This phase only shows it cannot act alone. Phase 11's question, now open rather than assumed. |
| 07 | will three observers be independent? | Sharper than expected: this one reduces to a single column, so three observers are three observers only if they do not all rest on the same signal. Phase 10. |
| 07 | the qualifier is built and unused | Its design survives — distance, not model confidence — but the economics give it nothing to buy here. It may matter when a component exists that is worth gating. |
| 07 | LOPO fold spread remains enormous | ±0.159. `assertj-core` scores AUC 0.255, `Achilles` 0.881. A mean over 23 such folds may be the wrong summary. |
| 08 | **the label-conflation defect is unmeasured** | How many `IsFlaky=1` tests are broken-then-fixed rather than non-deterministic? Never counted. Rejected as a task because it is circular; still a real defect in the ground truth. Carry to phase 13. |
| 08 | 3 projects is a very thin base | Two of three are at ceiling for the control, so the comparison rests almost entirely on okhttp. A fourth project could change the summary. |
| 08 | nothing predicts okhttp/200 | Neither control nor model beats chance. Whether the first 200 runs genuinely carry no signal, or whether a different representation would find some, is untested. |
| 08 | the GRU was barely tuned | hidden=16, 30 epochs, one seed. A stronger model might win — but it would have to beat a free `sum()`, and it lost by 0.24–0.50 in four cells. |
| 08 | are observers 1 and 2 independent? | Inputs are disjoint, which is necessary and not sufficient. Phase 10's question, now with one observer withdrawn. |
| 08 | two observers, two withdrawals | Phase 07's tabular observer cannot beat a constant; phase 08's sequence observer cannot beat a `sum()`. Whether anything survives for phase 11 to fuse is genuinely open. |
| 09 | **is 0.9851 a result about flakiness, or about one broken JVM?** | The dominant signal is a single `NoSuchMethodError` from an SSL/JVM incompatibility on the machine that produced these archives. It separates deterministic from flaky here; whether it generalises to any other environment is untested and probably not. |
| 09 | effective sample size ~19 | 202 tests are ~19 opinions. Confidence intervals computed over 202 would be badly overstated, and none were reported for that reason. |
| 09 | one project | `kevinsawicki` and `tootallnate` have no deterministic tests at all, so nothing cross-project can be measured. A fourth project with both classes would change what is claimable. |
| 09 | the 36 abstentions | 17.8% of tests have no message precedent. Whether that fraction is stable, or an artifact of holding out whole classes, is unmeasured. |
| 09 | observers are all redundant with something free | Three for three. Whether phase 11 has anything to fuse is now a serious question rather than a formality. |
| 09 | is the failure text independent evidence? | Inputs are disjoint from observers 1 and 2, but the dominant message reflects one environmental cause that may also drive `ExecutionTime`. Phase 10's question. |
| 10 | **`cause_group` is hand-assigned, not detected** | One correlation measured, on one project, between two of three observers. The contract enforces a grouping a human typed in. A design recomputing groupings from output covariance would be strictly better and was not built. |
| 10 | **observer 2's couplings were never computed** | No pairwise measurement involving the sequence observer exists. If it shares a cause with observer 3, the contract counts them twice and nothing would reveal it. |
| 10 | the 0.6987 coupling is from one project | `square-okhttp` only — the one project with both classes. Whether the coupling holds elsewhere is untested. |
| 10 | `credible = 0.5` and `min_coverage = 0.5` are defaults | Neither was derived from the cost table. Phase 11 sets thresholds; these are placeholders that currently decide real outcomes. |
| 10 | ESCALATE has never fired on real data | The path is tested on synthetic records only. |
| 10 | the contract is unvalidated end to end | No real observer output has been passed through it. Phase 11 is the first time it carries live evidence. |
| 11 | **the LLM arbiter was never measured** | The central question this phase is named for is unanswered. Not a failure of the experiment — a gap in it, and one no amount of reasoning about the other four strategies fills. |
| 11 | base rate 0.495 vs deployment 0.0316 | Every number is flattered. D's abstention economics in particular invert at 3.16%, where phase 07 measured abstention as a net loser. |
| 11 | the case set is one project | 202 tests, ~19 distinct failure messages. The effective sample is far smaller than 202. |
| 11 | `divergence_threshold = 0.1` was not derived | It sets D's coverage and therefore D's entire measured advantage. Chosen, not justified. |
| 11 | is the architecture worth keeping? | Three observers were built, three were matched by free alternatives, and fusion adds nothing over one of them. Phase 13 has to answer whether this system should exist in this form. |
| 11 | no arbiter rule was tested against a live model | The forbidden list is enforced by design and by prompt audit, not by an adversarial attempt to get a model to violate it. |
| 12 | **the explanation layer was never built or measured** | `design/12` specifies it in full and nothing implements it. The gate fired on the classification task the SLM would have been distilled for; whether a template-bound explainer helps an engineer at 02:47 is untested. |
| 12 | **"no fine-tune" is scoped to this corpus** | One project, 19 messages, 202 cases. It does **not** mean SLM distillation never helps for CI explanation. Hundreds of distinct, novel-phrased messages would make generalisation a real task and lower TF-IDF's ceiling. |
| 12 | token counts are estimated, not counted | `messages.count_tokens` needs credentials this environment lacks. 2.8 ch/tok is conservative, so input prices are upper bounds — but the estimate may be wrong. |
| 12 | the rate table is cached 2026-06-24 | Cited rather than recalled, and it may have drifted. Every price moves with it. |
| 12 | the prediction that explanations will be unimpressive | `design/12` records it; nothing has generated an explanation to check it against. The stated alarm — explanations that start sounding smart — has never been watched for. |
| 12 | 19 messages may be an artifact of one machine | The dominant signature is a JVM/SSL incompatibility on the host that produced these archives. A different environment might have a far richer message vocabulary, which would change this phase's conclusion. |
| 13 | **the archives are not checksummed** | Zenodo publishes no per-file md5 for the `.tgz` files, so `fetch_archives.sh` verifies only that each is a readable gzip tar. A differing re-download would not be caught. |
| 13 | **some invariants grade recorded artifacts, not live re-runs** | `test_05` asserts Jaccard 1.000 from `infra.json`. A mis-parse that regenerated the artifact is caught; one that left it stale is not. The full re-run is ~55 s and is not wired in. |
| 13 | **`cause_group` is still hand-assigned** | The remedy is now named (double-fault, Q statistic) and cheap, and was not applied. No coupling involving observer 2 has ever been computed. |
| 13 | **the `ExecutionTime` leak is undecidable from this dataset** | The decisive fact — whether it was measured on runs including failures — is a question for the dataset authors, not a computation. |
| 13 | **the explanation layer has never been evaluated** | It is implemented and its invariants hold structurally. Whether it helps an engineer at 02:47, and whether its own alarm (explanations that start sounding smart) ever fires, is untested. |
| 13 | **the append-only evidence store is designed, not built** | Slice 13 specifies it; nothing implements it. Family 4.2 of the register predicts the failure it would prevent. |
| 13 | **Family 3.1 guards a mechanism this corpus never exercised** | Poisoned runs manufactured zero flaky labels here — the 36 truncated runs report no failures. The instrument is untested against a real instance. |
| 13 | **the system does not work** | Three observers matched or beaten by free alternatives; fusion adds nothing; the fine-tune was gated out; the shipped component is a dictionary lookup abstaining on 17.8% of cases. Recorded in every file rather than in none. |

---

## The five that matter most to whoever inherits this

1. **`ExecutionTime` may be partially label-derived, and it is the whole tabular observer.**
   Dropping it takes LOPO AUC 0.6765 → 0.5577. The decisive evidence — whether it was
   measured on runs including failures — is not in the dataset. Pre-registered in
   `experiments/07-execution-time-leak.md` during phase 04, still open.
2. **`cause_group` is hand-assigned, and no coupling involving observer 2 was ever
   computed.** `docs/prior-work.md` names the standard remedy (double-fault measure, Q
   statistic) and records that it was not applied.
3. **The 40/3/1.5 cost numbers are guesses that dominate every result**, and were
   deliberately not revisited, because changing them when the model looks bad is the
   dishonest move.
4. **The explanation layer is designed, minimally implemented, and never evaluated.** Its
   own prediction — that the explanations will be unimpressive, and that sounding smart is
   the alarm — has never been checked.
5. **Everything after phase 05 rests on three projects, and much of it on one.** The
   dominant signal is a single JVM/SSL incompatibility on the host that produced these
   archives.

## What independent work says about all of it

arXiv 2607.09345 reports the same four conclusions this repository reached from scratch —
models matching an always-flaky baseline, collapse under project-disjoint evaluation, data
leakage in published evaluations, and rerun-based label reconstruction changing the result.
See `docs/prior-work.md`. The negative results here are most likely correct rather than an
artifact of a small subset.
