---
id: REQ-3178
artifact: requirement
topic: adoption
class: non-functional
status: approved
revised: 2026-09-21
elaborates: RES-0023
verification: judgement
---

# REQ-3178

The harness MUST NOT require anything a person installs or operates separately
from the units it ships, and a unit MAY carry a program, a server or a daemon
of its own.

A second installation costs a repository, because somebody has to perform it,
operate it and recover it by hand. A program that arrives with a unit, runs
from inside it and stops with it costs nothing beyond the install the
repository already chose.
Where the harness uses a tool somebody already has on the machine, that tool
stays theirs: the harness uses it when it is there, reports it as absent when
it is not, and never installs it or makes the method depend on it.
