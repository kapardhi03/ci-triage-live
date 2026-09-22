# Slice 04 — ingestion layer

## Responsibility
Turn the three licence-cleared source CSVs into one feature matrix that cannot contain a
column derived from the label.

## Reads
Only `data/raw/{test_features,test_results,Project_Info}.csv`, fetched and checksum-verified
by `scripts/fetch_raw.sh` from Zenodo record 4450723 (CC-BY-4.0). Nothing else. No network
access at import time, no second dataset, no hand-edited file.

## Emits
`(X, y, groups, manifest)`:

- `X` — the feature matrix, every column of which survived the exclusion policy below.
- `y` — `IsFlaky` from `test_results`, the rerun-observed label chosen in
  decisions/04-dataset-choice.md.
- `groups` — the project name per row, so phase 06 can hold out whole projects.
- `manifest` — what was dropped and why: every excluded column with its reason code, the
  join key, the row counts before and after, and the source checksums. A consumer that
  cannot see what was removed cannot audit the removal.

## Refuses
It refuses to return a feature matrix containing any column on the exclusion list. That is
not a warning and not a filter applied on request — the matrix is never constructed with
those columns present.

It refuses to emit a row whose label is unknown: tests present in `test_features` but not
in the joined `test_results` have no rerun outcome, and a row with no `IsFlaky` is dropped
rather than defaulted to `0`. Defaulting an absent label to the majority class would
manufacture negatives, which is the phase 03 error committed deliberately.

It refuses to run if a source checksum does not match the recorded value.

## Constraint
**No column derived from the label may reach the feature matrix.**

The guard cannot live in a step someone remembers to call — that step gets skipped. It
lives inside the *only* function that returns features, applied after every merge and
rename, so there is no code path that produces `X` without passing through it. A column
added later by any means is denied by default: the matrix is built from an allowlist of
columns that survived, never by subtracting a blocklist from whatever happened to arrive.

The exclusion list, with reasons:

| Column(s) | Reason code | Why |
|---|---|---|
| `FirstFailingRunID` | `label_derived` | AUC 1.000 alone — exists only if the test failed |
| `UniqueFailingExceptionTypes` | `label_derived` | AUC 0.998 — failure bookkeeping |
| `NumFailingRuns`, `NumPassingRuns` | `label_derived` | `IsFlaky` is literally `both > 0` |
| `FirstPassingRunID` | `label_derived` | same rerun bookkeeping family |
| `flaky` | `alternate_label` | the tool label — a label, not a feature |
| `flaky_source` | `label_derived` | non-null exactly when `flaky` is 1 |
| `hIndex...window5`, `...window10` | `project_constant` | ≥80% of rows equal their project's modal value; a project identifier in numeric costume, and phase 06 holds out whole projects |
| `test_name`, `project`, `testClassName`, `testMethodName`, `` | `identifier` | join keys and row index, not features |

The six surviving `hIndex...` columns are kept deliberately and at a price: they require
git history that this dataset does not ship (`Project_Info.csv` is 24 rows of URL + SHA,
one revision each). **Keeping them adds a git-history dependency to the phase 00 system
boundary.** Recorded here so that phase 06 can revisit it if the held-out-project gap
stays large.

## Connects to
Depends on slice 03 (ground-truth source — `IsFlaky` is the rerun-observed label, and its
provenance travels in `manifest`). Consumed by slice 05 (trust gate), slice 06 (splits —
via `groups`), and every observer from slice 07 onward. Its constraint is enforced by
`tests/test_data.py`, which must fail if any excluded column reappears in `X`.
