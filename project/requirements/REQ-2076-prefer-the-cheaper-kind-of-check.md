---
id: REQ-2076
artifact: requirement
topic: testing
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0032
verification: static
---

# REQ-2076

Where an obligation can be checked statically it MUST NOT be checked
behaviourally, and where it can be checked behaviourally it MUST NOT be
checked by evaluation, because each step down costs determinism.
