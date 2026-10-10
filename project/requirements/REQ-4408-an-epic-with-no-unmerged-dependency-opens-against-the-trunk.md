---
id: REQ-4408
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0346
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4408

An epic or a defect with no unmerged dependency MUST open its pull request
against the trunk.

Parallel work stays parallel, and a stack is never deeper than the
dependencies require.
