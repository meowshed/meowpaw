---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: an example that can't run as pasted: it uses a variable it never sets and has no prerequisites (G2).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the code block, which uses $TOKEN without setting it".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
