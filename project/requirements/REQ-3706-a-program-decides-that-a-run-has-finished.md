---
id: REQ-3706
artifact: requirement
topic: long-runs
class: functional
status: approved
revised: 2026-10-03
elaborates: RES-0320, RES-0074
verification: behavioural
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-3706

Whether a run has finished MUST be computed by a program from the record at the current tree, never taken from a model's judgement.

A model that judges its own finish can end a run early or never, and `/goal` judges from the conversation alone (RES-0320, conclusion 2), so the finish comes from the counts `paw status` computes.
