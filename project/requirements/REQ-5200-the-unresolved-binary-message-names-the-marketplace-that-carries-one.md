---
id: REQ-5200
artifact: requirement
topic: unresolved-binary-message
class: functional
status: approved
revised: 2026-10-25
elaborates: BUG-1690
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-5200

Where a launcher can't resolve a binary for an install whose marketplace
source ships none, its diagnostic MUST name that cause and the address of
the marketplace that does.

Without it, the diagnostic's one remedy is a reinstall that already ran, and
the person it stops has no way from the message alone to find why the
remedy did nothing.
