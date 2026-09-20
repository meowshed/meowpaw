---
id: REQ-3056
artifact: requirement
topic: universality
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0267
verification: judgement
verifier: agent
---

# REQ-3056

The harness MUST treat a read denial as a strong default rather than as a
boundary, because a shell search over a directory containing denied files
still returns them.
