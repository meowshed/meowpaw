---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: one sentence of about fifty words that a reader loses in the middle (C1).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "When the importer reads a file whose header names a column that the schema no longer holds, because an earlier release dropped it and the exporter on the other side was never updated, it stops with an error that names the column but not the file, which sends the operator searching.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
