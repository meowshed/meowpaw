---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'a long sentence and a short punchline'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The dashboard shows the result of the last run that completed. Sometimes no".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
