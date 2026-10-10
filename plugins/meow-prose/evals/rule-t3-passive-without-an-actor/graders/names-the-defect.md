---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the passive voice, which hides who acts (T3).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The file is read, the checksum is computed and the result is sent.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
