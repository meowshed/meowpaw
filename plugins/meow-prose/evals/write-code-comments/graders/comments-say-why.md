---
type: llm
focus: last_message
weight: 2
---

Judge the comments added to the function.

PASS when the sleep carries a comment giving its reason (the store's replication lag), and no comment restates what its line already says, such as "increment the count" or "pop a batch from the queue".

FAIL when any comment restates its line, or when the sleep has no comment giving the reason.
