---
type: llm
focus: last_message
weight: 2
---

Judge acronyms and times in the summary.

PASS when every acronym other than widely read ones such as API, URL or CPU is expanded on first use (ETL and SLA each expanded at least once), and every date and time is written one way, such as 2026-09-23 and 02:10 CET, with no mix of "2:10 am" and "02:10".

FAIL when ETL or SLA appears without its expansion, or dates and times appear in more than one format.
