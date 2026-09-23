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
