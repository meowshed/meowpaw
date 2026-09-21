---
id: REQ-2210
artifact: requirement
topic: public-repository
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0066
verification: behavioural
---

# REQ-2210

Every commit reaching the trunk MUST leave it building with its checks
passing, because whoever bisects a later problem will land on whichever one
does not.
