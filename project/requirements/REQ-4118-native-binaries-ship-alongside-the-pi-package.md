---
id: REQ-4118
artifact: requirement
topic: pi-packages
class: functional
status: withdrawn
revised: 2026-10-04
elaborates: RES-0340
verification: behavioural
---

# REQ-4118

**Withdrawn by ADR-2790. Replaced by REQ-4136.**

It read: the native binaries ship as platform-specific executables in the
Pi package or a dependency package, and the extension resolves each
binary's path relative to the package root.

No binary ships at all, and the reason is SPC-1080's own build: each unit's
release binary is compiled with only its own feature, so a package that
bundles several units cannot be served by any one unit's archive. REQ-4136
states what holds in its place: one meow binary built with every feature,
published once as the meow-full release and downloaded by each package's
installer at install time.
