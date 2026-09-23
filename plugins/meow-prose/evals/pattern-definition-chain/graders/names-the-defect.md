---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'definition chain'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "A check is a pass, and it blocks nothing.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
