---
id: REQ-0040
artifact: requirement
topic: adoption
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0023, RES-0021
verification: behavioural
---

# REQ-0040

The harness MUST NOT substitute a weaker capability for an unavailable one.

A weaker substitute reports a pass for a check that did not happen, which is
worse than the capability being missing and visible.
