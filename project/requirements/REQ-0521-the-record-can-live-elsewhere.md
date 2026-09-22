---
id: REQ-0521
artifact: requirement
topic: artifacts
class: functional
status: draft
revised: 2026-09-22
elaborates: RES-0271
verification: behavioural
---

# REQ-0521

A repository MUST be able to declare that its record lives in its own tree, in
another repository, or in a folder named by a path relative to its root, which
may lie outside it, and the harness MUST read and write the record there. A
repository that declares nothing keeps its record in its own tree.

A team whose specifications serve several code repositories keeps them in one
place, and a team whose code is public can keep its record apart. The path is
relative so that it names the same place on every machine that follows the
repository's checkout convention.
