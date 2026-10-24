---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the warning arrives after the step it protects (A2).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Run `rm -rf data/cache`. This deletes every cached report, and the next build takes an hour to refill it.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
