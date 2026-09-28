---
id: REQ-3210
artifact: requirement
topic: the-method
class: functional
status: approved
revised: 2026-09-27
elaborates: RES-0075
verification: behavioural
---

# REQ-3210

The implement step MUST NOT modify, delete, skip or weaken a check the cover
step wrote.

An implementing agent that edits a failing check is indistinguishable from one
cheating it, which is how agents most often pass tests they can't satisfy.
