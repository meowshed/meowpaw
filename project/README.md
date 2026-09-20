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

125 documents, indexed by
[RES-0001-synthesis.md](research/RES-0001-synthesis.md), which everything
downstream cites.

## Requirements

1,037 obligations, indexed by [requirements/README.md](requirements/README.md).
Each is one file carrying one obligation, and it declares whether it's
functional or non-functional and which of the four kinds of check verifies it:
a static check, a behavioural fixture, a judgement with its judge named, or a
measured evaluation.

## Decisions

None in force, as [adrs/README.md](adrs/README.md) records. The design step
hasn't run against the requirements as they now stand.

## Specifications and epics

Not written. Both come from decisions, and there are none.

## Defects

None recorded.
