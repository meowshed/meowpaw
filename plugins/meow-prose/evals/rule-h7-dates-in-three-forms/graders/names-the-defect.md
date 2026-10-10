---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: dates and numbers written in three ways in one text (H7).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "9/18/26, 18 September 2026 and 2026-09-18".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
