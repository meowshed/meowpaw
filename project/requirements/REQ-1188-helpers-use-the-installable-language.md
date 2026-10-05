---
id: REQ-1188
artifact: requirement
topic: helpers
class: non-functional
status: withdrawn
revised: 2026-10-03
elaborates: RES-0023
verification: static
---

# REQ-1188

**Withdrawn by ADR-2740. Replaced by the native tool ADR-1110 chose.**

It read: helpers that ship inside a unit MUST be written in the one language
the plugin platform installs dependencies for, so that installation needs no
step of its own.

The platform installs no dependency language for plugins, while the shipped
native binary needs no repository installation step. Keeping the language
constraint would contradict the working distribution mechanism.
