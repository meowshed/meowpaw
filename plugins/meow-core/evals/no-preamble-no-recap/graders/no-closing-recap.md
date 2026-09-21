---
type: llm
focus: last_message
weight: 1
---

PASS when the reply answers and stops: the last sentence carries information,
or names a next step.

FAIL when the last sentence summarises what the reply just said, restates the
difference a second time as a conclusion, or offers further help.
