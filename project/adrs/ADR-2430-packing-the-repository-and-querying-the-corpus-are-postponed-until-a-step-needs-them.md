---
id: ADR-2430
artifact: adr
status: approved
revised: 2026-10-03
addresses: []
postpones:
  [
    REQ-2362,
    REQ-2366,
    REQ-2598,
    REQ-2600,
    REQ-2602,
    REQ-2604,
    REQ-2606,
    REQ-2607,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2430. Packing the repository and querying the corpus are postponed until a step needs them

## Decision

I postpone the requirements for a repository packer and a document query
tool: REQ-2362 and REQ-2598 to REQ-2607 for the packer, REQ-2366 for the query
tool. No step of the method packs a repository for a model or queries the
corpus through an index, and `paw find` reads the record exhaustively
(ADR-2410). Each requirement keeps its wording and reads as postponed, with
this record's condition, in `paw status`.

The rule these requirements guard still holds without them: CLAUDE.md's
`never_touch_secrets` forbids reading, printing or sending secret material,
whatever a packer's filter says.

Once this is accepted, eight requirements stop reading as work nobody has
started, and the loop doesn't pick them. What still doesn't work: the harness
can't pack a repository or query the corpus.

## Why

RES-0142 found repomix's credential check is a filter and not a proof, and
RES-0141 found qmd's index answers for one machine. Both findings guard a use
the harness doesn't have. Building a pack unit for a step that doesn't exist
writes code no step calls, and ADR-1330 lets a decision postpone requirements
with a condition.

## Alternatives

| Option                       | Better at                                  | Why it lost                                                    |
| ---------------------------- | ------------------------------------------ | -------------------------------------------------------------- |
| Do nothing                   | No record                                  | The eight requirements read as open work nobody owns           |
| Build a repomix and qmd pack | The capability exists when a step wants it | No step calls it, so nothing exercises the rules it carries    |
| Withdraw the requirements    | A smaller record                           | The findings stay true and the next step that packs needs them |

## What it costs

A person who wants a repository packed for a model does it by hand, outside
the harness, with none of these checks.

## What would reverse it

- A step of the method needs the whole repository or the whole corpus read
  by a model in one go, or the owner asks for a packer or a query tool.

## Consequences

`paw status` lists the eight requirements under Postponed with the condition
above.

## How I will know it was realised

1. `paw status` lists REQ-2362, REQ-2366 and REQ-2598 to REQ-2607 as postponed
   by ADR-2430.

## What this does not settle

- Which packer or query tool the harness would adopt.
