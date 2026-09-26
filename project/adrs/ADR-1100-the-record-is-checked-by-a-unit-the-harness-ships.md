---
id: ADR-1100
artifact: adr
status: draft
revised: 2026-09-26
addresses:
  [
    REQ-0137,
    REQ-0145,
    REQ-0246,
    REQ-0520,
    REQ-0521,
    REQ-0524,
    REQ-0573,
    REQ-0590,
    REQ-0656,
    REQ-1673,
  ]
supersedes: []
---

# 1100. The record is checked by a unit the harness ships

## Decision

A new unit, `meow-method`, starts the method layer with the checks over the
record. Its program, `meow-method check`, reads a repository's record where the
repository declares it lives, reports every finding, and changes nothing
(REQ-0137):

```toml
[record]
root = "project"
```

`root` is a path relative to the repository's root, and it may lead outside
it, to a folder or to another repository's checkout (REQ-0520, REQ-0521).
Where it isn't declared, the record is at `project/`, the layout this
repository uses.

The checks are the ones `tools/` carries today, moved into the unit and
reading the record from `root`:

| Check        | Reports                                                                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| front matter | Metadata that breaks its kind's schema, and a status outside its kind's vocabulary (REQ-0573, REQ-0590)                                                                        |
| identifiers  | A duplicate identifier, and a file whose name doesn't match its identifier                                                                                                     |
| relations    | A relation or a link whose target doesn't resolve (REQ-0656)                                                                                                                   |
| index        | An index entry with no file, and a file with no index entry (REQ-0524)                                                                                                         |
| coverage     | A requirement a decision addresses that lands in no task or in two, and a requirement in force that no specification states, or a statement citing one not in force (REQ-0246) |
| shape        | An artifact missing a section its kind requires (REQ-0145)                                                                                                                     |

Each check reports its findings with the file and the line, and the program
exits 0 when there are none and 1 when there are any. `meow-method check
<name>` runs one check.

The unit carries the record's layout as data: each kind's prefix, directory,
required fields, status vocabulary and required sections. The layout is the
one `CLAUDE.md` states, and a later decision lets a repository declare kinds of
its own.

This repository's `test` verb runs `meow-method check` in place of the record
checks in `tools/`, which are then deleted, so the harness verifies its own
repository with a mechanism it ships (REQ-1673). The checks in `tools/` over
the harness's own units, for prompts, the kernel, budgets, the style and the
reply shape a subordinate agent carries, stay: they check what the harness
ships, not a record.

## Why

`CLAUDE.md` says of the record checks that they come back "as part of the
harness rather than beside it, because a harness checked by a mechanism it
doesn't ship hasn't been shown to work", and REQ-1673 requires it. Today a
repository that installs the harness gets none of them, and this repository's
own checks run from a folder no other repository has.

The record is the core of what the harness claims, and its checks are
mechanical, so a program carries them and fixtures test them, with no model
involved. Moving the existing checks first, before any record kind or step of
the chain, gives the method layer a working first increment that this
repository uses on the day it lands.

## Alternatives

| Option                                                | Better at                                        | Why it lost                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Move the existing checks into a unit, layout as data  | Working the day it lands, here and elsewhere     | Chosen                                                                                        |
| Leave the checks in `tools/`                          | Costing nothing                                  | REQ-1673 fails, and no other repository gets them                                             |
| Start with the record kinds and templates             | Giving a repository the record before its checks | A record nothing checks drifts from the start, which is the failure the method exists to stop |
| Write new checks from the requirements, not the tools | Checking what the requirements ask and no more   | The tools already pass on this record and caught real defects; rewriting them loses that      |
| One check per unit                                    | Installing only the checks a repository wants    | Six units for one layout, and the layout would be stated six times                            |

## What it costs

One more unit, with no skill yet and so nothing in context. The program needs
the interpreter the other units already use.

The layout moves from six scripts into one table the unit owns. A repository
whose record doesn't follow it gets findings for every difference until a
later decision lets it declare its own kinds.

The checks that remain in `tools/` still run beside the harness. They check
the harness's own units, which no other repository has.

## What would reverse it

- A repository adopting the harness finds the built-in layout wrong for its
  record often enough that declaring kinds has to come first.
- The record moves to a store the unit can't read as files, such as a tracker,
  and the checks have to read through it.

## Consequences

- `plugins/meow-method/` carries the program, the layout, fixtures, a manifest,
  a budget and a documentation page, and the marketplace lists it.
- A specification for checking the record states `[record]`, the layout and
  each check.
- This repository declares `root = "project"`, its `test` verb runs `meow-method
check`, and the six record checks in `tools/` are deleted.
- `CLAUDE.md`'s gate section names the unit where it names the scripts.

## How I will know it was realised

1. Each check reports a planted defect in a scratch record, with the file and
   the line, and reports nothing on a clean record.
2. With `root` pointing outside the repository, the checks read the record
   there.
3. The program changes no file: the tree is identical before and after a run.
4. On this repository, `meow-method check` reports what the six scripts in
   `tools/` report at the same revision, and nothing else.
5. The six record checks in `tools/` are gone, and this repository's `test`
   verb runs `meow-method check` and passes.

Each is a fixture or a run of a command, and none needs a model.

## What this does not settle

- Declared kinds, prefixes and vocabularies of a repository's own (REQ-0667 and
  the kinds requirements).
- Transitive coverage, suspect citations, orphaned artifacts and records that
  contradict the tree (REQ-0139, REQ-0141, REQ-0143, REQ-0704).
- A record kept in another repository that isn't checked out beside this one.
- The record's templates and the steps of the chain.
