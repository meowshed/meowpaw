---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: long words where a common short word is exact (D3).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "We will remediate the substantial latency and utilise a commence-on-demand strategy.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
