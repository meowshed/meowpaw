---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'that pointing at a whole sentence'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "A stub carries a name and a type, and no content. That allows one process to".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
