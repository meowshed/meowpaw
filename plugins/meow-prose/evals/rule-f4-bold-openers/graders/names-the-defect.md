---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: bold phrases that open every paragraph of a short section (F4).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the three bold openers in the section".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
