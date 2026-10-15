---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a commit subject that describes the process and carries two ideas (S1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Ran the tests, fixed the lint and updated the plan".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
