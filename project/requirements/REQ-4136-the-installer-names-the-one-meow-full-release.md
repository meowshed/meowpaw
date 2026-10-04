---
id: REQ-4136
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-04
verification: behavioural
elaborates: RES-0340, BUG-1403
---

# REQ-4136

Each package's install script downloads the meow-full release archive, the
one meow binary built with every unit's feature, extracts the binary for
the machine it runs on, names it `meow` where the shell wrappers look for
it, removes the archive it downloaded, and exits 0 where any step fails,
leaving the wrappers to report each check as unrun. The script runs on ESM,
so it imports what it calls and never names `require`.

Rationale: BUG-1403 found a `require` call inside a `.mjs` file and four
packages naming another unit's release, so the cleanup silently failed and
the log named a unit whose release the package does not ship. A unit's own
release archive then proved worse than useless for the packages: each
unit's binary is compiled with only its own feature (SPC-1080), and a
package that bundles several units needs every subcommand, so one
all-features binary, built once and reused by every package and both
harnesses, is the one download that can serve them all.
