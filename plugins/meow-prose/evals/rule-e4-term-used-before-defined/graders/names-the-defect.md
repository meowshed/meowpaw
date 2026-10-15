---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a term used before it is defined or glossed (E4).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the first use of "tombstone" with no gloss".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
