# CI flakiness triage

A build goes red at 02:47. One test failed. The change may be broken, the test may be
unreliable, or the machine may have hiccupped — and the report looks identical in each
case. This is the system that helps decide whether to stop the release.

Built from an empty `ci_triage/` directory across 14 phases: rules, tabular, sequence and
retrieval observers, a fusion layer, an arbiter, and an evidence record for every verdict.
Every design decision, its cost, and the alternatives rejected are recorded in the repo.

```bash
git clone https://github.com/kapardhi03/ci-triage.git
cd ci-triage
uv run pytest
```

## Where it stands

| Phase | Slice | Status |
|---|---|---|
| 00 | system boundary — what is inside, what is outside, who acts | done |
| 01 | external contract — four outputs and the cost of each mistake | done |
| 02 | evaluation component — separate from every model, on purpose | done |
| 03 | ground-truth source — provenance and what refreshes it | done |
| 04 | ingestion — source to feature matrix, and where the leak guard sits | done |
| 05 | trust gate — which runs may contribute evidence at all | in progress |
| 06–13 | splits, three observers, fusion, explanation, operations | ahead |

Current data: **26,134 rows, 825 positives (3.16%), 25 projects, 21 features**, from
FlakeFlagger (Zenodo 4450723, CC-BY-4.0).

## Findings so far

**The licence gate is a real gate.** The larger, broader, more convenient dataset (IDoFT)
has no licence at all — no `LICENSE`, no badge, only a citation request. Empty is not
unrestricted: copyright is automatic, so absent a licence the default is all rights
reserved, and GitHub's ToS grants view and fork within GitHub and nothing more. Rejected on
licensing, not on data quality. → [`decisions/04-dataset-choice.md`](decisions/04-dataset-choice.md)

**The label you pick decides whether your data is clean.** Two candidate labels disagree on
904 tests. `IsFlaky` (rerun-observed, 825 positives) versus `flaky` (tool-labelled, 205):
**763 of 825 rerun-proven flaky tests — 92% — are invisible to the tool label.** Choosing
the other column would have buried 92% of true positives in the negative class.

**`not flaky` is not a label. It's a budget, written down as if it were a fact.** A flip is
a witnessed contradiction and proves flakiness; no flip proves only that none occurred
within N runs. N reruns buys "not flakier than roughly 1-in-N", which is a choice about
which flip rate you have agreed to ship. → [`experiments/03-rerun-bias.md`](experiments/03-rerun-bias.md)

**A hypothesis of mine was partly refuted and is kept unedited.** I argued the negative
class would be materially contaminated. N turned out to be 10,000 — derived from
`NumFailingRuns + NumPassingRuns`, not taken on trust — so a hidden flake must flip rarer
than about 1-in-3,000 to survive. The argument was right but belonged to the other column.
→ [`EXPERIMENTS.md`](EXPERIMENTS.md)

**ECE alone selects the useless model.** A model predicting the base rate for every case
scores a perfect 0.000 calibration error; a perfect ranker scores 0.105. Calibration is a
diagnostic, never a selection criterion. → [`decisions/02-metric-ladder.md`](decisions/02-metric-ladder.md)

**A leak test can grade itself circularly.** The first version compared the feature matrix
against the module's own exclusion list, so deleting an entry made both sides agree and the
test still passed. Caught by mutation testing, not by review.
→ [`ai-ledger/04-data-and-licence.md`](ai-ledger/04-data-and-licence.md)

## How the work is organised

```
decide -> design -> hypothesis -> draft -> review -> patch -> test -> evidence -> record
```

Design precedes code. A hypothesis precedes every experiment. A number exists only after
its command ran. Every phase records one AI proposal rejected or narrowed, with the reason.

| Directory | Contents |
|---|---|
| `design/` | one system slice per phase, written before code |
| `ci_triage/` | implementation |
| `tests/` | invariants that fail when the logic is wrong |
| `decisions/` | decisions and their costs |
| `experiments/` | hypotheses written before runs |
| `knowns/` | supported conclusions and remaining uncertainty |
| `ai-ledger/` | AI proposals and the review of them |
| `artifacts/results/` | command-produced results |
| `scripts/` | reproducible data fetch, checksum-pinned |

```bash
uv run lab.py status          # current work
uv run lab.py check 05        # verify a phase's required artifacts exist
uv run pytest                 # invariants
```

Progress is measured by files on disk, not by claimed results.

## Data

FlakeFlagger, Zenodo record 4450723, CC-BY-4.0.
Alshammari, Abdulrahman; Morris, Christopher; Hilton, Michael; Bell, Jonathan.
*Flaky Test Dataset to Accompany "FlakeFlagger: Predicting Flakiness Without Rerunning
Tests."* Zenodo, 2021. DOI: 10.5281/zenodo.4450723.

Fetch with `scripts/fetch_raw.sh` (md5-pinned). Raw data is gitignored by design — the
command that produces it is what makes the work reproducible, not a committed CSV.

---

Built on the `ci-triage-live` phase framework and harness by Ayush Singh.
The system design, decisions, experiments and findings in this repository are my own.
