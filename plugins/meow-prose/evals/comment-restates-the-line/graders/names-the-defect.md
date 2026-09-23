---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the code comment "# increment the counter by one" restates the line below it (G1); the second comment gives a reason and is fine.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "# increment the counter by one".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
