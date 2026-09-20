---
id: REQ-2536
artifact: requirement
topic: source-control
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0131
verification: behavioural
---

# REQ-2536

The harness MUST NOT treat parallel working trees as separate repositories.

They share objects and references, so a branch or a tag made in one is
immediately visible in the others and a second copy of an operation is not
isolation.
