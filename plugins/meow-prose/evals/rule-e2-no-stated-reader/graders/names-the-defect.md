---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the document never says who reads it or at what level (E2).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the opening, which names no reader and no level".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
