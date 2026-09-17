# Decision 01 — output space

## The three-output starting point

Three causes, three outputs: real defect, flaky, infrastructure.

## The case that forced a fourth

At 2:47am the system sees a test that has failed a couple of times before (not enough to
call flaky), logs look normal (can't call infrastructure), and the code diff touches
something nearby but not directly (can't confidently call real defect). The evidence is
genuinely ambiguous.

Forcing one of the three means guessing. A guess of "flaky" risks shipping a real bug
(~40h cost). A guess of "real defect" delays the release for nothing (~3h). Both are worse
than admitting the evidence is thin.

## The fourth output: ABSTAIN

ABSTAIN means "the evidence isn't strong enough for me to call this — here's what I see,
you decide." The engineer's action on ABSTAIN is: rerun, quick infra check, review
history, then make the call themselves. Cost: ~1.5h.

ABSTAIN earns its place because:
- it triggers a different action than the other three
- its cost (~1.5h) sits below wrong-hold (~3h) and far below wrong-ship (~40h)
- if it cost more than holding, the system would never use it

## Cost table (engineer-hours, all guesses)

| True cause | System output | What happens | Cost |
|---|---|---|---|
| any | correct confident call | just worked | ~0h |
| real defect | flaky (wrong) | bug ships to customers | ~40h |
| flaky | real defect (wrong) | hold and investigate for nothing | ~3h |
| any | abstain | engineer investigates manually | ~1.5h |

Properties:
- **Asymmetric**: false "flaky" is ~13x costlier than false "real defect."
- **ABSTAIN is cheap, not free**: real work at 2:47am, but the cheapest wrong-ish outcome.

## Objective

Minimize total expected cost: the sum of each outcome's frequency times its cost from the
table. Not accuracy — accuracy treats every mistake as equal, but a false "flaky" is ~13x
costlier than a false "real defect."
