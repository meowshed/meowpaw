---
id: REQ-4142
artifact: requirement
topic: pi-packages
class: non-functional
status: approved
revised: 2026-10-04
elaborates: RES-0343
verification: behavioural
---

# CI builds every target under Linux, and a darwin binary arrives signed

The continuous integration builds all six targets of the native tool on
Linux runners — the musl targets natively, the windows targets through
cargo-xwin, the darwin targets through osxcross — with no macOS or Windows
runner in the workflow, and every darwin binary it produces carries an
ad-hoc signature written before it is packed. The Claude Code marketplace
release keeps its per-unit archives carrying all six platforms.

Rationale: RES-0343 found each route builds under Linux, that the windows
route's licence covers it, and that the darwin route's SDK licence is the
one trade-off — named and pinned in the workflow rather than hidden. A
darwin binary without a signature is killed by macOS on sight, so the
build signs with `ldid` and the installer signs again, and no person
handles a signature on any install path.
