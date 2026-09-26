---
id: SPC-1070
artifact: spec
status: live
revised: 2026-09-26
checked-at:
states:
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
---

# Checking the record

## Scope

This covers `meow-method check`, the program that checks a repository's
record: where it finds the record, the layout it reads it by, what each check
reports, and how it exits.

It leaves declared kinds of a repository's own, transitive coverage, suspect
citations, orphaned artifacts and records that contradict the tree to later
decisions, which ADR-1100 names. The documentation index and links outside the
record are this repository's, and `tools/` keeps checking them.

The harness doesn't implement this yet. ADR-1100 decides it and EPC-1070
realises it, so `checked-at` stays empty until that epic closes.

## Boundary

| Surface                               | What it is                              |
| ------------------------------------- | --------------------------------------- |
| `.meowpaw/profile.toml`, `[record]`   | Where the record lives                  |
| `plugins/meow-method/bin/meow-method` | The program: `check` and `check <name>` |
| `plugins/meow-method/lib/layout.toml` | The record's layout, as data            |
| `docs/meow-method.md`                 | The unit's documentation page           |

## Behaviour

### Where the record lives

```toml
[record]
root = "project"
```

`root` is a path relative to the repository's root, and it may lead outside it,
to a folder or to another repository's checkout (REQ-0520, REQ-0521). Where it
isn't declared, the record is at `project/`. Where the path doesn't exist, the
program says so and checks nothing, and exits 1: a record that can't be found
isn't a clean one.

### The layout

The unit carries the layout `CLAUDE.md` states, as data: for each kind, its
prefix, its directory under `root`, its required front matter fields, its
status vocabulary, the file that indexes it if one does, and the sections it
must carry if any. The kinds are the vision, specifications, research,
requirements, decisions, epics, tasks and defects.

### The checks

| Check        | Reports                                                                                                                               | Replaces                       |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| front matter | A missing field its kind requires, a revision that isn't a past date, and a status outside its kind's vocabulary (REQ-0573, REQ-0590) | `check_front_matter`, extended |
| identifiers  | A file whose name and identifier disagree, an identifier used twice, and a cited requirement that has no file                         | `check_ids`, over every kind   |
| relations    | An identifier in a relation field that doesn't resolve, and a link inside the record whose target doesn't exist (REQ-0656)            | new                            |
| index        | A file its kind's index doesn't list, and an index entry with no file (REQ-0524)                                                      | new                            |
| coverage     | A requirement a decision addresses in no task or in two, and one in force that no specification states (REQ-0246)                     | `check_coverage`               |
| shape        | An artifact missing a section its kind requires, research's summary and conclusions among them (REQ-0145)                             | `check_research`               |

Each finding names the file, and the line where there is one. `meow-method
check` runs every check and exits 0 when none found anything and 1 when any
did. `meow-method check <name>` runs one. No check writes a file (REQ-0137).

### This repository

`.meowpaw/profile.toml` declares `root = "project"`, and the `test` verb runs
`meow-method check` in place of the four scripts it replaces, which are
deleted (REQ-1673). `tools/check_index.py`, `tools/check_links.py` and the
checks over the harness's own units stay.

### The interpreter

The program needs Python 3.11 or later, like the other units. Where it is
missing, the launcher says the record was not checked and exits 3, never 0.

## Failure paths

| Condition                            | What happens                                          |
| ------------------------------------ | ----------------------------------------------------- |
| No profile, or no `[record]` table   | The record is looked for at `project/`                |
| `root` doesn't exist                 | Nothing is checked; the missing path is named, exit 1 |
| A file of no known kind under `root` | Reported as an artifact of no known kind              |
| An unknown check named               | An error naming the six checks, exit 2                |
| No Python 3.11 or later              | The record is reported as not checked, exit 3         |
