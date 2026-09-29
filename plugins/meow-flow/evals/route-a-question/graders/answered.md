---
type: llm
focus: last_message
weight: 1
---

Judge whether the session answered the question.

PASS when the reply names the router's reply fields: size, shape, reason, ambiguous and override words.

FAIL when the reply names fewer than four of them, or reports a route in place of an answer.
