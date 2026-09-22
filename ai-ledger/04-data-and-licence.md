# AI ledger — phase 04

## Rejected proposal

**Proposal:** Use IDoFT instead of FlakeFlagger. It is larger (300+ projects vs ~25), spans
Java and Python rather than Java alone, is actively maintained, and is directly on topic.
On data quality it is the better dataset.

**Verdict:** Rejected, on licensing grounds, not data grounds.

**Reason:** Checked three places a licence would appear — repo root file list, GitHub's
About sidebar, and the readme. No `LICENSE` file, no licence badge, nothing but a citation
request. **Empty is not unrestricted.** Copyright is automatic, so absent a licence the
default is all rights reserved. GitHub's Terms of Service grant other GitHub users the
right to view and fork within GitHub and nothing beyond that; publishing publicly is not a
grant to reuse the data in a product or as training input. A citation request is a courtesy,
not a licence. Raw facts are not copyrightable and a factual compilation gets only thin
protection, but curated selection and arrangement is exactly what thin protection attaches
to, other jurisdictions protect databases more strongly, and none of it is settled enough
to build on.

FlakeFlagger says yes in writing (CC-BY-4.0). IDoFT says nothing, and nothing is a no.
Full reasoning and the path to revisit it in decisions/04-dataset-choice.md.

## Narrowed proposal

**Proposal (mine):** For the history features, "keep only the wide windows — 500 and 10000 —
and drop the narrow ones that are project-constants."

**Verdict:** Narrowed, after the measurement contradicted it.

**Reason:** The premise was that project-constancy decreases monotonically with window
size. It does not. Measured within-project variance: `window75` 84.9% and `window100` 85.9%
both exceed `window500` at 65.6%. "Wide = better" was intuition presented as a finding, and
the cutoff I picked was arbitrary.

Replaced with a rule derived from the data: **drop any history column where ≥80% of rows
equal their project's modal value.** That drops `window5` (89.0%, 1.8 distinct values per
project) and `window10` (83.3%), and keeps six. The 80% threshold is still a chosen number
— there is no natural break in the gradient — but it is written down and therefore
arguable, which the original was not.

## Alternatives the builder rejected

- **Drop all 8 history columns.** Rejected. They are the second-strongest signal group in
  the dataset (AUC 0.58–0.65, behind only `ExecutionTime` at 0.76) and dropping them costs
  real predictive power. *No further reason recorded — the rejection was stated without
  one, and the tie-break between the remaining two options was delegated to me. Recorded
  as delegated rather than reasoned, so phase 06 knows how much weight it carries.*
- **Keep all 8.** Rejected in favour of the filtered version, for the phase 06 reason: a
  feature constant within a project is a project identifier in numeric costume, and phase
  06 holds out whole projects.

**Cost accepted either way:** both surviving options keep history features, which require
git history the dataset does not ship (`Project_Info.csv` is 24 rows of URL + SHA, one
revision each). **A git-history dependency is therefore added to the phase 00 system
boundary.** This is not a middle road on deployability; it is a bill to be paid later.

## Gap found in review

The first version of `test_no_excluded_column_reaches_the_feature_matrix` was **circular**:
it graded `X.columns` against `EXCLUDED`, so deleting an entry from `EXCLUDED` made both
sides agree and the test still passed. Mutation testing caught it — un-excluding
`flaky_source` left all 8 tests green.

The behavioural AUC leak detector could not cover the gap either, because choosing
`IsFlaky` as the label made `flaky_source` a weak predictor (AUC 0.535). It is excluded on
availability grounds, not correlation: at 02:47 on an unseen project nobody has run
IDFlakies, so a model leaning on it cannot be deployed. Same reasoning as the history
columns.

Fixed by freezing `MUST_NEVER_APPEAR` inside `tests/test_data.py`, independent of the
module it grades. Defeating it now requires editing the test, which is a reviewable act
rather than an accident. All five mutations are killed.

Second bug, in the manifest rather than the guard: `unmapped_result_projects` was computed
after the unmapped rows had already been dropped, so it reported `[]` while 3 projects and
469 rows had in fact been discarded. An audit record that reports a clean join it did not
perform is worse than no audit record. Fixed; every row is now accounted for.
