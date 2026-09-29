---
type: llm
focus: last_message
weight: 2
---

Judge whether the reply marks the route ambiguous and names the evidence on each side.

PASS when the reply says ambiguous, or `ambiguous: yes`, and names what points to the smaller size and what points to the larger one.

FAIL when the reply says `ambiguous: no`, omits the field, or names the evidence for one side only.
