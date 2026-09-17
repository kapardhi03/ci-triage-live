# AI ledger — phase 01

## Rejected proposal

**Proposal:** Use accuracy as the evaluation metric, since it's standard and easy to
explain.

**Verdict:** Rejected.

**Reason:** Accuracy treats every mistake as equal. The cost table shows a false "flaky"
(~40h, bug ships) is ~13x costlier than a false "real defect" (~3h, needless hold). The
objective must be cost-weighted expected cost, not raw accuracy. Using accuracy would
implicitly say shipping a bug is as bad as delaying a release, which is the one thing we
know is false.
