---
id: REQ-0079
artifact: requirement
topic: universality
class: non-functional
status: approved
revised: 2026-09-26
elaborates: RES-0004
verification: static
---

# REQ-0079

A unit outside the kernel MAY use another unit's program when that unit is
installed, and where it isn't, it MUST report the check that program would
have made as unrun, and MUST NOT behave as if the check passed.

REQ-0076 stops one unit from requiring another, and a unit that works only
with a second one installed breaks it. A unit that uses the second one when
present and says so when absent still works alone, and it keeps one check in
one place where a copy of the check would drift. The kernel is excluded,
because REQ-0077 keeps it from naming any unit at all.
