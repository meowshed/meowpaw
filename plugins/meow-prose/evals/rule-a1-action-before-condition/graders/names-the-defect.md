---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the action comes before its condition, so a reader may act before reaching the condition (A1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Drop the request if validation fails.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
