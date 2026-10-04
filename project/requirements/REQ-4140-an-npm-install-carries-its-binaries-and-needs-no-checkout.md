---
id: REQ-4140
artifact: requirement
topic: pi-packages
class: non-functional
status: withdrawn
revised: 2026-10-04
elaborates: RES-0342
verification: behavioural
---

# REQ-4140

**Withdrawn by ADR-2810. Replaced by REQ-4144.**

It read: each meowpaw Pi package publishes to npm with the meow-full binary
for every platform inside its tarball, so an install needs no checkout and
makes no request.

ADR-2810 ships the binary with the core package alone: five tarballs
carried the same six binaries redundantly, and the core package is the
install every other layer sits beside. REQ-4144 states what holds in its
place — the core tarball carries every platform's binary, the other
packages carry none, and their launchers fall back to `meow` on PATH.
