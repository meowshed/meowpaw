---
id: REQ-3702
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3702

Each iteration MUST receive the same frozen prompt and the path of the run's progress file from the program that holds the loop, and take its progress from the progress file and the record, never from the conversation.

Inside one session no iteration starts from the same context, because the conversation grows and compaction summarises it, so the same stated input is what a program can still give every iteration (RES-0320, conclusions 3 to 5). Replaces REQ-0880.
