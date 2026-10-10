---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: "may" and "should" used where the meaning, permission or obligation, is unclear (H4).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The client may retry and should wait.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
