---
id: REQ-4130
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340, BUG-1400
---

# REQ-4130

A Pi package carries inside its own directory every prompt, fragment,
template and supporting file its extension or skills load at runtime. No
extension resolves a path outside the package root. Where a file the
package owns is missing, the extension reports it and carries on with the
behaviour it can hold, and never reads a neighbouring package's or a
checkout's files.

Rationale: BUG-1400 found every shipped extension reading the monorepo's
`plugins/` directory, which holds nowhere the package actually installs. A
package that reads its own directory works wherever Pi puts it, and one
that cannot find its files fails visibly instead of running on empty
strings.
