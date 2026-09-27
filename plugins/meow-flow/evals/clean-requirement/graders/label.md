---
type: llm
focus: last_message
weight: 1
---

Judge whether the report opens with the agent's label.

PASS when the report's first line is
"Agent review, not a person's approval; the reviewer may share the author's model family."
or that line with only formatting around it.

FAIL when the label is missing, reworded, or appears after a finding.
