---
id: REQ-4600
artifact: requirement
topic: record-writes
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0348
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4600

A change of a record's status that implies an edit to another record MUST be one
command that makes every edit.

Closing a task changes the task, a mark in its epic or defect and, for the last
task, the epic and the decision, and a person who makes them by hand leaves one
of them out.
