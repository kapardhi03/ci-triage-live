# Problem

At 02:47 a release-branch build goes red. The on-call release engineer has to decide
what happens to the 09:00 release: ship it, hold it, or investigate to determine which.

The call has to be made now, not at 09:00. We can't hold the release the moment it goes
red, because the failure might not be real. And we can't just leave it till morning
either, because if the failure is real, fixing it and getting back to a verified green
build takes hours, and there aren't many hours between 02:47 and ship.

Three different causes produce the same red build:

1. The code change broke something (real defect).
2. The test is unreliable (flaky).
3. The machine hiccupped (infrastructure).

The CI report is identical in all three cases.

There are two ways to be wrong, and they don't cost the same:

- Ship a real bug: a broken release reaches customers. High cost, hard to undo.
- Hold a good release: burned night, slipped deadline. Real cost, but internal and
  recoverable.

Shipping a broken release is worse. When it's unclear, accept the internal cost of
holding rather than risk the customer-facing failure.
