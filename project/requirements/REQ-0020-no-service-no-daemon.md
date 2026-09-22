---
id: REQ-0020
artifact: requirement
topic: adoption
class: non-functional
status: withdrawn
revised: 2026-09-21
elaborates: RES-0023
verification: static
---

# REQ-0020

**Withdrawn. Replaced by REQ-3178 and REQ-3180.**

It read: the harness MUST NOT require a network service, a database, a
background daemon or a bespoke command-line tool in order to perform its
method, with tools the project already runs excepted.

It forbade too much. A program that installs with a unit, runs from inside it
and writes nothing into the repository being worked on costs that repository
nothing beyond the install it chose. The cost this requirement named, something
a person installs, operates and recovers by hand, belongs to a separate
installation and not to a program a unit carries.

The vision carried the same overreach and contradicted itself, promising no
program while naming `meow-book` as a separate tool beside the harness.
