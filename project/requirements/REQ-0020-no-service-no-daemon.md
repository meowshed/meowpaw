---
id: REQ-0020
artifact: requirement
topic: adoption
class: non-functional
status: approved
revised: 2026-09-20
elaborates: RES-0023
verification: static
---

# REQ-0020

The harness MUST NOT require a network service, a database, a background
daemon or a bespoke command-line tool in order to perform its method. Tools
the project already runs are excepted, because those are the project's and not
the harness's.

Anything that has to be running is something to install, operate and recover,
which puts the method behind an operational cost the repository did not ask
for.
