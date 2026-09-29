---
id: REQ-0266
artifact: requirement
topic: the-method
class: functional
status: withdrawn
revised: 2026-09-29
elaborates: RES-0055, RES-0012
verification: behavioural
---

# REQ-0266

**Withdrawn by ADR-2300. Replaced by REQ-3646 and REQ-3648.**

It read: a decomposition MUST carry a coverage check: every requirement the authorising record addresses lands in exactly one task or is explicitly deferred with a reason.

ADR-2300 lets a task or an epic close any number of requirements and a requirement be closed by any number of them, so a requirement landing in two tasks is no longer a finding; REQ-3646 keeps the part that every addressed requirement lands somewhere.
