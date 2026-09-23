---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'bold standing in for structure'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "**A migration of this kind demands close reading, and it disturbs little".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
