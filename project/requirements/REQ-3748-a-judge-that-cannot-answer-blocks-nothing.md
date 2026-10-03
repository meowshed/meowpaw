---
id: REQ-3748
artifact: requirement
topic: prose-and-comments
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0330
source: the repository owner's request, and BUG-1230
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3748

Where the judge can't be started, can't be reached, runs out of time or
answers outside the schema the gate asks for, the gate MUST let the publish
through with a report that the judged rules were not checked.

A judgement that didn't happen is unresolved, never passed, so the gate says
so. It doesn't block, because blocking every publish on a missing part teaches
people to uninstall the gate (ADR-1600).
