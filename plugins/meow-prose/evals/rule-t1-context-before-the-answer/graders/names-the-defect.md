---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the change comes last, after the context (T1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the opening that gives the history before the change".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
