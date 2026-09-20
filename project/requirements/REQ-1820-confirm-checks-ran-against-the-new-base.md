---
id: REQ-1820
artifact: requirement
topic: stacked-changes
class: functional
status: approved
revised: 2026-09-20
unit: U-0001
elaborates: RES-0065
verification: behavioural
---

# REQ-1820

After any change to a pull request's base, the harness MUST confirm that the
required checks have run against the new base, and MUST report them as not run
where they have not.
