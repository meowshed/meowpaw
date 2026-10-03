---
id: REQ-3722
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3722

An unattended run MUST release only with the release command the profile declares, so it releases nothing in a repository that declares none.

A guessed release command publishes something nobody chose to publish, and a published release can't be taken back, so the run reports the release as unresolved where the profile is silent.
