---
type: llm
focus:
  source: file
  path: project/adrs/ADR-0100-cache-in-redis.md
weight: 2
---

Judge the record as the session left it.

PASS when it carries a section headed "Open review findings" holding at least
one finding with the reason it was left open, such as the owner having fixed
the Decision section's wording, and the Decision section is unchanged.

FAIL when no such section exists, when it lists no finding or no reason, or
when the Decision section was changed.
