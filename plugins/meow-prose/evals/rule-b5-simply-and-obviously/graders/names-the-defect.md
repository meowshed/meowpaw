---
type: llm
focus: last_message
weight: 1
---

Judge whether the review names this defect: words that tell a struggling reader the fault is theirs: simply, just, obviously (B5).

PASS when a finding at fix or improve level points at this span, or at the sentence holding it, and names the rule or the pattern: "Simply add the key, and obviously the build will just work.".

FAIL when no finding points at it, or when the review rewrites the text instead of reporting findings.
