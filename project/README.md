---
id: index
artifact: index
status: live
revised: 2026-09-24
---

# The project

Everything the project has decided, is obliged to do, or has learned. Code
lives elsewhere, documentation lives in `docs/`, and the constitution is
`CLAUDE.md` at the repository root, because the platform loads it only from
there.

Each document declares its own lifetime in its front matter, so you can move a
file without changing what it is. A living document carries `status: live` and
you rewrite it freely. A record carries its own status, stays mutable while
it's a draft, and freezes when someone approves it.

| Kind          | Where                       | Identifier | Lifetime |
| ------------- | --------------------------- | ---------- | -------- |
| Vision        | [`vision.md`](vision.md)    | named      | living   |
| Specification | `specs/SPC-NNNN-<topic>.md` | `SPC-NNNN` | living   |
| Research      | [`research/`](research/)    | `RES-NNNN` | record   |
| Requirement   | `requirements/`             | `REQ-NNNN` | record   |
| Decision      | `adrs/`                     | `ADR-NNNN` | record   |
| Epic          | `epics/`                    | `EPC-NNNN` | record   |
| Task          | `tasks/`                    | `TSK-NNNN` | record   |
| Defect        | `bugs/`                     | `BUG-NNNN` | record   |

One artifact per file, named for its identifier, in a directory named for its
kind. A directory appears when its first artifact does. You find a record by
what it says and by the identifiers it cites, never by the week somebody wrote
it.

## Research

129 documents, indexed by
[RES-0001-synthesis.md](research/RES-0001-synthesis.md), which everything
downstream cites.

## Requirements

1,078 obligations, withdrawn ones included, indexed by
[requirements/README.md](requirements/README.md). Each is one file carrying
one obligation, and it declares whether it's functional or non-functional and
which of the four kinds of check verifies it: a static check, a behavioural
fixture, a judgement with its judge named, or a measured evaluation.

## Decisions

Every decision below is approved and in force, as amended by the ones after it.

- [ADR-1000](adrs/ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md):
  the reply shape is a forced output style carried by the kernel.
- [ADR-1010](adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md):
  the writing standard ships as `meow-prose`, held by a reviewer inside it and
  by a separately installed gate, and never by a pattern over prose.
- [ADR-1020](adrs/ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md):
  every shipped prompt is written in XML tags for Sonnet 5 and Opus 5.5, and
  the gate blocks with the field a prompt hook actually has.
- [ADR-1030](adrs/ADR-1030-shipped-prompts-use-top-level-tags-with-markdown-inside.md):
  five top-level tags with Markdown inside, and each rule a list item led by
  an identifier.
- [ADR-1040](adrs/ADR-1040-the-style-carries-the-reply-shape-to-a-subordinate-agent.md):
  the style carries the reply shape to a subordinate agent itself, through its
  rule R10.
- [ADR-1050](adrs/ADR-1050-a-unit-that-must-hold-is-loaded-by-its-description.md):
  a unit that has to hold is loaded by a description stating the obligation,
  and not by the `SessionStart` hook ADR-1020 chose.
- [ADR-1060](adrs/ADR-1060-the-kernel-names-no-unit-outside-it.md): the
  kernel names, points to and loads no unit outside it.
- [ADR-1070](adrs/ADR-1070-the-five-verbs-resolve-from-the-profile.md): the
  five verbs resolve from the repository's profile, and an unresolved verb is
  reported as unresolved.
- [ADR-1080](adrs/ADR-1080-a-commit-message-is-checked-against-the-declared-convention.md):
  a commit message is checked against the convention the repository declares
  and against the attribution ban.
- [ADR-1090](adrs/ADR-1090-a-git-pack-enforces-the-convention-at-push.md): a
  `git` pack refuses a commit on the trunk and checks a branch before it is
  pushed.
- [ADR-1100](adrs/ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md):
  the record is checked by a unit the harness ships, as EPC-1070 amends it.
- [ADR-1110](adrs/ADR-1110-one-native-tool-carries-every-units-program.md):
  every unit's program is a subcommand of one native tool, amending ADR-1070.
- [ADR-1120](adrs/ADR-1120-the-marketplace-is-served-from-meow-retran-me.md):
  the released marketplace is served from `meow.retran.me`.
- [ADR-1130](adrs/ADR-1130-the-chain-runs-as-steps-a-program-can-gate.md): the
  method's nine steps run as one skill, gated by `meow record`.

## Specifications

[SPC-1000](specs/SPC-1000-the-reply-shape.md) states the reply shape, checked
at #27. It records that REQ-0930 is unmet: the style applies when a person
selects it, and not on its own.

[SPC-1010](specs/SPC-1010-the-writing-standard.md) states the writing standard,
[SPC-1020](specs/SPC-1020-measuring-the-harness.md) states how a change to what
the harness says is measured, and
[SPC-1030](specs/SPC-1030-how-the-harness-writes-a-prompt.md) states how every
prompt the harness ships is written. The work realising them has landed, and
each leaves `checked-at` empty until its epics are verified.

[SPC-1040](specs/SPC-1040-the-five-verbs.md) states the five verbs, resolved
from the repository's profile. `meow-verbs` implements it, verified under
issue 115.

[SPC-1050](specs/SPC-1050-the-commit-convention.md) states the commit
convention and its check, and `meow-scm` implements it, verified under issue 130.

[SPC-1060](specs/SPC-1060-the-git-pack.md) states the `git` pack, and
`meow-git` implements it, verified under issue 138.

[SPC-1070](specs/SPC-1070-checking-the-record.md) states how the record is
checked, and `meow-method` implements it, verified under issue 168.

[SPC-1080](specs/SPC-1080-the-native-tool.md) states the native tool, its
launchers, its release and the marketplace address. The crate implements it,
verified under issue 160.

[SPC-1090](specs/SPC-1090-the-chain.md) states the method's chain: the steps,
the gate each checks, the state of the record and the command that drives it.
Nothing implements it yet.

## Epics and tasks

[EPC-1000](epics/EPC-1000-the-reply-shape-in-the-kernel.md) realises ADR-1000
in five tasks, TSK-1010 to TSK-1050, each closed with evidence. The epic closed
at #27 with one acceptance criterion unmet, named in the epic as REQ-3170
requires.

[EPC-1010](epics/EPC-1010-the-writing-standard-as-a-unit.md) realises ADR-1010
in eleven tasks, TSK-1110 to TSK-1210, and all eleven are closed with evidence.
Verified under issue 118, it closed with criterion 9 unmet, named in the epic:
BUG-1100 records that the reviewer is unmeasured on most of the rules it holds. Every requirement ADR-1010 addresses
lands in exactly one task except REQ-3034, which the epic defers with its
reason.

[EPC-1020](epics/EPC-1020-every-shipped-prompt-tagged-and-loaded.md) realises
ADR-1020 in four tasks, TSK-1230 to TSK-1260. Three are closed. TSK-1260,
which removes every instruction the loop shows has no effect, is postponed by
the owner until the case sets can see a single rule, and the task records why.

[EPC-1030](epics/EPC-1030-the-writing-standard-loaded-by-its-description.md)
realises ADR-1050 in one task, TSK-1270, closed in #85.

[EPC-1040](epics/EPC-1040-the-five-verbs.md) realises ADR-1070 in two tasks,
TSK-1280 and TSK-1290, both closed with evidence, and was verified against
every acceptance criterion under issue 115.

[EPC-1050](epics/EPC-1050-the-commit-convention.md) realises ADR-1080 in two
tasks, TSK-1300 and TSK-1310, both closed with evidence, and was verified
against every acceptance criterion under issue 130.

[EPC-1060](epics/EPC-1060-the-git-pack.md) realises ADR-1090 in one task,
TSK-1320, closed with evidence, and was verified against every acceptance
criterion under issue 138.

[EPC-1070](epics/EPC-1070-checking-the-record.md) realised ADR-1100 in two
tasks, TSK-1330 and TSK-1340, each closed with evidence, and was verified
against every acceptance criterion under issue 168.

[EPC-1080](epics/EPC-1080-the-native-tool.md) realised ADR-1110 in five
tasks, TSK-1350 to TSK-1390, each closed with evidence, and was verified
against every acceptance criterion under issue 160.

[EPC-1090](epics/EPC-1090-the-marketplace-address.md) realised ADR-1120 in two
tasks, TSK-1400 and TSK-1410, each closed with evidence, and was verified
against every acceptance criterion under issue 184.

[EPC-1100](epics/EPC-1100-the-chain.md) is approved and realises ADR-1130 in
three tasks, TSK-1420 to TSK-1440, each filed as an issue.

## Defects

| Defect                                                                               | What it was                                                                                 |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| [BUG-1000](bugs/BUG-1000-the-constitution-records-state.md)                          | `CLAUDE.md` recorded the project's state, and one claim was false                           |
| [BUG-1005](bugs/BUG-1005-the-constitution-cited-deleted-pages.md)                    | `CLAUDE.md` cited deleted pages and overstated what verifies a commit                       |
| [BUG-1010](bugs/BUG-1010-checks-walk-into-plugin-and-documentation-files.md)         | Three record checks reported a false positive on a plugin file                              |
| [BUG-1020](bugs/BUG-1020-the-marks-were-late.md)                                     | Two closed tasks stayed unmarked and their records carried no evidence                      |
| [BUG-1040](bugs/BUG-1040-the-shape-is-not-unconditional.md)                          | The forced style is not applied, so the reply shape is opt-in                               |
| [BUG-1090](bugs/BUG-1090-the-record-cites-a-hash.md)                                 | The record cited a commit hash where the pull request survives                              |
| [BUG-1100](bugs/BUG-1100-the-reviewer-is-unmeasured-on-most-rules.md)                | The reviewer is unmeasured on most of the rules it holds                                    |
| [BUG-1080](bugs/BUG-1080-the-records-cite-replaced-commits.md)                       | The records cited commits that a message rewrite replaced                                   |
| [BUG-1070](bugs/BUG-1070-the-records-are-written-below-the-standard.md)              | The records were written below the writing standard the constitution requires               |
| [BUG-1060](bugs/BUG-1060-the-unit-field-is-dead.md)                                  | A field the constitution required was dropped from the record and left in the templates     |
| [BUG-1050](bugs/BUG-1050-the-specification-direction-was-unchecked.md)               | A requirement the decision addresses was stated in no specification                         |
| [BUG-1030](bugs/BUG-1030-eval-results-were-committed.md)                             | A generated eval report reached `main`, because the ignore pattern was anchored at the root |
| [BUG-1110](bugs/BUG-1110-requirements-elaborate-missing-research.md)                 | Eight requirements elaborated research that never existed                                   |
| [BUG-1120](bugs/BUG-1120-the-install-instructions-give-no-binary.md)                 | The install instructions gave a unit without its binary                                     |
| [BUG-1130](bugs/BUG-1130-meow-method-counts-one-finding-as-findings.md)              | `meow-method` counted one finding as "1 findings"                                           |
| [BUG-1140](bugs/BUG-1140-the-guards-act-on-commands-that-neither-commit-nor-push.md) | `meow-git`'s guards acted on commands that neither commit nor push                          |
| [BUG-1150](bugs/BUG-1150-the-crate-tests-can-share-a-directory.md)                   | The crate's tests could share a temporary directory, so the gate failed at random           |

Fifteen are closed. BUG-1040 and BUG-1100 are open. BUG-1040 routes to design, because the mechanism
ADR-1000 chose does not deliver what the decision claims. BUG-1100 routes to requirements, because no requirement
asks for the reviewer's cases to cover every rule. BUG-1005 was written
after its fix, and says so.
