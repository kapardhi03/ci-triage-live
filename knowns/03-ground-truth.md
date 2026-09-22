# Phase 03

No data has been loaded. Every entry below is an argument or an open question, not a
measurement — the evidence column says so explicitly where that is the case.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| assumed | known | no human judged these tests; every label is the output of a rerun procedure | decisions/03-label-procedure.md |
| unknown | known | `flaky` means a pass and a fail were witnessed on identical code — a proof | decisions/03-label-procedure.md |
| unknown | known | `not flaky` means N runs elapsed without a flip — absence of evidence at a sample size, not a property of the test | decisions/03-label-procedure.md |
| unknown | known | the label error is **one-directional**: a deterministic test cannot acquire a `flaky` mark, so contamination runs only into the negative class | experiments/03-rerun-bias.md |
| unknown | known | N reruns buys "not flakier than ~1-in-N", never "not flaky" — P(catch) = 1-(1-p)^N | decisions/03-label-procedure.md |
| unknown | known | at N=100, a genuine 1-in-500 race is mislabelled `not flaky` ~82% of the time | decisions/03-label-procedure.md (arithmetic, not measurement) |
| unknown | known | the hidden positives are systematically the **rare** flakes — frequent ones were caught, so the contamination sits in the hard cases | experiments/03-rerun-bias.md |
| unknown | known | certifying 1-in-500 across a 25-project corpus ≈ $2,000; certifying 1-in-5,000 ≈ $60,000 and ~5,200 days serial CI | decisions/03-label-procedure.md (costed on stated guesses) |
| unknown | known | no finite N finishes the job — every budget buys a threshold, never a proof; and the label is stale on the next commit | decisions/03-label-procedure.md |
| unknown | known | measured **precision is a lower bound**; measured **recall is an overestimate** (denominator holds only easily-caught flakes) — biased in opposite, known directions | experiments/03-rerun-bias.md |
| unknown | known | constraint carried into lab 05: **a false positive is a candidate, not a verdict** — FPs are sampled and reran before counting against a model | experiments/03-rerun-bias.md |
| unknown | known | model FPs are the cheapest search instrument for bad labels; the model that cannot be trusted is also how the labels get fixed | experiments/03-rerun-bias.md |
| unknown | known | dropping the negative class from selection was rejected — ~97% of rows discarded to avoid a few-percent error | ai-ledger/03-ground-truth.md |
| **known-unknown** | **known-unknown** | **N is not known.** Every number in this phase is conditional on it. Phase 04 must find the recorded rerun count; if unrecorded, that absence is the finding | decisions/03-label-procedure.md |
| known-unknown | known-unknown | the true flaky rate is higher than the published positive rate — direction predicted, magnitude unknown | experiments/03-rerun-bias.md |
| known-unknown | known-unknown | whether model-flagged FPs flip more often than random `not flaky` rows — the claim's main refutation condition, untested | experiments/03-rerun-bias.md |
| known-unknown | known-unknown | whether any reverse-direction error exists (labels merged across differing commits or environments) — would break the one-way claim | experiments/03-rerun-bias.md |
| known-unknown | known-unknown | the dataset's licence — not checked; phase 04 is a hard gate before any row is loaded | labs/04-data-and-licence/ |
