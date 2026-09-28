---
id: REQ-0820
artifact: requirement
topic: delegation
class: functional
status: withdrawn
revised: 2026-09-28
elaborates: RES-0016, RES-0263
verification: behavioural
---

# REQ-0820

**Withdrawn by ADR-1700. Replaced by REQ-3270 and REQ-3271.**

It read: the harness MUST set the nesting depth for delegation to one, rather
than instruct an agent not to delegate further.

RES-0284 found that the depth is a variable only the user's or the
repository's settings can set, because a plugin's own settings keep only two
keys, so a harness shipped as plugins can't meet the obligation as written.
REQ-3270 withholds the delegation tool from every agent the harness ships, so
none can delegate further, and REQ-3271 keeps the session's depth of one for
when a plugin can set it.
