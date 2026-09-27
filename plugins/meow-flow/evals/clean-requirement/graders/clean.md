---
type: llm
focus: last_message
weight: 2
---

Judge whether the report calls the requirement clean.

The requirement carries one obligation, states its reason, stands alone, is
testable by a behavioural check, and cites the research it elaborates.

PASS when the report says the requirement is clean, or reports only findings
it marks as preferences.

FAIL when the report marks any finding as a fix, or invents a missing section
or field.
