---
id: REQ-4900
artifact: requirement
topic: prompt-format
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0320
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4900

A unit with side effects MUST be invocable only by a person, except the driver,
which the model invokes.

A run's hook can only hand the model a prompt, so the model has to invoke the
driver through the `Skill` tool, which makes the driver the one action a model
must be able to run.
