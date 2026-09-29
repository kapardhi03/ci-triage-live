# CI flakiness triage

A build goes red at 02:47. One test failed. The change may be broken, the test may be
unreliable, or the machine may have hiccupped — and the report looks identical in each
case. Someone has to decide whether the 09:00 release ships.

This is a system built to make that call, across 14 phases from an empty directory: three
observers, a trust gate, an integration contract, a fusion layer, an LLM arbiter, and an
evidence record behind every verdict.

**It does not work, and that is the result.**

```bash
git clone https://github.com/kapardhi03/ci-triage-live.git
cd ci-triage-live
uv run pytest                              # 121 tests
uv run python -m ci_triage.assemble_knowns # rebuild KNOWNS.md from source
```

---

## The headline

Every component was compared against the cheapest thing that could possibly work. **None of
them won.**

| phase | component built | the free alternative | result |
|---|---|---|---|
| 07 | gradient-boosted tree | `always hold the release` | **tie**, 0.0957 vs 0.0957 h/row |
| 08 | GRU over run histories | `sum()` over a list | **control wins 4–0** |
| 09 | MiniLM retrieval + 5-NN | `if "setSNIServerNames" in text` | **tie**, 0.9851 vs 0.9851 |
| 11 | fusion, four strategies | one decision rule | **identical labels, 202/202** |
| 11 | LLM arbiter (`gpt-4o-mini`) | a stub returning the top voice | **tie**, 0.9904 vs 0.9904 |
| 12 | fine-tuned SLM | TF-IDF + linear | **gated out before the GPU** |

Four components, five free alternatives, zero wins for the trained thing.

## Why — and independent confirmation

The corpus has **~20 distinct failure modes and one dominant cause**. A single JVM/SSL
incompatibility accounts for most of the separable signal, and every method points at it.

After reaching that from scratch, a doubt-first search found
[arXiv 2607.09345](https://arxiv.org/html/2607.09345) reporting **four of the same
conclusions** on different detectors and a different dataset:

| this repo | that paper |
|---|---|
| the GBT ties a constant policy | Flakify and FlakyQ **matched the always-flaky baseline**, F1 0.80 vs 0.80 |
| 0.7621 random → 0.6490 project-held-out | **collapse project-disjoint, recovery under standard CV on identical data** |
| leaking columns found by single-column AUC scan | **data leakage in published evaluations**, F1 0.95 → 0.88 when fixed |
| rerun-based negatives are a budget, not a fact | rebuilt labels from **500 executions**, detectors collapsed |

It names the cause this project only reached as a symptom: *flakiness is not a static
property of test code.*

**The negative results here are most likely correct rather than an artifact of a small
subset.** That is worth more than any positive number in the repository.

---

## Findings

**`not flaky` is not a label. It's a budget, written down as if it were a fact.**
A flip is a witnessed contradiction; no flip proves only that none occurred within N runs.
N reruns buys *"not flakier than roughly 1-in-N"* — a choice about which flip rate you have
agreed to ship. → [`experiments/03-rerun-bias.md`](experiments/03-rerun-bias.md)

**The label you pick decides whether your data is clean.**
Two candidate labels disagree on 904 tests. **763 of 825 rerun-proven flaky tests — 92% —
are invisible to the tool label.** → [`decisions/04-dataset-choice.md`](decisions/04-dataset-choice.md)

**The split is the experiment.** Random 5-fold 0.7621, leave-one-project-out 0.6490 — and
the random split's standard deviation is **ten times tighter**, so it reports a falsely
*stable* number as well as a falsely high one. → [`decisions/06-split-choice.md`](decisions/06-split-choice.md)

**ECE alone selects the useless model.** A base-rate predictor scores **0.000** calibration
error; a perfect ranker scores 0.105. → [`decisions/02-metric-ladder.md`](decisions/02-metric-ladder.md)

**A cost table can make the task degenerate.** At 40:3 asymmetry and a 3.19% base rate the
cost-optimal threshold is **p > 0.930**; the calibrated model's maximum across 25,867 rows
is **0.2362**. It has information and cannot act on it. → [`decisions/07-the-pivot.md`](decisions/07-the-pivot.md)

**Disjoint inputs are not independent evidence.** The three observers share zero columns,
and `ExecutionTime` predicts observer 3's *input* at **AUC 0.6987** — better than observer 1
predicts its own label. → [`docs/architecture.md`](docs/architecture.md)

**The best-looking component was the most dangerous.** The LLM arbiter posts the best
calibration in the table (ECE 0.0096) while trying to move **~23% of cases** toward "flaky"
against real-defect evidence — 44 genuine defects in one run, ~1,760 engineer-hours of
shipped bugs, stopped only by a guard it could not see. **No metric on the ladder detects
this.** → [`experiments/11-fusion-comparison.md`](experiments/11-fusion-comparison.md)

---

## What the mistakes taught

Five checks in this repository were **green while being wrong**, and none was caught by
reading. All were caught by deliberately trying to break something.

| where | the check | why it passed anyway |
|---|---|---|
| phase 02 | cost-asymmetry test | it encoded the same inverted mapping it graded |
| phase 04 | leak guard test | it compared the matrix to the module's own exclusion list |
| phase 08 | keep/throw criterion | unsatisfiable in 3 of 6 cells by arithmetic |
| challenge | arbiter abandonment rule | constrained clamp rate only — a policy that never decided anything passed it |
| experiment 14 | Q statistic | `N01 = 0` makes Q = 1 regardless of dependence |

The pattern: **a check whose reference derives from the thing it checks.** Mutation testing
is therefore part of the method here, not a nicety —
[`tests/test_invariants.py`](tests/test_invariants.py) holds nine instruments for the nine
slices that would otherwise emit a plausible number while broken.

---

## The record

| | |
|---|---|
| **phases** | 14 of 14, plus a challenge extension and three follow-ups |
| **tests** | 121, nine invariants mutation-tested |
| **decisions** | 11, each with what it cost |
| **experiments** | 10, every hypothesis written before its run |
| **AI ledger** | 13 entries, one rejected or narrowed proposal per phase |
| **KNOWNS.md** | **237 established, 82 known-unknowns** |

**Eight predictions were refuted and every one is kept unedited** — phase 03's contamination
magnitude, phase 06's gap size, phase 07's "ECE much better", phase 08's control ranking,
phase 11's arbiter placement and its inverting-rankings claim, the cautious prompt's verdict,
the middle prompt's coverage, and experiment 14's coupling prediction.

The known-unknowns column is longer than is comfortable. A short one would mean the register
was dishonest, not that the system was understood.

## Method

```
decide -> design -> hypothesis -> draft -> review -> patch -> test -> evidence -> record
```

Design precedes code. A hypothesis and an abandonment condition precede every run. **A number
exists only after its command produced it.** Every phase records one AI proposal rejected or
narrowed, with the reason.

| directory | contents |
|---|---|
| [`design/`](design/) | one system slice per phase, written before code |
| [`decisions/`](decisions/) | decisions and what each one cost |
| [`experiments/`](experiments/) | hypotheses written before runs, results appended never edited |
| [`knowns/`](knowns/) | what moved, and what remains unknown |
| [`ai-ledger/`](ai-ledger/) | AI proposals and the review of them |
| [`artifacts/results/`](artifacts/results/) | command-produced results |
| [`FAILURES.md`](FAILURES.md) | how this system *will* fool someone, as a prediction |
| [`docs/prior-work.md`](docs/prior-work.md) | five doubts, five searches, including two that changed nothing |

## Reproducing

```bash
bash scripts/fetch_raw.sh                  # md5-pinned CSVs from Zenodo
bash scripts/fetch_archives.sh             # three project archives, 589 MB
uv run python -m ci_triage.data            # feature matrix + leak guard
uv run python -m ci_triage.evidence        # rebuild frozen inputs, verify hash
uv run python -m ci_triage.arbiter_run     # arbiter + null control (needs OPENAI_API_KEY)
uv run python -m ci_triage.coupling        # observer coupling measures
uv run pytest
```

Raw data is gitignored by design — the command that produces it is what makes the work
reproducible, not a committed CSV.

## Data

FlakeFlagger, Zenodo record 4450723, CC-BY-4.0.
Alshammari, Abdulrahman; Morris, Christopher; Hilton, Michael; Bell, Jonathan.
*Flaky Test Dataset to Accompany "FlakeFlagger: Predicting Flakiness Without Rerunning
Tests."* Zenodo, 2021. DOI: 10.5281/zenodo.4450723.

A larger, broader alternative (IDoFT) has **no licence at all** and was rejected on that
basis — empty is not unrestricted. → [`decisions/04-dataset-choice.md`](decisions/04-dataset-choice.md)

---

Built on the `ci-triage-live` phase framework and harness by Ayush Singh.
The system design, decisions, experiments and findings in this repository are my own.
