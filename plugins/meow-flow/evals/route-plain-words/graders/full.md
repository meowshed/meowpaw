---
type: llm
focus: last_message
weight: 2
---

Judge whether the router routed the request full.

PASS when the reply gives the size `full` for the request.

FAIL when the reply gives `none` or `reduced`, gives no size, or lists the request as several changes.
