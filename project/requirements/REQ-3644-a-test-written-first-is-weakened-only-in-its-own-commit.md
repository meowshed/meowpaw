---
id: REQ-3644
artifact: requirement
topic: the-short-chain
class: functional
status: approved
revised: 2026-09-29
elaborates: RES-0310
verification: judgement
verifier: person
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3644

The implementation MUST NOT modify, delete, skip or weaken a test written ahead of it, except in a commit of its own whose message says why the test was wrong.

Weakening a test is the cheapest way to make it pass, and a commit of its own keeps the change reviewable without a record (RES-0310, conclusion 8).
