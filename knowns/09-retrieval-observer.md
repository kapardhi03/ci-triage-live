# Phase 09

Scope: `square-okhttp` only — the one project with both classes (102 deterministic, 100
flaky). Not comparable to `precomputed/retrieval-eval.json` (17 projects).

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | retrieval keeps what weights discard: at 3.16% positives the gradient is dominated by the majority class and rare cases average into the noise floor; an index compresses nothing | decisions/09-index-contents.md |
| unknown | known | MiniLM embeddings + 5-NN score **0.9851** against a **0.5050** majority baseline, leave-one-class-out | artifacts/results/retrieval.json |
| unknown | known | **a single substring check scores 0.9851 — identical to four decimals** | artifacts/results/retrieval.json |
| unknown | known | TF-IDF char-ngrams + 5-NN also score 0.9851; exact-message lookup scores **0.9940** where it matches | artifacts/results/retrieval.json |
| unknown | known | **100 of 102 deterministic tests share one failure message** (`NoSuchMethodError: setSNIServerNames`) | artifacts/results/retrieval.json |
| unknown | known | the corpus holds **19 distinct messages across 202 tests** — the effective sample size is ~19, not 202 | artifacts/results/retrieval.json |
| unknown | known | the same message appears under **both** labels: one flaky test shares the deterministic cluster's text | decisions/09-index-contents.md |
| unknown | known | **the shipped component is `MessageLookup`**: 82.2% coverage, **0.9940 precision on covered**, 36 abstentions | artifacts/results/retrieval.json |
| unknown | known | abstaining on an unseen message removes the stateful-dependency problem entirely — the table is the state, and no stale neighbour is silently returned | ai-ledger/09-retrieval-observer.md |
| unknown | known | indexing the test/class name would leak: every `HttpOverSpdy3Test.*` is deterministic, so class membership recovers the label without reading the failure | decisions/09-index-contents.md |
| unknown | known | a single-class index makes precision@k **1.0 by construction**; the observer refuses rather than warns | tests/test_retrieval.py::test_single_class_index_is_refused |
| unknown | known | without the self-exclusion guard a query retrieves **itself at distance 0** with its own label | tests/test_retrieval.py::test_without_the_guard_the_query_does_retrieve_itself |
| unknown | known | **cross-project retrieval is not performable in either direction** and is recorded unscored | artifacts/results/retrieval.json |
| unknown | known | **three phases, three free alternatives, zero wins for the trained component** (07 tie, 08 loss, 09 tie) | ai-ledger/09-retrieval-observer.md |

## Open

| Statement | Why it is still open |
|---|---|
| **is 0.9851 a result about flakiness, or about one broken JVM?** | The dominant signal is a single `NoSuchMethodError` from an SSL/JVM incompatibility on the machine that produced these archives. It separates deterministic from flaky here; whether it generalises to any other environment is untested and probably not. |
| effective sample size ~19 | 202 tests are ~19 opinions. Confidence intervals computed over 202 would be badly overstated, and none were reported for that reason. |
| one project | `kevinsawicki` and `tootallnate` have no deterministic tests at all, so nothing cross-project can be measured. A fourth project with both classes would change what is claimable. |
| the 36 abstentions | 17.8% of tests have no message precedent. Whether that fraction is stable, or an artifact of holding out whole classes, is unmeasured. |
| observers are all redundant with something free | Three for three. Whether phase 11 has anything to fuse is now a serious question rather than a formality. |
| is the failure text independent evidence? | Inputs are disjoint from observers 1 and 2, but the dominant message reflects one environmental cause that may also drive `ExecutionTime`. Phase 10's question. |
