---
id: REQ-4700
artifact: requirement
topic: tracker-sync
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0349
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4700

A synchronisation MUST apply the change of the one side that changed since the
last synchronisation, and MUST apply the record's where both sides changed.

A tracker keeps one time for a whole issue and the record keeps none, so the
sides are told apart by a fingerprint of each at the last synchronisation
(RES-0349).
