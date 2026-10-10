---
id: RES-0348
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The record costs its writes and not its reads, so commands for the writes answer the question and a database doesn't

## Summary

The record is 2,060 files and 6.3 MB, and the tool reads all of it in 2.4
seconds for a full check and in 0.01 seconds for a search, so reading doesn't
justify a database. Writing does cost: 94% of the commits since 2026-09-20 touch
the record, 51% touch three or more record files, and 54% touch an index page.
A write that implies several files, closing a task, is still done by hand, and
the check or the gate has caught it wrong at least three times in a day. Commands
that make each such write one step keep the files, the diffs and the frozen
check, and take the cost away.

The document covers the record's storage and its writes. It doesn't cover the
tracker, which is a separate question.

## The question

Should the record move from one file for each artifact to a flat database, or
to SQLite, with the tool as its only interface?

The assumption behind the question is that the number of files is the cost. The
data below says the cost sits in the writes that cross files, and a database
removes that only by removing what makes the record reviewable.

## Method

I counted the files, bytes and lines under `project/` with `git ls-files`, and
timed `paw check`, `paw status` and `paw find` on a warm tree on 2026-10-10. I
classified the 506 commits since 2026-09-20 with `git log --name-only`, by
whether they touch `project/`, how many record files they touch, and whether
they touch an index page. I read the rules the record states about storage:
`CLAUDE.md` (the layout table and `living_and_record`), the vision (line 212),
REQ-0030, REQ-0575, REQ-1402 and ADR-1180. I did not run a database or a
benchmark of one, and I did not time a person's edits.

## Findings

### Reading takes seconds

The record holds 2,060 tracked files, 6,299,883 bytes and 122,266 lines:
1,226 requirements, 344 tasks, 165 research documents, 130 decisions, 106 epics,
62 defects and 25 specifications. `paw check` took 2.44 seconds, `paw status`
1.30 and `paw find stage` 0.01.

### Writing crosses files

Of the 506 commits since 2026-09-20, 477 touch `project/`, 256 of those touch
three or more record files outside the index pages, and 275 touch an index
page. Closing one task is a status change in the task, a mark in the epic or
the defect, a `done` in the epic and the decision when it was the last task,
and a regenerated index.

### The gate and the check catch the writes that go wrong

On 2026-10-09 and 2026-10-10 the gate or `paw check` rejected a task that was
complete and stored `approved` (TSK-5240), an epic that left a written task
unmarked (TSK-5270), and a record whose citation was suspect after an edit.
The history carries 14 commits whose subject says a record was marked done,
closed or corrected after the change that completed it.

### The rules the record states keep it as files

The layout table names "one artifact per file" and the vision promises plain
Markdown with no tracker and no database. REQ-0030 asks that the record be
usable without the tool, REQ-1402 that its projection onto a tracker be made by
ordinary commands, and `paw check frozen` reads each approved artifact's diff
against its base, a per-file operation.

### Indexes are already generated

REQ-0575 and ADR-1180 make each kind's index a program's output, and `check
index` fails drift. The pages written by hand are `project/README.md`'s prose
and rows for epics and defects, and `RES-0001-synthesis.md`.

## Comparison

| Option                                      | Better at                                               | Why it falls short                                                           |
| ------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Keep the files, add commands for the writes | Keeps diffs, frozen check, editor reading; fixes writes | Two ways to edit, and the commands must track the templates                  |
| One flat database in one file               | One place, one atomic write                             | One diff for every change, a conflict on every parallel pull request         |
| SQLite                                      | Queries, transactions                                   | A binary file git can't diff or review, and a tool needed to read the record |
| Do nothing                                  | No work                                                 | The writes stay by hand, with 14 corrections in three weeks                  |

## The case against the commands

A command is a second way to write a record, and the hand edit stays possible,
so a person who edits by hand and a command that edits the same fields can
disagree about the form. The commands must write what the templates and `paw
check` accept and nothing else, which means each command is tested against the
check. A record kept in files is also read by `grep` and an editor, and a
command that rewrote a file wholesale would lose that, so a command changes the
lines it owns and leaves the rest.

## Conclusions

1. The record stays one artifact for each file, plain Markdown, and a database
   is not adopted (Findings: reading takes seconds; the rules the record states
   keep it as files).
2. A status change is one command that edits every file it implies and
   regenerates the index, so closing a task is a single step (Findings: writing
   crosses files; the gate and the check catch the writes that go wrong).
3. Each such command writes only what `paw check` accepts, and leaves every
   other line of a file as it was (The case against the commands).
4. A hand edit stays valid, and a command's result passes `paw check` without
   the command (Findings: the rules the record states keep it as files).

## Sources

- `git ls-files project`, `git log --since=2026-09-20 --name-only` and `paw check`, `paw status`, `paw find` on the tree at pull request 880, run 2026-10-10 - the counts and times.
- `CLAUDE.md`, layout table and the principles `living_and_record` and `reviewable_history`, as of pull request 880, read 2026-10-10 - one artifact per file.
- `project/vision.md` line 212, as of pull request 880, read 2026-10-10 - plain Markdown, no database.
- `project/requirements/REQ-0030-*.md`, `REQ-0575-*.md` and `REQ-1402-*.md`, as of pull request 880, read 2026-10-10 - the record without the tool, generated indexes, projection by ordinary commands.
