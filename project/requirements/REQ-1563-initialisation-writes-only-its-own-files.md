---
id: REQ-1563
artifact: requirement
topic: onboarding
class: functional
status: approved
revised: 2026-09-20
elaborates: RES-0058
verification: static
---

# REQ-1563

The step that writes a profile MUST write only the files the harness owns, and
MUST NOT create a unit of work, run a verb, install anything that changes what
other tools do, or edit a file the repository already keeps.

It is run to adopt the harness rather than to start work, and a command that
changes the repository's own files while doing so is a change nobody asked for
and nobody reviewed.
