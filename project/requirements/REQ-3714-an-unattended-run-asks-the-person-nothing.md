---
id: REQ-3714
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3714

An unattended run MUST decide each approval gate and each clarifying question itself, against the written principles, without asking the person anything.

The owner chose this on 2026-10-03: a run that stops for a person isn't unattended, so the person reads the run's report afterwards in place of answering during it. REQ-2380 says what the decision is made against, and REQ-2386 lists what the run couldn't do.
