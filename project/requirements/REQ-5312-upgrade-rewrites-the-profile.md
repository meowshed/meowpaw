---
id: REQ-5312
artifact: requirement
topic: upgrade
class: functional
status: approved
revised: 2026-10-31
elaborates: RES-0369
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-5312

The upgrade MUST remove the retired step from the gates a profile declares.

A profile that names a step that no longer exists declares a gate nothing holds.
