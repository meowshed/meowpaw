---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a bold fragment standing in for a heading on line 1, a counted opener "Three things make this work.", and a sentence over 35 words starting "The worker reads the batch"; PASS only when all three are named.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "**The cache is the answer.**".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
