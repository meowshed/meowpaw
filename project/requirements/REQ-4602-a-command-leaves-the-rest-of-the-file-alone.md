---
id: REQ-4602
artifact: requirement
topic: record-writes
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0348
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4602

A command that writes a record MUST change only the lines it owns, and its
result MUST pass `paw check` without the command.

A hand edit stays valid, so the record is read and written with an editor and
without the tool (REQ-0030).
