---
id: REQ-3716
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3716

An unattended run MUST push its branch, open its pull request, merge it once the pull request's checks pass and run the declared release command, each on its own decision, listing each of these actions in its report as a harness decision.

The owner chose on 2026-10-03 that unattended mode works fully without a person, so it lands and releases its own work. Listing each action is what lets the person audit afterwards what nobody approved at the time (REQ-2384). Replaces REQ-2374.
