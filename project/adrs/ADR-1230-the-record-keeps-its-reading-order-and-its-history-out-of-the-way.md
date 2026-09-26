---
id: ADR-1230
artifact: adr
status: draft
revised: 2026-09-26
addresses: [REQ-0525, REQ-0530, REQ-0552, REQ-0554, REQ-0555, REQ-2880]
supersedes: []
---

# 1230. The record keeps its reading order, and its history out of the way

## Decision

Three checks join the record's:

- `check index` reads the order in which the specifications' index lists the
  specifications, and reports one listed before a specification it cites, so
  reading the index in order never needs a forward reference. It holds for the
  specifications alone, because a record's index is ordered by identifier.
- `check shape` reports a living document that cites a withdrawn requirement
  outside a section headed Withdrawn, and a directory under the record's root
  named for an archive.
- Three rules on a draft requirement's statement, the paragraph under its
  heading: `one-obligation` reports more than one keyword such as `MUST`,
  `stands-alone` reports a phrase such as "such a record" or "the previous
  step" that leans on a neighbour, and `no-negated-requirement` reports "No X
  MUST Y", which negates a requirement where `MUST NOT` prohibits a behaviour.

The specifications are reordered to meet the first check, and a contract that
names a unit's specification names the unit instead, which breaks the cycles
the check finds. The evidence for what already holds is recorded: the
constitution outranks every artifact, and a superseded record names what
replaced it.

After this decision the specifications read from the bottom layer up, and a
draft requirement carrying two obligations fails the check. What still doesn't
work: 231 approved requirements carry more than one keyword, and the rules
apply to drafts alone, so those wait for the amendment path to split them.

## Why

RES-0012 found the specifications listed in dependency order, with the
layering rule expressed as the ordering of the index, and withdrawn
requirements collected at the end so that none interrupts the reading order.
RES-0011 found a repository that dropped its archive: a directory named for
age holds material nobody reads, which neither freezes nor discards it.
RES-0254 found that one obligation, standing alone, and a prohibition written
as `MUST NOT` are each mechanically checkable, and that sixteen requirements
leaning on a neighbour and twelve negated ones had to be rewritten.

Measured on this record at `21f7790`: five specifications cite a later one,
and SPC-1080 and SPC-1010 sit in citation cycles, because SPC-1080 names each
unit's specification and the contracts SPC-1020 and SPC-1030 name SPC-1010.

The strongest objection: the keyword count reports a statement whose second
`MUST` belongs to the same obligation. It will, and a statement that needs two
keywords is two statements more often than not; the rule applies to drafts,
where splitting costs one edit.

## Alternatives

| Option                                         | Better at                       | Why it lost                                                            |
| ---------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| Three checks, and the specifications reordered | Each property held by a program | Chosen                                                                 |
| Generate the specifications' index in order    | No hand-kept order              | The index is prose the owner writes, and a cycle has no order          |
| Apply the requirement rules to every record    | Finds the 231 now               | An approved requirement is frozen, so the finding can't be fixed       |
| Do nothing                                     | Costs nothing                   | A reader meets forward references, and drafts repeat RES-0254's errors |

## What it costs

An order check in `index`, two findings in `shape`, three draft rules, edits to
three specifications and the index's order, and a task of recorded evidence.

## What would reverse it

- The specifications grow past what one ordered list serves, and the order
  moves into each specification's front matter.

## Consequences

- `check index` fails where a specification is listed before one it cites.
- `check shape` fails on a withdrawn requirement cited in a living document's
  body, and on an archive directory.
- `check rules` fails on a draft requirement carrying two obligations, leaning
  on a neighbour, or negating a requirement.

## How I will know it was realised

1. A fixture lists a specification before one it cites and fails `check
index`, and this repository's index passes.
2. Fixtures show `check shape` reporting a withdrawn requirement in a living
   document's body and an archive directory, and passing one collected under
   Withdrawn.
3. Fixtures show `check rules` reporting each of the three statements in a
   draft requirement, and passing each in an approved one.
4. Each requirement that already holds has its evidence recorded in the task
   that closes it.
5. Every requirement ADR-1230 addresses lands in exactly one closed task.

## What this does not settle

- Splitting the approved requirements that carry two obligations, which the
  amendment path does one at a time.
