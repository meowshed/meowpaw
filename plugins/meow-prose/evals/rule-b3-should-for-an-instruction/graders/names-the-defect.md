---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: an instruction written as "you should" and "you can", which makes the step sound optional (B3).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "You should set the timeout to 30 seconds, and you can then restart the worker.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
