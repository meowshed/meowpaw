---
id: ADR-1150
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0237,
    REQ-0638,
    REQ-0640,
    REQ-0642,
    REQ-0644,
    REQ-0646,
    REQ-0648,
    REQ-0650,
    REQ-0652,
    REQ-0654,
    REQ-0658,
    REQ-0692,
    REQ-0698,
    REQ-0700,
    REQ-0702,
  ]
supersedes: []
---

# 1150. The record answers what an identifier is and what cites it, and a closed task carries its evidence

## Decision

`meow record show <id>` resolves an identifier to its artifact and prints its
path, kind, stored status and title, the identifiers it names in each relation
field, and every artifact that cites it, grouped by the field or the body that
cites it. The downward direction is computed each time it runs, from the upward
relations every artifact authors, so nobody keeps a reverse list. A withdrawn or
superseded artifact still resolves, and `show` prints its status, so an
identifier resolves forever.

Three rules join the epic's in `lib/layout.toml`, for every record:

- `done-has-evidence`: a task an epic marks `[x]` has an `## Evidence` section
  with more than "Not yet.".
- `added-says-why`: a task marked `[+]` carries an `added:` line saying why
  nobody foresaw it.
- `dropped-says-why`: a task marked `[~]` keeps its entry with a `dropped:` line
  saying why.

The relations stay as they are: bare identifiers in front matter, one fixed
vocabulary the layout names, authored only upward and each resolving, which the
relations check already holds. This decision records that they meet REQ-0237
and REQ-0638 to REQ-0648 and REQ-0654, with a fixture for each.

After this decision a person or a step asks the program what an identifier is
and what depends on it, where today they search the tree by hand, and an epic
can't mark a task done that carries no evidence. What still doesn't work:
`show` reads the record only, so a check or a test naming a requirement isn't
listed as citing it, and whether the work landed for a task still unmarked
isn't checked.

## Why

RES-0036 found that every bidirectional-link system authors relations upward
and derives them downward, and RES-0019 found that tooling over a structured
Markdown corpus answers queries with identifiers first. REQ-0652 asks for both
directions from one identifier, and REQ-0650 asks that the downward one be
derived, because the author of a record can't know what will later cite it.

The three rules are sections and lines a program settles, as REQ-2694 asks.
The probe of this repository on 2026-09-26 found no task marked done without
evidence once a leading "Not yet." is allowed to precede it, and no `[+]` or
`[~]` entry at all, so each rule holds on every record, frozen or not.

The strongest objection: `show` duplicates `grep`. It doesn't, because `grep`
finds text and not relations: it can't tell a citation in `closes` from a
mention in prose, and it can't group what it found by the field that holds it.

## Alternatives

| Option                                                  | Better at                               | Why it lost                                                                         |
| ------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------- |
| `show`, computing both directions each run              | Nothing to keep in step; always current | Chosen                                                                              |
| A generated reverse index committed to the tree         | Readable without the program            | A second source of the same fact, which drifts the first time nobody regenerates it |
| Downward relations authored by hand on the cited record | No program                              | REQ-0650 forbids it: the earlier record can't know its later citers                 |
| Do nothing: search with `grep`                          | Costs nothing                           | Finds text, not relations, and misses the field a citation sits in                  |

## What it costs

A subcommand and its fixtures in the crate, three named rules and theirs, and
an entry in the documentation.

## What would reverse it

- The record grows past what one read of the tree answers in about a second, and
  a cached index becomes worth its drift.
- A later decision derives the task marks from the tasks' own state, and the
  three rules move to the task.

## Consequences

- `meow record show` exists, with fixtures, and SPC-1100 states it.
- The epic kind's `rules` gain `done-has-evidence`, `added-says-why` and
  `dropped-says-why`, and SPC-1070 lists them.

## How I will know it was realised

1. `meow-method show REQ-0190` prints its path, status and title, and lists
   ADR-1130 under `addresses` and SPC-1090 under `states` among what cites it.
2. `show` on a withdrawn requirement prints it as withdrawn.
3. An epic marking a task `[x]` whose evidence is only "Not yet." fails `check
rules`, naming the task.
4. `meow-method check` on this repository reports 0 findings.

## What this does not settle

- Listing the checks and tests that name a requirement, which live outside the
  record.
- Whether work that landed belongs to a task still unmarked.
- Generating the indexes from the tree.
