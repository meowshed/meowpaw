---
id: REQ-3035
artifact: requirement
topic: the-harness-on-itself
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0266
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3035

The measurement suite MUST run only by hand on the owner's machine, so that no
workflow under `.github/workflows/` runs it or holds a model credential.

A scheduled or continuous-integration run makes a real model call on every
trigger, and the owner decided that none of them does.
