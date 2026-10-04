---
id: REQ-4140
artifact: requirement
topic: pi-packages
class: non-functional
status: approved
revised: 2026-10-04
elaborates: RES-0342
verification: behavioural
---

# An npm install carries its binaries and needs no checkout

Each meowpaw Pi package publishes to npm under the `@meowshed` scope with
the meow-full binary for every platform the build workflow builds inside
its tarball, so `pi install npm:@meowshed/<unit>` succeeds on a machine
that holds no meowpaw checkout and makes no request at install or load
time. The `postinstall` runs only where the binary is absent, which is a
git-source install, and exits 0 without failing the install where it
cannot download.

Rationale: RES-0342 found a local-path install pointing into the checkout
and running no lifecycle script, so the first install died with the
checkout and its binaries had to be fetched by hand. A tarball that
carries every platform is the one distribution that is both
checkout-independent and free of a download that can fail.
