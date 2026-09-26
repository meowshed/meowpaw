---
id: REQ-2832
artifact: requirement
topic: the-forge
class: functional
status: draft
revised: 2026-09-26
elaborates: RES-0277
verification: static
---

# REQ-2832

Reading a forge's history MUST NOT write to the forge.

A read that changes the forge can't be repeated to see what it would find.
