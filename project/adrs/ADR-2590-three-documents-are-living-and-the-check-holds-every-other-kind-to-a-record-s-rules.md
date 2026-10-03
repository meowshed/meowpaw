---
id: ADR-2590
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-0610, REQ-0612, REQ-0628, REQ-0632, REQ-2897]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2590. Three documents are living, and the check holds every other kind to a record's rules

## Decision

Exactly three kinds are living: the vision, the constitution and the
specification (REQ-0610). `paw check` already reads `status: live` from front
matter, and it now fails a document of any other kind that declares it. A
living document carries no history: no "previously", no superseded wording
and no tombstone, and the specification states only what the system does now
(REQ-0612, REQ-0632). `paw check` reports a specification that carries
`~~struck~~` text, a tombstone heading or a sentence naming an earlier
version.

A withdrawn record opens its body with a line naming the record that
withdrew it, as REQ-0020's "Withdrawn. Replaced by REQ-3178 and REQ-3180."
does, and `paw check` fails a withdrawn record whose first line names no
identifier (REQ-0628). An epic carries no
per-task status, because the status is derived from the tasks, and
`paw check` fails an epic with a status column or a checkbox per task
(REQ-2897).

Once this is accepted, the record's split into living and frozen kinds is
held by a program. What still doesn't work: "a sentence naming an earlier
version" is matched by a short list of phrases, so a new phrasing passes until
it joins the list.

## Why

RES-0011 found that a document both living and historical gets rewritten
until its history is wrong, and that a withdrawal without its reason loses
the argument while keeping the statement. RES-0256 found that an epic which
carries task status shows a second answer that drifts from the tasks.
CLAUDE.md states the same three living kinds.

## Alternatives

| Option                          | Better at                  | Why it lost                                                        |
| ------------------------------- | -------------------------- | ------------------------------------------------------------------ |
| Do nothing                      | No new rules               | Five requirements rest on review, and a tombstone in a spec passes |
| Let each kind declare its life  | Flexible                   | Extensibility then opts out of the method, against REQ-0670        |
| Keep a history section in specs | A reader sees what changed | Version control keeps the history, and a second copy drifts        |

## What it costs

The phrase list needs a line each time a new way of saying "earlier" gets
through.

## What would reverse it

- A fourth kind turns out to need rewriting in place, such as a living
  glossary, and the three-kind rule blocks it.

## Consequences

`paw check` gains the four rules.

## How I will know it was realised

1. `paw check` fails a fixture requirement with `status: live` (REQ-0610).
2. It fails a fixture specification with a struck-through line (REQ-0632).
3. It fails a withdrawn fixture whose first line names no identifier
   (REQ-0628).
4. It fails a fixture epic with a status per task (REQ-2897).

## What this does not settle

- Whether an approved record that broke these rules before them is migrated.
  The rules apply to drafts, and approved records are excused under method
  rule M15.
