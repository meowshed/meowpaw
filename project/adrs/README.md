---
id: index
artifact: index
status: live
revised: 2026-09-22
---

# Decisions

Four decisions are in force.

|                                                                                                      | Decision                                                                      | Status                        |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------- |
| [ADR-1000](ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)                       | The reply shape is a forced output style carried by the kernel                | approved                      |
| [ADR-1010](ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md)                     | The writing standard ships as a unit that reviews itself                      | approved, amended by ADR-1020 |
| [ADR-1020](ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md) | Every shipped prompt is tagged, and a rule that must hold is loaded by a hook | approved                      |
| [ADR-1030](ADR-1030-shipped-prompts-use-top-level-tags-with-markdown-inside.md)                      | Shipped prompts use top-level tags with Markdown inside                       | approved                      |

The design step has run twice against the requirements as they now stand. It
produced fifty records earlier, and this repository no longer carries them:
they addressed a requirement set that has since been merged, split and reduced,
so we'll write them again from the requirements we have now. The history keeps
them, and no new decision reuses one of their identifiers.

Identifiers are allocated in blocks by layer, with gaps, so a decision written
later joins its neighbours. A decision names the requirements it addresses,
says what works once you accept it and what still doesn't, and leaves the
system working.
