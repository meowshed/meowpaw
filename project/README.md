---
id: index
artifact: index
status: live
revised: 2026-09-20
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
kind. A directory appears when its first artifact does. Each record names its
unit of work in its own front matter as `unit`, so you find a record by what it
says and never by the week somebody wrote it.

## Research

126 documents, indexed by
[RES-0001-synthesis.md](research/RES-0001-synthesis.md), which everything
downstream cites.

## Requirements

1,053 obligations, indexed by [requirements/README.md](requirements/README.md).
Each is one file carrying one obligation, and it declares whether it's
functional or non-functional and which of the four kinds of check verifies it:
a static check, a behavioural fixture, a judgement with its judge named, or a
measured evaluation.

## Decisions

[ADR-1000](adrs/ADR-1000-the-reply-shape-is-a-forced-output-style-in-the-kernel.md)
is approved and in force: the reply shape is a forced output style carried by
the kernel. It is the first turn the design step has run against the
requirements as they now stand.

## Specifications

[SPC-1000](specs/SPC-1000-the-reply-shape.md) states the reply shape. It
carries no `checked-at` until the epic that realises it closes with evidence,
and it says so in its own scope.

## Epics and tasks

[EPC-1000](epics/EPC-1000-the-reply-shape-in-the-kernel.md) is approved and
realises ADR-1000 in five tasks, TSK-1010 to TSK-1050, each filed as an issue
from #5 to #9. TSK-1000 is the planning task that produced all of it.
`tools/check_coverage.py` reports every requirement the decision addresses
landing in exactly one task.

## Defects

None recorded.
