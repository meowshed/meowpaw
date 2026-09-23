---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'importance promised instead of given'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Two details of that result are worth reading closely. The retry already".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
