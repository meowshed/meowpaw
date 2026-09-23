---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'a person where the reader is you'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "A person makes a series of changes, reads the whole diff, and then decides.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
