---
id: index
artifact: index
status: live
revised: 2026-09-22
---

# Decisions

Every decision below is in force, as amended by the ones after it.

|                                                                                                      | Decision                                                                         | Status                        |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------------------- |
| [ADR-1000](ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)                       | The reply shape is a forced output style carried by the kernel                   | approved                      |
| [ADR-1010](ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md)                     | The writing standard ships as a unit that reviews itself                         | approved, amended by ADR-1020 |
| [ADR-1020](ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md) | Every shipped prompt is tagged, and a rule that must hold is loaded by a hook    | approved                      |
| [ADR-1030](ADR-1030-shipped-prompts-use-top-level-tags-with-markdown-inside.md)                      | Shipped prompts use top-level tags with Markdown inside                          | approved                      |
| [ADR-1040](ADR-1040-the-style-carries-the-reply-shape-to-a-subordinate-agent.md)                     | The style carries the reply shape to a subordinate agent                         | approved                      |
| [ADR-1050](ADR-1050-a-unit-that-must-hold-is-loaded-by-its-description.md)                           | A unit that must hold is loaded by a description stating the obligation          | approved                      |
| [ADR-1060](ADR-1060-the-kernel-names-no-unit-outside-it.md)                                          | The kernel names no unit outside it                                              | approved                      |
| [ADR-1070](ADR-1070-the-five-verbs-resolve-from-the-profile.md)                                      | The five verbs resolve from the profile, and an unresolved verb is reported      | approved                      |
| [ADR-1080](ADR-1080-a-commit-message-is-checked-against-the-declared-convention.md)                  | A commit message is checked against the convention the repository declares       | approved                      |
| [ADR-1090](ADR-1090-a-git-pack-enforces-the-convention-at-push.md)                                   | A git pack refuses a commit on the trunk and checks a branch before it is pushed | approved                      |
| [ADR-1100](ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md)                            | The record is checked by a unit the harness ships                                | approved                      |
| [ADR-1110](ADR-1110-one-native-tool-carries-every-units-program.md)                                  | One native tool carries every unit's program                                     | approved                      |
| [ADR-1120](ADR-1120-the-marketplace-is-served-from-meow-retran-me.md)                                | The marketplace is served from meow.retran.me                                    | approved                      |
| [ADR-1130](ADR-1130-the-chain-runs-as-steps-a-program-can-gate.md)                                   | The chain runs as steps that a program gates                                     | approved                      |

The design step has run twice against the requirements as they now stand. It
produced fifty records earlier, and this repository no longer carries them:
they addressed a requirement set that has since been merged, split and reduced,
so we'll write them again from the requirements we have now. The history keeps
them, and no new decision reuses one of their identifiers.

Identifiers are allocated in blocks by layer, with gaps, so a decision written
later joins its neighbours. A decision names the requirements it addresses,
says what works once you accept it and what still doesn't, and leaves the
system working.
