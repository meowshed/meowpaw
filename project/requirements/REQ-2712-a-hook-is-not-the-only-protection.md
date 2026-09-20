---
id: REQ-2712
artifact: requirement
topic: safety
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0203
verification: judgement
verifier: agent
---

# REQ-2712

A design MUST NOT be safe only because a hook blocks something.

Hooks do not run before a workspace is trusted, do not run when disabled, and
do not run under a policy that permits only managed ones.
