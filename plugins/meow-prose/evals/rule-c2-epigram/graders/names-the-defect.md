---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a claim written as a proverb, with its reason left out (C2).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "A cache is a promise you keep until you can't.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
