---
id: index
artifact: index
status: live
revised: 2026-09-22
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

127 documents, indexed by
[RES-0001-synthesis.md](research/RES-0001-synthesis.md), which everything
downstream cites.

## Requirements

1,069 obligations, indexed by [requirements/README.md](requirements/README.md).
Each is one file carrying one obligation, and it declares whether it's
functional or non-functional and which of the four kinds of check verifies it:
a static check, a behavioural fixture, a judgement with its judge named, or a
measured evaluation.

## Decisions

[ADR-1000](adrs/ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)
is approved and in force: the reply shape is a forced output style carried by
the kernel. It is the first turn the design step has run against the
requirements as they now stand.

[ADR-1010](adrs/ADR-1010-the-writing-standard-ships-as-a-unit-that-reviews-itself.md)
is approved and in force: the writing standard ships as `meow-prose`, held
by a reviewer inside it and by a separately installed gate, and never by a
pattern over prose.

[ADR-1020](adrs/ADR-1020-every-shipped-prompt-is-tagged-and-a-rule-that-must-hold-is-loaded-by-a-hook.md)
is a draft that amends it: every shipped prompt is written in XML tags for
Sonnet 5 and Opus 5.5, the writing skill is loaded by a `SessionStart` hook,
and the gate blocks with the field a prompt hook actually has.

## Specifications

[SPC-1000](specs/SPC-1000-the-reply-shape.md) states the reply shape, checked
at #27. It records that REQ-0930 is unmet: the style applies when a
person selects it, and not on its own.

[SPC-1010](specs/SPC-1010-the-writing-standard.md) states the writing standard
and [SPC-1020](specs/SPC-1020-measuring-the-harness.md) states how a change to
what the harness says is measured. Nothing implements either yet, so both leave
`checked-at` empty.

## Epics and tasks

[EPC-1000](epics/EPC-1000-the-reply-shape-in-the-kernel.md) is approved and
realises ADR-1000 in five tasks, TSK-1010 to TSK-1050, each filed as an issue
from #5 to #9 and each closed with evidence. The epic closed at #27 with
one acceptance criterion unmet, named in the epic as REQ-3170 requires. TSK-1000 is the
planning task that produced all of it, and `tools/check_coverage.py` reports
every requirement the decision addresses landing in exactly one task.

[EPC-1010](epics/EPC-1010-the-writing-standard-as-a-unit.md) is approved and
realises ADR-1010 in eleven tasks, TSK-1110 to TSK-1210, each filed as an issue
once the epic was approved. TSK-1100 is the planning task, under #46. Every
requirement ADR-1010 addresses lands in exactly one task except REQ-3034, which
the epic defers with its reason.

[EPC-1020](epics/EPC-1020-every-shipped-prompt-tagged-and-loaded.md) is a draft
that realises ADR-1020 in four tasks, TSK-1230 to TSK-1260, not yet filed as
issues. TSK-1220 is the planning task, under #62.

## Defects

| Defect                                                                       | What it was                                                                                 |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [BUG-1000](bugs/BUG-1000-the-constitution-records-state.md)                  | `CLAUDE.md` recorded the project's state, and one claim was false                           |
| [BUG-1005](bugs/BUG-1005-the-constitution-cited-deleted-pages.md)            | `CLAUDE.md` cited deleted pages and overstated what verifies a commit                       |
| [BUG-1010](bugs/BUG-1010-checks-walk-into-plugin-and-documentation-files.md) | Three record checks reported a false positive on a plugin file                              |
| [BUG-1020](bugs/BUG-1020-the-marks-were-late.md)                             | Two closed tasks stayed unmarked and their records carried no evidence                      |
| [BUG-1040](bugs/BUG-1040-the-shape-is-not-unconditional.md)                  | The forced style is not applied, so the reply shape is opt-in                               |
| [BUG-1090](bugs/BUG-1090-the-record-cites-a-hash.md)                         | The record cited a commit hash where the pull request survives                              |
| [BUG-1080](bugs/BUG-1080-the-records-cite-replaced-commits.md)               | The records cited commits that a message rewrite replaced                                   |
| [BUG-1070](bugs/BUG-1070-the-records-are-written-below-the-standard.md)      | The records were written below the writing standard the constitution requires               |
| [BUG-1060](bugs/BUG-1060-the-unit-field-is-dead.md)                          | A field the constitution required was dropped from the record and left in the templates     |
| [BUG-1050](bugs/BUG-1050-the-specification-direction-was-unchecked.md)       | A requirement the decision addresses was stated in no specification                         |
| [BUG-1030](bugs/BUG-1030-eval-results-were-committed.md)                     | A generated eval report reached `main`, because the ignore pattern was anchored at the root |

Ten are closed. BUG-1040 is open: it routes to design, because the mechanism
ADR-1000 chose does not deliver what the decision claims. BUG-1005 was written
after its fix, and says so.
