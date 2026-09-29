---
type: llm
focus: last_message
weight: 2
---

Judge whether the Agent call's result, as the session printed it, is marked as
stopped at the agent's turn ceiling.

PASS when the printed result carries a marking the platform wrote, such as a
note that the agent reached its maximum turns, its turn limit or `maxTurns`,
or that the result is partial.

FAIL when the printed result lists the numbers with no such marking, or when
the session reports the agent finished.
