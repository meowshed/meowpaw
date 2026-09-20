---
id: REQ-0010
artifact: requirement
topic: adoption
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0002
verification: static
---

# REQ-0010

The harness MUST be installable into an existing repository without modifying
that repository's build, its dependencies or its directory layout beyond
adding files the harness owns.

A harness that changes the build makes the repository depend on it, which is
the opposite of adoptable: it can then be neither removed nor tried.
