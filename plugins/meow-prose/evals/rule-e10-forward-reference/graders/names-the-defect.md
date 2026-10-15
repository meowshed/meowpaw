---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the main path refers forward to a later section for something the reader needs now (E10).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: ""section 7 explains why"".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
