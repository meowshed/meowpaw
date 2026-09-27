---
id: index
artifact: index
status: live
revised: 2026-09-22
---

# Decisions

Every decision below is in force, as amended by the ones after it.
`paw index adr --write` generates everything below from the tree, and
`paw check index` reports it when it falls out of date.

<!-- meow-flow index -->

42 decisions in all: 42 approved.

| Identifier                                                                                                      | What it concluded                                                                                                | Status   |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------- |
| [ADR-1000](ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)                                  | The reply shape is a forced output style carried by the kernel                                                   | approved |
| [ADR-1010](ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md)                                | The writing standard ships as a unit that reviews itself                                                         | approved |
| [ADR-1020](ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md)            | Every shipped prompt is tagged, and a rule that must hold is loaded by a hook                                    | approved |
| [ADR-1030](ADR-1030-shipped-prompts-use-top-level-tags-with-markdown-inside.md)                                 | Shipped prompts use top-level tags with Markdown inside                                                          | approved |
| [ADR-1040](ADR-1040-the-style-carries-the-reply-shape-to-a-subordinate-agent.md)                                | The style carries the reply shape to a subordinate agent                                                         | approved |
| [ADR-1050](ADR-1050-a-unit-that-must-hold-is-loaded-by-its-description.md)                                      | A unit that must hold is loaded by a description stating the obligation                                          | approved |
| [ADR-1060](ADR-1060-the-kernel-names-no-unit-outside-it.md)                                                     | The kernel names no unit outside it                                                                              | approved |
| [ADR-1070](ADR-1070-the-five-verbs-resolve-from-the-profile.md)                                                 | The five verbs resolve from the profile, and an unresolved verb is reported                                      | approved |
| [ADR-1080](ADR-1080-a-commit-message-is-checked-against-the-declared-convention.md)                             | A commit message is checked against the convention the repository declares                                       | approved |
| [ADR-1090](ADR-1090-a-git-pack-enforces-the-convention-at-push.md)                                              | A `git` pack refuses a commit on the trunk and checks a branch before it is pushed                               | approved |
| [ADR-1100](ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md)                                       | The record is checked by a unit the harness ships                                                                | approved |
| [ADR-1110](ADR-1110-one-native-tool-carries-every-units-program.md)                                             | One native tool carries every unit's program                                                                     | approved |
| [ADR-1120](ADR-1120-the-marketplace-is-served-from-meow-retran-me.md)                                           | The marketplace is served from meow.retran.me                                                                    | approved |
| [ADR-1130](ADR-1130-the-chain-runs-as-steps-a-program-can-gate.md)                                              | The chain runs as steps that a program gates                                                                     | approved |
| [ADR-1140](ADR-1140-a-draft-meets-every-content-rule-a-frozen-record-keeps-its-own.md)                          | A draft meets every content rule, and a frozen record keeps the rules it was approved under                      | approved |
| [ADR-1150](ADR-1150-the-record-answers-what-an-identifier-is-and-what-cites-it.md)                              | The record answers what an identifier is and what cites it, and a closed task carries its evidence               | approved |
| [ADR-1160](ADR-1160-each-step-carries-its-own-obligations.md)                                                   | Each step's file carries the obligations of its step, and each template those of its kind                        | approved |
| [ADR-1170](ADR-1170-an-approval-is-a-stored-status-a-check-holds-frozen.md)                                     | An approval is a stored status that a check holds frozen, and a session opens with what waits for one            | approved |
| [ADR-1180](ADR-1180-the-record-grows-by-program-indexed-allocated-and-searched.md)                              | The record grows by program: its indexes generated, its identifiers allocated and its content searched           | approved |
| [ADR-1190](ADR-1190-the-design-step-carries-the-obligations-on-what-it-designs.md)                              | The design step carries the obligations on what it designs, and the other steps their share                      | approved |
| [ADR-1200](ADR-1200-the-harness-holds-its-quality-attributes-with-evidence.md)                                  | The harness holds its quality attributes, each with a check or a stated piece of evidence                        | approved |
| [ADR-1210](ADR-1210-the-record-reports-where-it-contradicts-itself.md)                                          | The record reports where it contradicts itself, and derives each requirement's state                             | approved |
| [ADR-1220](ADR-1220-an-insight-is-a-kind-of-record.md)                                                          | An insight is a kind of record, written only when something was learned                                          | approved |
| [ADR-1230](ADR-1230-the-record-keeps-its-reading-order-and-its-history-out-of-the-way.md)                       | The record keeps its reading order, and its history out of the way                                               | approved |
| [ADR-1240](ADR-1240-a-change-to-the-records-shape-migrates-what-exists.md)                                      | A change to the record's shape migrates what exists, and a retired name stays retired                            | approved |
| [ADR-1250](ADR-1250-init-writes-a-profile-and-a-constitution-from-what-the-repository-holds.md)                 | `/meow-method:init` writes a profile and a constitution from what the repository holds                           | approved |
| [ADR-1260](ADR-1260-onboarding-recovers-what-a-repository-is-and-places-every-document.md)                      | Onboarding recovers what a repository is, and places every document it already has                               | approved |
| [ADR-1270](ADR-1270-each-unit-is-adopted-alone-and-a-missing-capability-names-its-fix.md)                       | Each unit is adopted alone, and a missing capability names what would supply it                                  | approved |
| [ADR-1280](ADR-1280-onboarding-finishes-by-removing-what-it-placed.md)                                          | Onboarding finishes by removing what it placed, once the report is approved                                      | approved |
| [ADR-1290](ADR-1290-a-github-pack-reads-a-repositorys-history.md)                                               | A GitHub pack reads a repository's history, and writes nothing                                                   | approved |
| [ADR-1300](ADR-1300-onboarding-reads-what-the-history-states.md)                                                | Onboarding reads what the documents and the forge history state, and recovers it as drafts                       | approved |
| [ADR-1310](ADR-1310-the-github-pack-projects-an-approved-epic-onto-issues.md)                                   | The GitHub pack projects an approved epic's tasks onto issues, and reports where the two disagree                | approved |
| [ADR-1320](ADR-1320-source-control-is-held-by-checks-where-a-program-settles-it.md)                             | Source-control discipline is held by a check where a program settles it, and by the commit skill where none does | approved |
| [ADR-1330](ADR-1330-a-decision-may-postpone-requirements-and-each-verification-revisits-them.md)                | A decision may postpone requirements, and each verification revisits them                                        | approved |
| [ADR-1340](ADR-1340-version-control-tools-other-than-git-are-postponed.md)                                      | Version control tools other than git are postponed                                                               | approved |
| [ADR-1350](ADR-1350-the-record-command-is-named-paw.md)                                                         | The record's command is `paw`, and `meow-method` stays one release as a deprecated alias                         | approved |
| [ADR-1360](ADR-1360-removing-an-instruction-is-postponed-until-the-cases-can-see-one.md)                        | Removing an instruction is postponed until the cases can see one                                                 | approved |
| [ADR-1370](ADR-1370-each-unit-ships-its-own-page-and-a-program-holds-the-documentation-to-the-tree.md)          | Each unit ships its own page, and a program holds the documentation to the tree                                  | approved |
| [ADR-1380](ADR-1380-the-document-step-writes-one-kind-per-page-and-checks-through-the-verbs.md)                 | The document step writes one kind per page to the declared style, and checks documentation through the verbs     | approved |
| [ADR-1390](ADR-1390-the-method-unit-is-meow-flow-and-meow-method-stays-one-release-as-a-stub.md)                | The method's unit is `meow-flow`, and `meow-method` stays one release as a stub that says so                     | approved |
| [ADR-1400](ADR-1400-a-licensing-unit-applies-the-declared-header-and-a-program-checks-every-file-is-covered.md) | A licensing unit applies the header a repository declares, and a program checks that every file is covered       | approved |
| [ADR-1410](ADR-1410-the-verbs-are-format-lint-check-test-and-build.md)                                          | The verbs are `format`, `lint`, `check`, `test` and `build`, and the old names are read for one release          | approved |

Amended: ADR-1000 by ADR-1040; ADR-1010 by ADR-1020; ADR-1020 by ADR-1030 and ADR-1050; ADR-1070 by ADR-1110 and ADR-1410; ADR-1100 by EPC-1070; ADR-1350 by ADR-1390.
<!-- /meow-flow index -->
