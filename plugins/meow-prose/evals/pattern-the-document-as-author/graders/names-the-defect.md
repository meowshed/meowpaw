---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the pattern 'the document as author'.

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "These notes therefore say "the importer" and reserve "the loader" for the".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
