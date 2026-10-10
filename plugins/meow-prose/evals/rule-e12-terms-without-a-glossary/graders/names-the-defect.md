---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: the document introduces more than five terms and gives no glossary near the top (E12).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "the opening, which introduces lane, relay, spool, ticket, shard and quorum with no glossary".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
