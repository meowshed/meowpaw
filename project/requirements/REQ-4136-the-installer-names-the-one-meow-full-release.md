---
id: REQ-4136
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-11
verification: behavioural
elaborates: RES-0340, BUG-1403
---

# REQ-4136

**Withdrawn by ADR-2920. Replaced by REQ-4610.**

It read: each package's install script downloads the meow-full release archive,
the one meow binary built with every unit's feature, extracts the binary for
the machine it runs on, names it `meow` where the shell wrappers look for it,
removes the archive it downloaded, and exits 0 where any step fails.

ADR-2920 names the shared executable `paw`, and REQ-4610 requires every build,
archive and installer to preserve that name.
