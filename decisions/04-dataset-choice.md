# Phase 04 — Dataset choice

Date: 2026-09-22
Phase gate: (1) may we use this data? (2) can it answer the question from phases 01–03?
Status: gate (1) cleared and recorded below before any bytes were placed in `data/raw/`.

## Decision

Use **FlakeFlagger** (Zenodo record 4450723). Reject **IDoFT** for now on licensing
grounds, not on data quality.

## Candidates considered

| Dataset | Source | Scope | Licence |
|---|---|---|---|
| FlakeFlagger | Zenodo record 4450723 (DOI 10.5281/zenodo.4450723) | ~24 Java/Maven projects, rerun-based flaky labels + engineered features | **CC-BY-4.0** (stated on record) |
| IDoFT (International Dataset of Flaky Tests) | GitHub `TestingResearchIllinois/idoft` + mir.cs.illinois.edu/flakytests | 300+ Java & Python projects, actively maintained | **None found** (see below) |

## Licence findings

### FlakeFlagger — CC-BY-4.0 (explicit)
- The Zenodo record's Rights section states: Creative Commons Attribution 4.0 International.
- Source: https://zenodo.org/records/4450723 (Rights section).
- Obligation: attribution. On redistribution or reuse (including commercial use and
  use as training data) we must credit the creators, link the licence, and indicate if
  changes were made. No other restriction blocks use inside a commercial triage model.

### IDoFT — no licence found (the "empty" case)
Checked three places a licence would appear; none present:
- Repo root file list — no `LICENSE`/`LICENSE.md`. Source: https://github.com/TestingResearchIllinois/idoft
- GitHub "About" sidebar — Resources lists only "Readme"; no licence badge (GitHub
  auto-surfaces a licence when a `LICENSE` file exists; none shown).
- `readme.md` — an Acknowledgments section requests citation (BibTeX provided) but grants
  no permission to copy, redistribute, or build on the data. A citation request is not a licence.

**Empty ≠ unrestricted.** Copyright is automatic (Berne Convention; US and India both follow
it). No licence means no permission has been granted, i.e. the default is "all rights
reserved" by the author, not public domain. GitHub's Terms of Service only grant other GitHub
users the right to view and fork within GitHub; they do not grant reuse in a downstream product
or as training data. There is a genuine but murky wrinkle — raw facts are not copyrightable and
a factual compilation gets only "thin" protection (Feist v. Rural, US) — but IDoFT's curated
selection/arrangement is exactly what thin protection can attach to, other jurisdictions protect
databases more strongly (EU sui generis database right), and none of it is settled enough to be
the foundation of a company. Not legal advice; the safe engineering default is: unlicensed =
off-limits until a documented "yes."

Path to make IDoFT usable later (not done yet): email the author (testflaky@gmail.com, listed
in the readme) for explicit permission/licence, and/or open an issue asking them to add a
`LICENSE` file. Revisit only if a phase needs its breadth and a documented grant exists.

## Attribution (to carry with the data through the pipeline)

> Data: Alshammari, Abdulrahman; Morris, Christopher; Hilton, Michael; Bell, Jonathan.
> "Flaky Test Dataset to Accompany 'FlakeFlagger: Predicting Flakiness Without Rerunning
> Tests'." Zenodo, 2021. DOI: 10.5281/zenodo.4450723. Licensed CC-BY-4.0
> (https://creativecommons.org/licenses/by/4.0/). Used unmodified except where noted in
> downstream processing.

## Provenance — what landed in `data/raw/`

Retrieved: 2026-09-22, from Zenodo record 4450723.
Only the three CSVs were pulled (~10 MB). The per-project `.tgz` rerun-log archives
(~6.5 GB) were deliberately NOT downloaded; phase 08 will pull three specific projects.

| File | Bytes | md5 | sha256 |
|---|---|---|---|
| Project_Info.csv | 1738 | 5b3392a4f7367b2a566b919a98989a97 | f0064b25ed64995842465b67c6fec86b5ddf72d30e1a7dc5b64abd8b0208e9fd |
| test_features.csv | 6870159 | 63306c05fafcc6446911ab7000f85ae0 | 52cd97a1796972754a19d967df8c813805c3ee8f40d78370b2bbf503cf3b8c00 |
| test_results.csv | 3516114 | fcd2674ab42068de627ec6afce4f6d1a | 86210ed8ac0171a3d64cf5ab83d503cc97e82845e0299b9f55599a8414218f13 |

md5s match the values published on the Zenodo record. Reproduce with `scripts/fetch_raw.sh`.

## Data shape (raw, as downloaded) — read before phase 05

The three raw CSVs do NOT agree on flaky counts or project counts. This is a labelling
decision to make deliberately in phase 05, not a download error.

- `test_results.csv` — 26,765 rows, 28 projects. `IsFlaky` = 828 flaky / 25,937 non-flaky.
  This is the rerun ground truth: NumFailingRuns / NumPassingRuns across the 10,000 reruns.
- `test_features.csv` — 26,619 rows, 27 projects. `flaky` = 205 flaky / 26,414 non-flaky,
  with `flaky_source` in {NA, IDFlakies (184), DeFlaker (21)}. This label comes from prior
  detection tools, not from the reruns.
- `Project_Info.csv` — 24 projects (URL, SHA), the studied revisions.
- (For reference, the pre-processed `processed_data.csv` circulated separately has 22,236
  rows, 24 projects, 811 flaky — i.e. the rerun-based label after merge/feature filtering.)

Open question for the second gate: which label is "flaky" for our purpose — rerun-observed
(`test_results.IsFlaky`, 828) or tool-labelled (`test_features.flaky`, 205)? The two files also
join on different keys (`test_features`: test_name/project/class/method; `test_results`:
Project + Test). The choice changes the positive class by ~4x, so it must be settled and
recorded before any model is trained.
