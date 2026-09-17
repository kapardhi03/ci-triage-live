# Phase 01

| Was | Now | Statement | Evidence |
|---|---|---|---|
| unknown | known | four outputs: real defect, flaky, infrastructure, abstain — each triggers a different engineer action | decisions/01-output-space.md |
| unknown | known | ABSTAIN is derived from the case where evidence is too thin to call any of the three causes | decisions/01-output-space.md |
| unknown | known | false "flaky" costs ~40h (bug ships); false "real defect" costs ~3h (needless hold); asymmetry is ~13x | decisions/01-output-space.md |
| unknown | known | ABSTAIN costs ~1.5h — cheap but not free; must sit below wrong-hold or the system won't use it | decisions/01-output-space.md |
| unknown | known | objective is minimize total expected cost, not accuracy | decisions/01-output-space.md |
| unknown | known | accuracy is rejected because it treats every mistake as equal | ai-ledger/01-decision-and-cost.md |
| known-unknown | known-unknown | exact cost numbers are guesses — need real incident data to calibrate | — |
| known-unknown | known-unknown | confidence threshold for ABSTAIN vs. committing to a label — not derived yet | — |
| known-unknown | known-unknown | how to measure whether the system's confidence is trustworthy (calibration) | — |
