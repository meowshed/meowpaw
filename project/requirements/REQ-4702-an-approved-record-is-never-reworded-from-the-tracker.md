---
id: REQ-4702
artifact: requirement
topic: tracker-sync
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0349
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4702

A synchronisation MUST NOT write a title or body from the tracker into an
approved record, and MUST report the difference.

The issue's state still flows to the record (REQ-1353 is replaced by this and
REQ-4700).
