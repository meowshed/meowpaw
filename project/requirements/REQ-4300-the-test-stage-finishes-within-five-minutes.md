---
id: REQ-4300
artifact: requirement
topic: test-stage-speed
class: non-functional
status: approved
revised: 2026-10-10
elaborates: RES-0345
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4300

The `test` stage MUST finish within 300 seconds on the owner's machine, with
the units' binaries already built.

The bound is a choice recorded in RES-0345: it sits above the slowest suite,
162 seconds, and below every duration measured on 2026-10-09 and 2026-10-10.
