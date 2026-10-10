---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: one paragraph holds two ideas and opens with neither (E3).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the paragraph that runs from the log format into the retry policy".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
