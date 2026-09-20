---
id: index
artifact: index
status: live
revised: 2026-09-20
---

# Decisions

No decisions are in force. One is drafted and waiting on approval.

|                                                                                | Decision                                                       | Status |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------- | ------ |
| [ADR-1000](ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md) | The reply shape is a forced output style carried by the kernel | draft  |

The design step has run once against the requirements as they now stand. It
produced fifty records earlier, and this repository no longer carries them:
they addressed a requirement set that has since been merged, split and reduced,
so we'll write them again from the requirements we have now. The history keeps
them, and no new decision reuses one of their identifiers.

Identifiers are allocated in blocks by layer, with gaps, so a decision written
later joins its neighbours. A decision names the requirements it addresses,
says what works once you accept it and what still doesn't, and leaves the
system working.
