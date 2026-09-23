# Slice 11 — decision layer

## Responsibility
Turn the collapsed evidence for one test into one verdict, and decide when no rule should
decide.

## Reads
`Evidence` records **after** slice 10 has collapsed them by `cause_group`. Never raw
observer output, because un-collapsed records let one physical cause vote twice — the
coupling measured in phase 10 at AUC 0.6987.

It reads no features, no archives, no failure text and no label. If it could read those it
would be a fourth observer, and the independence slice 10 enforces would be its own to
violate.

## Emits
A fused verdict plus the strategy that produced it, the divergence between the observers,
the coverage if the strategy abstains, and the `calibrated` status of the probability it
returns. A fused probability inherits the weakest calibration status of its inputs — mixing
one calibrated and one uncalibrated observer produces an uncalibrated result, and saying
otherwise would launder the uncertainty.

## Refuses
It refuses to fuse records that slice 10 has not collapsed.

It refuses to report unanimity between observers that are not distinct. Three records from
one `cause_group` agreeing is one opinion; reporting it as consensus is the false-consensus
failure, and it is the thing `tests/test_fusion.py` exists to catch.

It refuses to rank a strategy that did not complete on every frozen case. A strategy that
times out, exceeds budget or cannot run is `incomplete` — an unranked result, not a loss and
not a win.

## Constraint
**Agreement may only raise confidence when the agreeing observers are distinct**, and **no
strategy may be ranked on a case set different from the one its competitors ran on.**

The case list is frozen and hashed (`sha256[:16] = 305d8ece8a0fa240`, 202 cases). A ranking
computed over different cases, different labels, or a different metric implementation is not
a comparison.

## The arbiter: what it may not see, and what it may not do

Both halves, because an arbiter with no forbidden actions can silently overrule the one
component whose numbers are trustworthy.

**Forbidden to see:**
- the label, under any framing;
- the other strategies' outputs — otherwise it is ranking, not arbitrating;
- the test name, class name or project — phase 09 showed class membership alone recovers the
  label, so identity in the prompt is a leak wearing a different hat;
- anything that would let it recompute an observer's input from scratch, which would make it
  a fourth observer whose correlation with the other three is unmeasured.

**Forbidden to do:**
- **manufacture a probability.** It arbitrates between existing ones. A number it invents has
  no calibration, no provenance and no error bar, and slice 10 would have to mark it
  uncalibrated anyway;
- **move a case toward SHIP.** It may escalate toward HOLD or ABSTAIN and never the reverse.
  Under the phase 01 table a wrong "flaky" costs ~40h against ~3h for a needless hold, so an
  arbiter that can only add caution has a bounded worst case and one that can relax caution
  does not;
- **overrule a calibrated observer with an uncalibrated judgement.** Where a calibrated
  probability exists it stands, and the arbiter may add caution around it, not replace it;
- **cite evidence absent from the record.** Anything it says must be traceable to an
  `Evidence` record, or slice 12's explanation layer would be explaining something that did
  not happen.

## Connects to
Depends on slice 10 (collapsed evidence, the contract, the case/run level split), slice 01
(four outputs, cost table) and slice 02 (all metrics). Consumed by slice 12 (explanation)
and slice 13 (operations). It does not consume observers directly.

## Scope
The comparison runs on 202 `square-okhttp` cases at a **49.5%** base rate, because that is
the set all three observers can speak about. Deployment sees **3.16%**. Whichever strategy
wins here is flattered relative to deployment, and that is recorded beside every number
rather than discovered later.
