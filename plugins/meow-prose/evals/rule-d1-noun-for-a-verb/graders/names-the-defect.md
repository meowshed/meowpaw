---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: an action buried in nouns where a verb would carry it (D1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Invalidation of the cache occurs on modification of the record.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
