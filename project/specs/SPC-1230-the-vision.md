---
id: SPC-1230
artifact: spec
status: live
revised: 2026-10-03
states:
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
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The vision

## Scope

This covers a project's vision, `vision.md` at the record's root: the sections
it carries, what `paw check` reports in it and the two questions the design
step asks of a decision that touches it.

It leaves the record's other kinds and the rules every living document shares
to SPC-1070, and the constitution to its own specification.

ADR-2580 decides it, and EPC-2450 realises it.

## Boundary

| Surface                                           | What it is                                                   |
| ------------------------------------------------- | ------------------------------------------------------------ |
| `<record root>/vision.md`                         | The project's one vision                                     |
| `plugins/meow-flow/templates/vision.md`           | The template `paw template vision` names                     |
| `paw check`                                       | Reports a missing section, a date, a requirement or a length |
| `plugins/meow-flow/skills/method/steps/design.md` | Asks a decision whether its vision claims hold               |

## Behaviour

### One vision, with its sections

A project has one vision, at the record's root, and an epic that changes it
edits that file and keeps no copy (REQ-0614), so `paw check`'s `identifiers`
check reports a second file carrying `id: vision` as the identifier used
twice. The template carries a section
for each thing a vision states, and `paw check`'s `shape` check reports a
vision missing one of them:

| Section             | What it states                                                                        |
| ------------------- | ------------------------------------------------------------------------------------- |
| Who it is for       | The people the project is for (REQ-0616), and what each does today instead (REQ-0618) |
| Quality goals       | The quality goals in priority order, with ties broken (REQ-2850)                      |
| What it will not do | The non-goals, so a proposal can be refused by citing one (REQ-0620)                  |
| Risks               | The risks that are live now (REQ-2854)                                                |

The template's other sections, What it is, The problem and Where it is going,
stay optional for the check.

### What `paw check` reports

`paw check`'s `rules` check reports, naming the file and the line:

- a date in the body, in the form `YYYY-MM-DD`, a month named with a year, or
  a quarter with a year such as `Q3 2026`, because a vision carries no
  roadmap and no dates (REQ-2856); the `revised` field in the front matter is
  exempt;
- a sentence that holds a requirement's identifier together with `MUST`,
  `MUST NOT`, `SHALL` or `SHOULD`, because a vision restates no requirement
  (REQ-2857);
- a body over 2,000 words, counted without the front matter and fenced code,
  because a vision nobody reads in one sitting settles no argument (REQ-0611).

### What the design step asks

Each claim in the vision is made falsifiable by a requirement or removed
(REQ-2852). That is a judgement, so the design step asks it of every decision
that changes the vision. Where a decision contradicts the vision, the design
step reports that one of the two is stale, asks which and doesn't write the
decision with both in force (REQ-0624).

## Failure paths

| Condition                                   | What happens                                                         |
| ------------------------------------------- | -------------------------------------------------------------------- |
| The vision lacks a required section         | `shape` reports it, naming the section                               |
| A date in the vision's body                 | `rules` reports it, naming the line                                  |
| A requirement stated as an obligation in it | `rules` reports it, naming the line and the identifier               |
| A body over 2,000 words                     | `rules` reports it with the count                                    |
| No `vision.md` at the record's root         | Nothing is reported for it, because a record may keep no vision      |
| A decision contradicts the vision           | The design step reports one as stale and asks which, writing neither |
