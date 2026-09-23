---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'absence as the subject'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The client caches answers, and nothing tells it when one stops being true.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
