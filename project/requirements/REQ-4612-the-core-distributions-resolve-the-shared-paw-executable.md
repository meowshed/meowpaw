---
id: REQ-4612
artifact: requirement
topic: pi-packages
class: functional
status: approved
revised: 2026-10-11
elaborates: ADR-2920
verification: behavioural
---

# REQ-4612

The Claude and Pi `meow-core` distributions MUST carry the all-features `paw`
executable for every supported platform, and every other unit's launcher MUST
resolve that executable through the core distribution without resolving its
own wrapper recursively.

Claude launchers use the core unit's data marker. The Pi core extension exports
its absolute executable path as `MEOWPAW_BINARY`, and Pi launchers invoke that
path directly; the `meow-flow` launcher also passes its package layout through
`MEOW_LAYOUT`. This keeps every unit on the one build while preserving the
record's package-specific layout.
