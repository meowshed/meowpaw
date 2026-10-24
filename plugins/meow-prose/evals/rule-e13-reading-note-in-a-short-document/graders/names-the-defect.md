---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a note on how to read the document sits at the top of a document of about 200 words (E13).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the "How to read this document" section".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
