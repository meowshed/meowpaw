---
id: REQ-4144
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
elaborates: RES-0342, RES-0343
verification: behavioural
---

# The core package alone carries the meow binary

The `@meowshed/meow-core` npm tarball carries the all-features meow binary
for every platform the build workflow builds, and the other five packages
carry no binary and run no installer. Each package's launcher looks for
its unit's binary beside itself first and falls back to `meow` on PATH,
which the core extension resolves, and reports each check as unrun where
neither holds.

Rationale: five packages carrying the same binary are five redundant
copies of it and five installers to keep in step, where the core package
is the layer every install already includes and its extension is already
the one putting directories on PATH. One distribution point for one
binary, and a missing core install degrades to the wrappers' designed
unrun report instead of breaking an install.
