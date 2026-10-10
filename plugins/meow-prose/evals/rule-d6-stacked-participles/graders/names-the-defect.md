---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: a sentence that stacks -ing clauses (D6).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Running the check, comparing the output, noting each difference and updating the record, the script finishes by sending the report, closing the file and exiting.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
