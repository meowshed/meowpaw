---
id: index
artifact: index
status: live
revised: 2026-09-22
---

# Decisions

Every decision below is in force, as amended by the ones after it.
`meow-method index adr --write` generates everything below from the tree, and
`meow-method check index` reports it when it falls out of date.

<!-- meow-method index -->

27 decisions in all: 26 approved, 1 draft.

| Identifier                                                                                           | What it concluded                                                                                      | Status   |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------- |
| [ADR-1000](ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)                       | The reply shape is a forced output style carried by the kernel                                         | approved |
| [ADR-1010](ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md)                     | The writing standard ships as a unit that reviews itself                                               | approved |
| [ADR-1020](ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md) | Every shipped prompt is tagged, and a rule that must hold is loaded by a hook                          | approved |
| [ADR-1030](ADR-1030-shipped-prompts-use-top-level-tags-with-markdown-inside.md)                      | Shipped prompts use top-level tags with Markdown inside                                                | approved |
| [ADR-1040](ADR-1040-the-style-carries-the-reply-shape-to-a-subordinate-agent.md)                     | The style carries the reply shape to a subordinate agent                                               | approved |
| [ADR-1050](ADR-1050-a-unit-that-must-hold-is-loaded-by-its-description.md)                           | A unit that must hold is loaded by a description stating the obligation                                | approved |
| [ADR-1060](ADR-1060-the-kernel-names-no-unit-outside-it.md)                                          | The kernel names no unit outside it                                                                    | approved |
| [ADR-1070](ADR-1070-the-five-verbs-resolve-from-the-profile.md)                                      | The five verbs resolve from the profile, and an unresolved verb is reported                            | approved |
| [ADR-1080](ADR-1080-a-commit-message-is-checked-against-the-declared-convention.md)                  | A commit message is checked against the convention the repository declares                             | approved |
| [ADR-1090](ADR-1090-a-git-pack-enforces-the-convention-at-push.md)                                   | A `git` pack refuses a commit on the trunk and checks a branch before it is pushed                     | approved |
| [ADR-1100](ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md)                            | The record is checked by a unit the harness ships                                                      | approved |
| [ADR-1110](ADR-1110-one-native-tool-carries-every-units-program.md)                                  | One native tool carries every unit's program                                                           | approved |
| [ADR-1120](ADR-1120-the-marketplace-is-served-from-meow-retran-me.md)                                | The marketplace is served from meow.retran.me                                                          | approved |
| [ADR-1130](ADR-1130-the-chain-runs-as-steps-a-program-can-gate.md)                                   | The chain runs as steps that a program gates                                                           | approved |
| [ADR-1140](ADR-1140-a-draft-meets-every-content-rule-a-frozen-record-keeps-its-own.md)               | A draft meets every content rule, and a frozen record keeps the rules it was approved under            | approved |
| [ADR-1150](ADR-1150-the-record-answers-what-an-identifier-is-and-what-cites-it.md)                   | The record answers what an identifier is and what cites it, and a closed task carries its evidence     | approved |
| [ADR-1160](ADR-1160-each-step-carries-its-own-obligations.md)                                        | Each step's file carries the obligations of its step, and each template those of its kind              | approved |
| [ADR-1170](ADR-1170-an-approval-is-a-stored-status-a-check-holds-frozen.md)                          | An approval is a stored status that a check holds frozen, and a session opens with what waits for one  | approved |
| [ADR-1180](ADR-1180-the-record-grows-by-program-indexed-allocated-and-searched.md)                   | The record grows by program: its indexes generated, its identifiers allocated and its content searched | approved |
| [ADR-1190](ADR-1190-the-design-step-carries-the-obligations-on-what-it-designs.md)                   | The design step carries the obligations on what it designs, and the other steps their share            | approved |
| [ADR-1200](ADR-1200-the-harness-holds-its-quality-attributes-with-evidence.md)                       | The harness holds its quality attributes, each with a check or a stated piece of evidence              | approved |
| [ADR-1210](ADR-1210-the-record-reports-where-it-contradicts-itself.md)                               | The record reports where it contradicts itself, and derives each requirement's state                   | approved |
| [ADR-1220](ADR-1220-an-insight-is-a-kind-of-record.md)                                               | An insight is a kind of record, written only when something was learned                                | approved |
| [ADR-1230](ADR-1230-the-record-keeps-its-reading-order-and-its-history-out-of-the-way.md)            | The record keeps its reading order, and its history out of the way                                     | approved |
| [ADR-1240](ADR-1240-a-change-to-the-records-shape-migrates-what-exists.md)                           | A change to the record's shape migrates what exists, and a retired name stays retired                  | approved |
| [ADR-1250](ADR-1250-init-writes-a-profile-and-a-constitution-from-what-the-repository-holds.md)      | `/meow-method:init` writes a profile and a constitution from what the repository holds                 | approved |
| [ADR-1260](ADR-1260-onboarding-recovers-what-a-repository-is-and-places-every-document.md)           | Onboarding recovers what a repository is, and places every document it already has                     | draft    |

Amended: ADR-1000 by ADR-1040; ADR-1010 by ADR-1020; ADR-1020 by ADR-1030 and ADR-1050; ADR-1070 by ADR-1110; ADR-1100 by EPC-1070.
<!-- /meow-method index -->
