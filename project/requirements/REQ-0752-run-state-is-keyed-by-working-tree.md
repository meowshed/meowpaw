---
id: REQ-0752
artifact: requirement
topic: state
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0031, RES-0262
verification: behavioural
---

# REQ-0752

Run state MUST be keyed by the path of the working tree it belongs to, and
MUST record the repository's identity inside the state rather than in its
location.

Keying by the repository collides between parallel working trees and between
two clones of the same remote, which are both ordinary. Recording the identity
inside means the state can still be found by either.
