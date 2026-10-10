---
id: REQ-4502
artifact: requirement
topic: shared-binary
class: functional
status: approved
revised: 2026-10-10
elaborates: RES-0347
verification: static
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# REQ-4502

A unit that runs a program of the native tool MUST declare the core unit under
`dependencies` in its manifest, and MUST depend on no other unit.

The dependency points down at the kernel, so adopting a subset of the units
still adopts the core.
