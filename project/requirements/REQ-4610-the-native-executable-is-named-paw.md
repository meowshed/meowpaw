---
id: REQ-4610
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-11
elaborates: ADR-2920
verification: behavioural
---

# REQ-4610

The Rust build MUST emit the shared native executable as `paw` for every
supported target, and every release archive and installer MUST preserve that
name, including the platform extension on Windows.

The Claude and Pi launchers invoke the same artifact, and an archive named
`meow-<target>` cannot satisfy a launcher looking for `paw`. A mismatch leaves
a released unit unable to run its program.
