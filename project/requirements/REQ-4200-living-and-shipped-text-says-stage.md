---
id: REQ-4200
artifact: requirement
topic: stage-term
class: non-functional
status: approved
revised: 2026-10-10
elaborates: RES-0344
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4200

Living and shipped text MUST call `format`, `lint`, `check`, `test` and `build`
stages, where each page that introduces the word defines them as independent,
so a reader from a continuous integration tool doesn't take them for a
sequence in which a failure stops the next.

A frozen record keeps the word it was written with.
