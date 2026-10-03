---
id: REQ-3744
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

# REQ-3744

The gate MUST block on a judged finding only where two independent judgements
of the same text name the same rule and the same span.

A span that is in the text can still be judged wrongly: BUG-1230's case 2,
reproduced, blocked once in three runs on `in depth`, a phrase the body holds
and the list doesn't. Agreement between two judgements is how RES-0330 steadies
a model's answer, and it is the reversal condition ADR-1600 names.
