---
type: llm
focus: last_message
weight: 2
---

Each of the five questions blocks a safe release: ownership of the retry
budget, a migration tested on 2% of the data, in-flight jobs at cut-over, a
rollback script never run, and an unchecked alert threshold.

PASS when the reply keeps all five, or keeps fewer and explicitly names each
one it left out, so the person can see what was set aside.

FAIL when the reply returns two or three questions and the others disappear
without being named.
