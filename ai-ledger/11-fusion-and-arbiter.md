# AI ledger — phase 11

## Rejected proposal

**Proposal:** Report D as the winning fusion strategy. It tops both rankings — accuracy
0.9940 against 0.9554, ECE 0.0071 against 0.0435 — and escalating on disagreement is the
architecturally sensible design.

**Verdict:** Rejected.

**Reason:** On D's own covered 166 cases, **A, B and C also score 0.9940**. D's entire
advantage is which cases it declines, not how it decides them, and it declines exactly the
36 where the lookup has no entry. Reporting it as a winner would credit a coverage choice as
a decision-quality improvement.

The builder's pre-registration required coverage beside accuracy precisely so this could not
pass, and their own refutation condition 3 named it before the run.

## Narrowed proposal

**Proposal:** Rank E last, or interpolate its position from the four strategies that ran.
Leaving a gap in the table looks unfinished.

**Verdict:** Rejected outright, not narrowed.

**Reason:** TASK is explicit that an unavailable strategy is an unranked result, not evidence
it won or lost. `precomputed/fusion-comparison.json` exists and would have filled the row
with real numbers from the 17-project reference build — which is exactly the substitution
that makes a comparison meaningless. E is `incomplete`, its predicted position is recorded,
and the prediction will never be checked. That is the honest shape of the result.

## The builder's committed claim, refuted

> *"The two rankings nearly invert. C tops accuracy and bottoms calibration, B mirrors it.
> Report both metrics; a single scoreboard is dishonest here."*

**Refuted.** A, B and C tie on accuracy to four decimals, so there is no ordering to invert.
D tops both rankings and A is second in both — they agree. B, predicted best on calibration,
came last.

Kept unedited. The instinct behind it — that accuracy and calibration can disagree and a
single number can hide which one picked the winner — is sound and was worth committing to;
it simply does not hold on this data. The related instinct *did* pay off: requiring coverage
beside accuracy is what exposed D.

## What the phase actually found

Four strategies, **one decision rule**. A, B and C emit identical labels on 202/202 cases;
they differ only in the probability they attach, which is why their ECE separates and their
accuracy cannot.

Fusion had nothing to fuse:

- the tabular observer's **maximum probability over all 202 cases is 0.1609**, so it cannot
  move any decision at a 0.5 cutoff;
- slice 10 collapses it with the lookup (shared `ssl-jvm`), so fusion runs over **two voices,
  never three** — 166 records de-duplicated, lookup winning the collapse 161 times.

Two voices, one inert. The three-observer architecture reduces, on this data, to the phase 09
lookup with an abstention rule bolted on.

## A consequence of phase 10 worth stating plainly

The `cause_group` collapse is working exactly as designed and its cost is now visible: it
removes an entire observer from the fusion. That is correct — the coupling was measured at
AUC 0.6987 — and it means the architecture's headline claim of three independent observers
was never true on this data. Phase 10 recorded the contract as "correct machinery around
components whose individual value is unproven"; phase 11 shows the machinery working and
finding almost nothing to operate on.

## Not done

No arbiter call was made and no arbiter result is claimed. The prompt is rendered, printed in
full, and audited against the forbidden-to-see list — the label, test name, class name,
project and other strategies' outputs are all absent — but nothing consumed it.

---

## Extension (2026-09-29): the arbiter ran

### Rejected proposal

**Proposal:** Report E as the best strategy in the table. Accuracy 0.9904 and ECE 0.0096 are
second only to D on accuracy and the best calibration of any completed strategy, on the same
frozen 202 cases with the same metric implementation. It earned its place.

**Verdict:** Rejected. **Withdrawn**, on two pre-registered grounds.

**Reason:** Those numbers are produced by a component that tried to move **49 of 202 cases**
toward FLAKY against REAL_DEFECT evidence. **44 of those 49 were genuine real defects** —
unclamped, roughly **1,760 engineer-hours** of shipped bugs at the phase 01 price, on 202
cases. The only thing that stopped it was a guard it could not see.

And on its own covered set it is **exactly tied** with a free stub: 0.9904 against 0.9904 on
the same 104 cases. It adds nothing and costs a safety mechanism.

Reporting it as the winner would have been the single worst act of this project, because
every metric on the phase 02 ladder agrees it is excellent.

### What the clamp rate caught that nothing else could

The abandonment condition was written before the run:

> *"Accuracy could look healthy while the model systematically pushes toward the expensive
> error, and nothing in the accuracy number would show it."*

Measured: the model's raw distribution was **`AGREE_FLAKY` 121, `ESCALATE` 49,
`AGREE_REAL_DEFECT` 32**. It wants to say flaky. No metric in this repository sees that —
accuracy cannot, ECE cannot, Brier cannot, cost-weighted risk cannot, because the clamp had
already converted the unsafe calls into abstentions before scoring.

**The instrument existed only because the rule was written down first.** That is the
strongest single argument this project has produced for hypothesis-before-evidence.

### A reproducibility failure found in passing

The phase 11 observer probabilities existed **only in a session scratchpad**. They were gone
when this extension started, and `.ci-lab/interviews/13.md` had claimed *"every number in
`artifacts/results/` was produced by a command in the repository"* — true of the committed
artifacts, false of the inputs that produced the fusion comparison.

Fixed by `ci_triage/evidence.py`, which rebuilds them from `data/raw/` and verifies the
frozen hash. It reproduces `305d8ece8a0fa240` exactly, so the phase 11 result is now
regenerable rather than asserted. The claim in the interview was wrong when written and is
corrected here rather than edited there.

### Ponytail pass

Removed from the first draft: a `Arbiter` class holding client, model and stats (replaced by
three functions and a dict); a retry/backoff wrapper (the SDK retries, and a failure should
surface as `incomplete` rather than be papered over); a `--model` CLI flag with no second
user; and a separate prompt-template file (the renderer is twelve lines and belongs beside
the thing it serves).

Kept deliberately: the `stats` dict threaded through, because the clamp count is a **reported
result** and not merely instrumentation — hiding it inside the function would have hidden the
finding.
