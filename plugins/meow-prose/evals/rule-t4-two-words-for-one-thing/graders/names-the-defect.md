---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: one thing called a job, a task and a unit of work in one paragraph (T4).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "job, task and unit of work".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
