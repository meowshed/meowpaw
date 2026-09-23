---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'pointer fragment'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "It runs on the current storage layer. Section 8.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
