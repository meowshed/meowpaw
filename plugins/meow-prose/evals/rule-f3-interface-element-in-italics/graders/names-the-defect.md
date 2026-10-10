---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a button and a command shown as plain text where bold and code font belong (F3).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Press Save and then run mise run all.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
