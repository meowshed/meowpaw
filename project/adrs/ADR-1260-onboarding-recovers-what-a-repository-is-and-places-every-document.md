---
id: ADR-1260
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [
    REQ-1540,
    REQ-1542,
    REQ-1544,
    REQ-1546,
    REQ-1548,
    REQ-1550,
    REQ-1552,
    REQ-1556,
    REQ-1558,
    REQ-3092,
    REQ-3094,
    REQ-3096,
  ]
supersedes: []
---

# 1260. Onboarding recovers what a repository is, and places every document it already has

## Decision

`meow-method` gains `/meow-method:onboard`, a command only a person invokes,
run after `/meow-method:init`. It reads the repository's documentation, any
harness it already has, and its code, and writes:

- the vision, the specifications and, where the repository has no
  `CLAUDE.md`, the constitution, each recovered statement ending with the file
  it came from and a confidence of high, medium or low, and anything it can't
  trace to a file dropped;
- no requirement and no decision, because code shows what a system does and
  never what it must do, nor which alternatives lost;
- an onboarding report, `onboarding.md` at the record's root, a new kind of
  record opening with which verbs resolve, then the conventions observed, each
  as a frequency offered as a decision, the disposition of every document the
  repository already has, the gaps, and adoption as numbered steps that each
  leave the repository working.

The report is a draft, and the command stops there for approval. It rewrites
no existing file, and reads an existing harness in full as evidence before
placing it.

`check coverage` holds the disposition: each document the repository tracks
outside the record gets exactly one outcome in the report, migrated, cited,
superseded or discarded, with where it went or why, so nothing is deleted
before it is placed. `check rules` holds the adoption section's numbered
steps.

After this decision a repository can be brought into the method with its
documents accounted for, and the gap list is the input to the requirements
step. What still doesn't work: the record starts with no requirements, and
says its coverage is zero until a person affirms each one through the
requirements step, which is the design and not a gap in it.

## Why

RES-0037 found that the specification is recovered and requirements and
decisions are not, that every recovered statement is traceable to a file with
its confidence marked, that gaps are a deliverable, that an existing harness
carries principles whose reasons nothing else in the repository has, that
nothing is deleted before it is placed, and that onboarding stops at approval.
RES-0154 found that the record starts nearly empty and says so, that a
convention is a frequency offered as a decision, that adoption is a sequence
of working steps, that no existing file is rewritten, and that onboarding asks
what a repository already is where initialisation asks what it should be.

The strongest objection: a report whose disposition the program checks costs
the person a table of every document before anything useful happens. It does,
and RES-0037 found that deleting before placing is how an onboarding loses
what a repository knew; a table is the cheapest way to show nothing was lost.

## Alternatives

| Option                                          | Better at                      | Why it lost                                                          |
| ----------------------------------------------- | ------------------------------ | -------------------------------------------------------------------- |
| A command, a report kind, a checked disposition | Every document placed, checked | Chosen                                                               |
| Generate requirements from the code             | A full record at once          | A reconstruction wearing a record's clothes, which REQ-1544 forbids  |
| Onboarding folded into init                     | One command                    | Init asks what a repository should be, onboarding what it already is |
| Do nothing                                      | Costs nothing                  | Existing documents stay outside the record, or are lost moving in    |

## What it costs

A command with its rules, a report kind with its template, a disposition check
in `coverage` and an adoption rule.

## What would reverse it

- Onboarding runs show the disposition table is never read, and it moves into
  the gap list.

## Consequences

- `/meow-method:onboard` exists, and `meow-method template onboarding` prints
  the report's template.
- `check coverage` reports a tracked document with no outcome or with two, an
  outcome outside the four, and one naming no destination or reason.
- `check rules` reports an adoption section that isn't numbered steps.

## How I will know it was realised

1. Fixtures show `check coverage` reporting a document the report doesn't
   place, one placed twice, an unknown outcome and a discard with no reason,
   and passing a report that places every document once.
2. A fixture shows `check rules` reporting an Adoption section without
   numbered steps.
3. `/meow-method:onboard` carries `disable-model-invocation`, and each rule
   ADR-1260 places in it maps to its requirement in the task that closes it.
4. Every requirement ADR-1260 addresses lands in exactly one closed task.

## What this does not settle

- Measuring whether a model recovers statements faithfully, which waits for
  evaluation.
