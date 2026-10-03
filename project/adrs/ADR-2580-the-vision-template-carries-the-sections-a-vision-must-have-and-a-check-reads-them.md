---
id: ADR-2580
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-0611,
    REQ-0614,
    REQ-0616,
    REQ-0618,
    REQ-0620,
    REQ-0624,
    REQ-2850,
    REQ-2852,
    REQ-2854,
    REQ-2856,
    REQ-2857,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2580. The vision template carries the sections a vision must have, and a check reads them

## Decision

A project has one vision, at the record root, and an epic updates it
and keeps no copy (REQ-0614). Its template, `paw template vision`, carries a
section for each thing a vision must state: who the project is for
(REQ-0616), what those people do today instead (REQ-0618), what the project
won't do (REQ-0620), the quality goals in priority order with ties broken
(REQ-2850), and the risks that are live now (REQ-2854).

`paw check` gains a vision rule. It reports a vision missing one of those
sections, a vision that carries a date or a dated plan (REQ-2856), a
requirement identifier stated as an obligation in it (REQ-2857), and a vision
over 2,000 words, because a vision nobody can read in one sitting settles no
argument (REQ-0611).

Each claim in the vision either is made falsifiable by a requirement or is
removed (REQ-2852). That is a judgement, so the design step's file asks it of
every decision that changes the vision. Where a decision contradicts the
vision, the design step reports that one of the two is stale and asks which,
and doesn't proceed with both (REQ-0624).

Once this is accepted, a vision is checked for its sections like any other
record. What still doesn't work: this repository's `project/vision.md` has no
section for quality goals or live risks, and its "Where it is going" section
reads as a plan, so the first run reports it and a task rewrites it.

## Why

RES-0035 found that a vision without an audience, an alternative and
non-goals can't be cited against a proposal, and that one too long to
re-read stops being consulted. RES-0251 found that a vision carrying a
roadmap goes wrong on a schedule, and that quality goals without an order
can't settle a trade-off. The 2,000-word figure is my choice for "one
sitting", about ten minutes of reading.

## Alternatives

| Option                      | Better at                   | Why it lost                                                |
| --------------------------- | --------------------------- | ---------------------------------------------------------- |
| Do nothing                  | No check                    | Eleven requirements rest on review of a living document    |
| A rubric judged by an agent | Reads meaning, not headings | Method rule M19 dispatches no agent to review a record     |
| No length limit             | Nothing cut to fit          | A vision nobody re-reads settles nothing, as REQ-0611 says |

## What it costs

This repository's vision gets rewritten to the template, and every later
change to it has to keep the sections.

## What would reverse it

- The check reports a missing section more often for a vision that people
  read and cite than for one they don't, which would show the sections are
  the wrong ones.

## Consequences

The vision template gains its sections. `paw check` gains the vision rule. A
task rewrites `project/vision.md`.

## How I will know it was realised

1. `paw check` reports a fixture vision with no non-goals section (REQ-0620).
2. It reports a fixture vision with a date in it (REQ-2856).
3. It reports a fixture vision over 2,000 words (REQ-0611).

## What this does not settle

- What this repository's quality goals are, which the rewrite decides.
