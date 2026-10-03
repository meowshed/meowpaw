---
id: REQ-3746
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

# REQ-3746

A judged finding MUST block only where a program has confirmed that its span
occurs verbatim in the command.

The model that found the span can't be trusted to check it, because BUG-1230's
model quoted a bold line and an idiom the text didn't hold. REQ-3183 states
what a span must be, and this states who checks it.
