---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the same fact said twice in one paragraph (T5).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The cache expires entries after ten minutes. After ten minutes, an entry in the cache is expired.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
