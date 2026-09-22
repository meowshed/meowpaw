---
id: REQ-1428
artifact: requirement
topic: safety
class: non-functional
status: withdrawn
revised: 2026-09-22
elaborates: RES-0031
verification: static
---

# REQ-1428

**Withdrawn. Replaced by REQ-1429.**

It read: the harness MUST NOT modify files outside the repository except its
own run state.

It forbade writing the record where the repository keeps it, once a repository
could keep its record in another repository or a folder outside its tree
(REQ-0521). Its reason, protecting files that belong to somebody else, holds
for everything except that declared location, so the replacement keeps the rule
and names the one further exception.
