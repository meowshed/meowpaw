---
id: REQ-1150
artifact: requirement
topic: prompt-format
class: functional
status: approved
revised: 2026-09-23
elaborates: RES-0272
verification: evaluation
---

# REQ-1150

How often a unit that has to be in context before the model acts is loaded
MUST be measured on each model it serves, on requests that should load it and
on near misses that should not, including answers in chat.

One description loaded the writing skill in 45 of 50 writing runs on Opus 5.5
and in 0 of 30 on Sonnet 5, so a result on one model says nothing about the
other. A wording that loads a unit more often is only better if the near misses
stay unloaded.
