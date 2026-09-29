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
none can delegate further, and REQ-3271 asks for the session's depth of one,
postponed until a plugin can set it.

## Open review findings

- The reviewer asked, as a preference, for the reason a setting beats an
  instruction in the quoted rule. I left it, because the rule is withdrawn and
  the quotation keeps its original wording.
- The reviewer noted that ADR-2200 still cites REQ-0820 as the reason a
  subagent can't dispatch another. I left ADR-2200 as it is, because it is
  approved and frozen; REQ-3270 now carries that obligation for the agents the
  harness ships.
