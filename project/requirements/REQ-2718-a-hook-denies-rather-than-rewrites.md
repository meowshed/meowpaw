---
id: REQ-2718
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: behavioural
---

# REQ-2718

The harness MUST NOT rewrite a tool's input from a hook, and MUST deny with a
reason instead, so the change is visible and is redone deliberately.
