# meow-method

`meow-method` checks your repository's record: the research, requirements,
decisions, specifications, epics, tasks and defects the method keeps. It reads
the record where you declare it, reports each finding with its file and line,
and writes nothing. It installs on its own, with no other part of the
`meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-method@meowpaw
```

## Declare where the record lives

Put it under `[record]` in `.meowpaw/profile.toml` at the repository's root:

```toml
[record]
root = "project"
```

`root` is relative to the repository's root, and it may lead outside it, to a
folder or to another repository's checkout. Where you declare none, the record
is at `project/`.

## Run it

From the repository, run every check, or one by name:

```bash
meow-method check
meow-method check relations
```

A run with one finding prints it and each check's count:

```text
project/tasks/TSK-0001-a-task.md:4: status done is not one a task stores: draft, approved, withdrawn, rejected, superseded
front-matter: 1 findings
identifiers: 0 findings
relations: 0 findings
index: 0 findings
coverage: 0 findings
shape: 0 findings
```

| Check          | Reports                                                                                      |
| -------------- | -------------------------------------------------------------------------------------------- |
| `front-matter` | A field the kind requires that's missing, a status the kind doesn't store, a bad `revised`   |
| `identifiers`  | A file whose name and `id` disagree, an identifier used twice, a cited requirement not found |
| `relations`    | An identifier in a relation field with no file, and a link in the record to a missing file   |
| `index`        | A file its kind's index doesn't list, and an index entry with no file                        |
| `coverage`     | A requirement a decision addresses that lands in no task or in two, or no specification      |
| `shape`        | An artifact missing a section its kind carries, such as research without its conclusions     |

It exits 0 when no check found anything, 1 when any did or the root doesn't
exist, 2 for a check it doesn't know, and 3 when the record wasn't checked.

## What it costs you

Nothing in context: the unit ships a program and no skill, hook or style. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, it
reports the record as not checked and exits 3.

## Where the rules come from

The decision is
`project/adrs/ADR-1100-the-record-is-checked-by-a-unit-the-harness-ships.md`,
and the unit is specified in `project/specs/SPC-1070-checking-the-record.md`.
The layout it reads each kind by is `plugins/meow-method/lib/layout.toml`.
