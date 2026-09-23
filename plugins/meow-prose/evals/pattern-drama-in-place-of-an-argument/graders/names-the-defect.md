---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'drama in place of an argument'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Read that paragraph against section 3 and the overlap is uncomfortable.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
