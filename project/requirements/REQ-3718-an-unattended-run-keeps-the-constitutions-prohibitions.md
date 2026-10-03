---
id: REQ-3718
artifact: requirement
topic: unattended-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0074
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3718

An unattended run MUST keep every prohibition the constitution states, including that it merges only after the gate has passed.

A prohibition is a rule and not a question to a person, so taking the person out of the run doesn't lift it: the run still never touches secret material, never credits an AI, never commits to the trunk directly and never merges past a failing gate.
