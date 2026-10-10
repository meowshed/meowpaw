---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a table sits at the end with no sentence saying what the reader should take from it (E14).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the table, which follows the paragraph with no sentence saying what it shows".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
