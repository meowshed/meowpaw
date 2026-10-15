---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a sentence that adds nothing the reader lacks (I1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "The importer is an important part of the system and plays a role in how data enters it.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
