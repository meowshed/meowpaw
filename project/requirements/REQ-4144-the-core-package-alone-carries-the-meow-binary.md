---
id: REQ-4144
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-11
elaborates: RES-0342, RES-0343
verification: behavioural
---

# REQ-4144

**Withdrawn by ADR-2920. Replaced by REQ-4612.**

It read: the `@meowshed/meow-core` npm tarball carries the all-features meow
binary for every supported platform, while every other package carries none;
each launcher looks beside itself and falls back to `meow` on PATH.

ADR-2920 keeps the one all-features executable in `meow-core` and names it
`paw`. REQ-4612 requires Claude launchers to resolve it through the core data
marker and Pi launchers to use the absolute path exported by the core extension,
which avoids resolving a package's own wrapper recursively.
