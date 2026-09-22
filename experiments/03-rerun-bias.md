# Experiment 03 — rerun bias in the label set

No data has been loaded. This is a prior claim, written before phase 04 opens the file, so
that it can be checked rather than remembered favourably.

## The claim

**The label noise in this dataset is one-directional. The positive class is essentially
uncontaminated; the negative class contains an unknown number of genuinely flaky tests
that the rerun budget was too small to catch. There is no mechanism that produces the
reverse error.**

Someone could disagree with this. The claim is falsifiable, and the refutation conditions
are below.

### Why the direction is one-way

A `flaky` label required witnessing a pass and a fail on identical code. A clean,
deterministic test cannot produce that evidence, so it cannot acquire the label. There is
no path from "not flaky" to a spurious `flaky` mark.

A `not flaky` label required only that N runs elapsed without a flip. A genuinely flaky
test whose flip rate is below ~1/N acquires this label routinely. That path is wide open
and nothing closes it.

### Who is hiding in the negative class

Rare flakes, specifically. The contamination is not random across the negative class — it
is concentrated in tests whose flip rate sits just under the detection floor the budget
bought. Frequent flakes were caught; rare ones were not. The hidden positives are
systematically the *hard* cases.

## What this does to the metric ladder from phase 02

The bias has a known direction, so the metrics are not merely noisy. They are biased
predictably, which makes them **bounds** rather than estimates:

| Metric | Effect of contamination | Correct reading |
|---|---|---|
| **precision** | some scored false positives are hidden real flakes | **lower bound** — true precision ≥ measured |
| **recall** | denominator holds only flakes that flipped *easily* | **overestimate** — graded on the easy subset |

They lean in opposite directions, and which way each leans is known.

Consequence: a model that looks mediocre against this label set may be doing better than it
appears, and tuning it into agreement with the negatives is tuning it to reproduce the
labelling procedure's blind spot.

## The constraint carried into lab 05

**A false positive is a candidate, not a verdict.**

When the model scores a row `flaky` and the CSV says `not flaky`, that disagreement is not
automatically the model's error. It is a claim about the label, and it gets sampled and
reran before it is counted against the model.

**Corollary (holds until those reruns are actually done):** precision over the
un-reran set is reported as a lower bound, never as a point value. The bound is what stands
while the budget is unspent; option 2 is the procedure for converting it into a real number
row by row.

### Why this beats the alternatives

Restating precision as a bound only *caveats* data already in hand. Dropping the negative
class from model selection discards ~97% of the rows to avoid a contamination that is
probably a few percent of that class — a wild over-correction that leaves almost nothing to
train on.

Targeted reruns **generate new information**, and they are the only affordable version of
the fix. Rerunning the whole corpus at N = 15,000 costs ~$60,000 and ~5,200 days of serial
CI. Rerunning the few hundred rows where the model disagrees costs almost nothing, and
those rows are the ones most enriched for hidden flakes — the same disagreement that
depresses measured precision is what concentrates them.

The model cannot be trusted because the labels are bad. The model is also the cheapest
instrument for finding which labels are bad. That loop is the answer to "there is no
solution for this."

## Predictions, recorded before the data is opened

1. The positive rate in the published labels will be low — I expect **under 10%**.
2. The true flaky rate is **higher** than the published positive rate. Direction stated now;
   magnitude unknown.
3. Rerunning a sample of model-flagged false positives at high N will flip a
   **materially higher** fraction than rerunning an equal-sized random sample of
   `not flaky` rows.

## What would support the claim

Prediction 3 holds: model-flagged false positives flip at a rate clearly above the random
`not flaky` baseline. That is direct evidence that hidden positives exist, that they sit in
the negative class, and that the model finds them.

## What would abandon it

Any of the following, and the claim above gets rewritten rather than quietly softened:

- **Model-flagged FPs flip at the same rate as random `not flaky` rows.** The negative class
  may still be contaminated, but the model is not a usable instrument for finding it, and
  the lab-05 constraint loses its justification.
- **Neither group flips at all at high N.** Contamination is negligible at any budget
  reachable here, and the negative class can be treated as clean in practice.
- **Recorded N turns out to be very large** (phase 04). The detection floor is then far
  below any flip rate that matters operationally, and the concern shrinks to a footnote.
- **Evidence of a reverse-direction error** — any mechanism by which a deterministic test
  acquires a `flaky` label, such as labels merged across differing commits or environments.
  That would break the one-way claim outright.

## Open unknown blocking everything above

**N is not known.** Every number in this file is conditional on it. Phase 04 must find the
recorded rerun count, and if it is unrecorded, that absence is itself the finding.
