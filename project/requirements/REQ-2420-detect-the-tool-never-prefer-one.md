---
id: REQ-2420
artifact: requirement
topic: packs
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0104, RES-0105, RES-0106
verification: behavioural
---

# REQ-2420

Where several tools serve one verb in an ecosystem, the pack MUST resolve the
verb from what the repository configured and MUST NOT choose between them on
its own.

Running the tool the project did not choose reformats or re-lints the whole
repository, which is the largest false difference a pack can produce.
