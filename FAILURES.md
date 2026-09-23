# Failure register

**Written as a prediction, 2026-09-23.** How this system *will* fool someone, not how it
already did. Three failures that already happened appear only as evidence that the class is
real, clearly marked `ALREADY HAPPENED`; everything else is forecast.

Each entry: the failure, **how it looks from the outside** (which is always plausible — that
is what makes it a failure rather than a bug), and **the instrument** that catches it.

---

## Family 1 — the system lies about its performance

### 1.1 A number is quoted without its split

**Failure.** Someone reports **0.7569** — the random-split AUC — because it is the larger
number and the split is in a different file.

**From the outside:** a healthy-looking result in a slide, an issue comment, a README. There
is no error. The number is real; it answers a question nobody is asking, because deployment
sees unseen projects.

**Instrument:** every result file carries `split` and `scope` fields, and
`tests/test_invariants.py::test_06_zero_positive_folds_are_skipped_not_scored` asserts the
LOPO fold accounting. A number without a split is a number that cannot be located in
`artifacts/results/`.

### 1.2 A strategy is credited for declining the hard cases

**Failure.** Escalate-on-disagreement reports 0.9940 against 0.9554 and is written up as the
best fusion strategy.

**From the outside:** a clean win on both accuracy and calibration. Nothing looks wrong.

**ALREADY HAPPENED** — phase 11. On D's own covered 166 cases, A, B and C **also** score
0.9940. The entire advantage was which cases it declined.

**Instrument:** `test_09_accuracy_is_never_reported_without_coverage`. Accuracy without
coverage is not a comparable number, and the invariant refuses a results file that omits it.

### 1.3 An unavailable component is ranked last instead of unranked

**Failure.** The LLM arbiter could not run, so it appears at the bottom of the table — or
worse, `precomputed/fusion-comparison.json` fills the row with numbers from a different
corpus.

**From the outside:** a complete table. Every row populated. The reader concludes the LLM
performed worst, which was never measured.

**Instrument:** `test_08_the_decision_cell_criterion_fired_against_the_model` and the
`incomplete` status in `fusion.json`. A strategy that did not complete on every frozen case
is excluded from the ranking, not placed in it.

---

## Family 2 — the calibrator collapses

### 2.1 Calibration collapses to a constant and reports AUC 0.5

**Failure.** The calibration mapping degenerates and emits one value for every input.

**From the outside:** **AUC exactly 0.500**, which reads as "ranks at chance" — an
unremarkable, believable result.

**ALREADY HAPPENED** — phase 08, `kevinsawicki`/200: calibrated AUC 0.5000 with
`n_distinct_calibrated = 1`. The model had no ranking at all. Its raw AUC was **0.0000** —
perfectly inverted, not random — and monotonic calibration flattened it rather than
un-inverting it.

**Instrument:** every calibrated result reports `n_distinct` beside AUC. AUC 0.5 with
`n_distinct = 1` is a collapse; with `n_distinct = 150` it is genuine chance ranking, and
AUC alone cannot distinguish them.

### 2.2 An uncalibrated score is combined with a calibrated one

**Failure.** Two observers' probabilities are averaged when one means "80% of these turn out
flaky" and the other means "this scored 0.8 on something."

**From the outside:** a fused probability in the usual range. Perfectly plausible.

**Instrument:** `Evidence` raises `UncalibratedProbabilityError` when `probability` is set
and `calibrated` is `None`, and a fused probability inherits the weakest calibration status
of its inputs. Mutation-tested: making the flag optional fails two tests.

### 2.3 Calibration is fitted on the projects it is applied to

**Failure.** The mapping is fitted across all projects, then applied to a held-out one.

**From the outside:** ECE improves. The improvement is real and does not transfer.

**Instrument:** `test_06_no_project_spans_a_grouped_split`, plus
`test_qualifier_is_fitted_without_the_held_out_project` — a qualifier fitted on everything
cannot detect the held-out project as alien, and the test asserts the honest one scores lower.

---

## Family 3 — infrastructure contaminates the result

### 3.1 A poisoned run manufactures flaky labels

**Failure.** A build that never compiled reports the whole suite as failing; under
`IsFlaky = both > 0` every clean test in it acquires a flaky label.

**From the outside:** a larger positive class. Better class balance. *Easier* modelling.

**Instrument:** the slice 05 gate, and
`test_05_gate_deterministic_set_matches_ground_truth` freezing the cross-check at Jaccard
1.000. **Note the honest limit:** this did **not** happen in this corpus — the 36 truncated
runs report zero failures and manufactured nothing. The instrument guards a mechanism this
subset never exercised, so it is untested against a real instance.

### 3.2 One environmental cause is counted as three observers

**Failure.** Observers agree because one JVM/SSL incompatibility drives all their inputs;
averaging their confidence makes the system more certain on the basis of nothing new.

**From the outside:** unanimous agreement, high confidence. The most convincing possible
output.

**Instrument:** `cause_group` collapse before aggregation, and
`test_11_correlated_agreement_cannot_inflate_confidence` — five correlated records give the
same answer as two. **Known deficiency:** the grouping is hand-assigned, and no coupling
involving observer 2 was ever computed. `docs/prior-work.md` names the remedy (double-fault
measure, Q statistic) and records that it was not applied.

### 3.3 The archive silently stops being representative

**Failure.** Run archives cover a contiguous prefix or suffix of run IDs rather than a random
sample, so the "trusted runs" are a systematic subset.

**From the outside:** nothing. Counts look right.

**ALREADY OBSERVED (benign):** `kevinsawicki` archives cover run IDs 2095–9999 with no gaps —
the ~2,095 missing runs are a contiguous prefix, not scattered loss.

**Instrument:** `infra.json` records run-id ranges and full row accounting (469 dropped
unmapped, 8 case-folding collisions, 485 feature rows unjoined). A manifest that does not
account for every row is the symptom.

---

## Family 4 — it breaks in operation

### 4.1 The lookup silently ages out

**Failure.** The shipped `MessageLookup` has no entry for a new failure signature. Coverage
decays from 82.2% as the codebase changes.

**From the outside:** precision **stays high** — it is measured only on covered cases. The
system looks stable while answering less and less.

**Instrument:** coverage is reported with every accuracy, and unseen messages return
`ABSTAIN` rather than a guess. Monitor the **abstention rate**, not the precision; precision
is the metric that will not move.

### 4.2 The evidence store is rewritten

**Failure.** A verdict's record is edited after the fact — to correct a bug, tidy a format,
or make a retrospective consistent.

**From the outside:** a clean, coherent history. This is exactly what a covered-up failure
looks like.

**Instrument:** the evidence store is **append-only** by design (slice 13). A system that can
rewrite its own history cannot be audited, and the failures in this register are precisely
the ones an edit would hide.

### 4.3 An invariant is skipped and read as passed

**Failure.** A test skips because an artifact is missing, and the suite reports green.

**From the outside:** all tests pass.

**Instrument:** slice 13 refuses to pass an invariant it could not evaluate — `_artifact()`
raises `pytest.skip` with the message *"a skip is not a pass."* This is the phase 03 error
(absence of evidence read as evidence) in the operations layer, and it would be the worst
place to repeat it.

### 4.4 A test is written that cannot fail

**Failure.** A check grades code against a number that code computed, or a criterion is
adopted whose margin exceeds the available headroom.

**From the outside:** a green test. Indistinguishable from a working one.

**ALREADY HAPPENED, THREE TIMES** — the inverted cost mapping (slice 02, five phases green,
and the test encoded the same misreading); the circular leak test (slice 04, green whether
the guard worked or not); the unsatisfiable keep criterion (slice 08, would have dropped the
model by arithmetic in 3 of 6 cells).

**None was caught by a passing test. All three were caught by deliberately trying to break
something.**

**Instrument:** every frozen constant in `tests/test_invariants.py` is hardcoded in that
file, independent of the module it grades; and mutation runs are part of the method rather
than a nicety. This is the failure family most likely to recur, because a green tick is the
most persuasive object in the repository.
