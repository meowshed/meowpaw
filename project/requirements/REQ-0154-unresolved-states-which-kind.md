---
id: REQ-0154
artifact: requirement
topic: verification
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0160
verification: behavioural
---

# REQ-0154

When a verb is unresolved, the harness MUST state which kind of unresolved it
is: that nothing can resolve it for this language, or that nothing in this
repository has.

The two lead to different actions - the first is a fact about the ecosystem
and the second is a gap in the repository's declaration - and a report that
collapses them tells the reader neither.
