# Phase 08

Scope: 3 projects with archives (`kevinsawicki-http-request`, `square-okhttp`,
`tootallnate-java-websocket`), project-grouped split, 3 folds. Not comparable to
`precomputed/sequence-eval.json` (17 projects) or to phase 06/07 numbers.

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | predicting `IsFlaky` from a full run sequence is **circular** — the label is *"does this list contain both a 0 and a 1"*, computable by regex, AUC 1.0 by construction | experiments/08-heuristic-control.md |
| unknown | known | **`IsFlaky` conflates two phenomena**: `P P F P F P` (non-determinism) and `F F F F P P P P` (broken then fixed) both satisfy it; only the arrangement separates them | ai-ledger/08-sequence-observer.md |
| unknown | known | "interleaved vs blocked" is **also circular** as a task — the label is a function of the sequence fed in | experiments/08-heuristic-control.md |
| unknown | known | prefix-predicts-suffix is circularity-free and answers an actionable question: *given this history, will the test flip going forward?* | design/08-sequence-observer.md |
| unknown | known | **the control — a `sum()` over the prefix — scores 1.0000 on kevinsawicki at both prefix lengths and 0.9992 on tootallnate/2000**; mean 0.9296 at k=2000 | artifacts/results/sequence.json |
| unknown | known | the control sits at **exactly chance (0.4967)** on okhttp/200, the only cell where anything was at stake | artifacts/results/sequence.json |
| unknown | known | **the GRU never beats the control: 0 wins, 2 ties, 4 losses** across six cells | artifacts/results/sequence.json |
| unknown | known | the pre-registered criterion required 0.5467 on okhttp/200; the model scored **0.4975**. **Withdrawn** | experiments/08-heuristic-control.md |
| unknown | known | in the decision cell the control's 95% CI is **[0.4647, 0.5331]** — contains 0.5. **Neither predictor beats chance there** | artifacts/results/sequence.json |
| unknown | known | a calibrated AUC of 0.5000 with **`n_distinct` = 1** means the model collapsed to a constant, not that it ranks at chance — AUC alone cannot tell them apart | artifacts/results/sequence.json |
| unknown | known | the GRU's raw AUC on kevinsawicki/200 is **0.0000** — perfectly inverted, not random; monotonic calibration flattened it to a constant rather than un-inverting it | artifacts/results/sequence.json |
| unknown | known | observer 2's inputs are **disjoint** from observer 1's — zero shared columns — but disjoint inputs are not independent evidence | design/08-sequence-observer.md |
| assumed | known | a keep/throw criterion can itself be circular: "beat the control by 0.05 in every cell" was unsatisfiable in 3 of 6 cells by arithmetic | ai-ledger/08-sequence-observer.md |
| unknown | known | the same structural flaw — a check whose reference derives from the thing it checks — has now appeared **three times** (phases 04, 07, 08), caught each time only by trying to break it | ai-ledger/08-sequence-observer.md |

## Predictions, checked

| Prediction | Outcome |
|---|---|
| criterion: model ≥ 0.5467 on okhttp/200 | **fired against the model** — 0.4975. Withdrawn as committed. |
| (implicit) the control would be strong | **understated** — it is at ceiling on 2 of 3 projects |

Kept unedited.

## Open

| Statement | Why it is still open |
|---|---|
| **the label-conflation defect is unmeasured** | How many `IsFlaky=1` tests are broken-then-fixed rather than non-deterministic? Never counted. Rejected as a task because it is circular; still a real defect in the ground truth. Carry to phase 13. |
| 3 projects is a very thin base | Two of three are at ceiling for the control, so the comparison rests almost entirely on okhttp. A fourth project could change the summary. |
| nothing predicts okhttp/200 | Neither control nor model beats chance. Whether the first 200 runs genuinely carry no signal, or whether a different representation would find some, is untested. |
| the GRU was barely tuned | hidden=16, 30 epochs, one seed. A stronger model might win — but it would have to beat a free `sum()`, and it lost by 0.24–0.50 in four cells. |
| are observers 1 and 2 independent? | Inputs are disjoint, which is necessary and not sufficient. Phase 10's question, now with one observer withdrawn. |
| two observers, two withdrawals | Phase 07's tabular observer cannot beat a constant; phase 08's sequence observer cannot beat a `sum()`. Whether anything survives for phase 11 to fuse is genuinely open. |
