---
id: ADR-1310
artifact: adr
status: done
revised: 2026-09-26
addresses:
  [
    REQ-1350,
    REQ-1351,
    REQ-1352,
    REQ-1353,
    REQ-1354,
    REQ-1355,
    REQ-1356,
    REQ-1360,
    REQ-1368,
    REQ-1372,
    REQ-1376,
    REQ-1378,
    REQ-1380,
    REQ-1382,
    REQ-1384,
    REQ-1386,
    REQ-1388,
    REQ-1392,
    REQ-1394,
    REQ-1396,
    REQ-1400,
    REQ-1402,
  ]
supersedes: []
---

# 1310. The GitHub pack projects an approved epic's tasks onto issues, and reports where the two disagree

**Amended by ADR-2890.** An issue edited on GitHub is applied to the record where only it changed and the record is a draft, and reported otherwise.

## Decision

`meow-github project <epic>` projects an approved epic's tasks onto GitHub
issues, one issue per task, and `meow-github project --check <epic>` reports
the state of each without writing:

- The repository declares its tracker in `.meowpaw/profile.toml` as
  `[tracker] kind = "github"`; with none declared, the command says so and
  does nothing, and no step of the method depends on a tracker.
- It projects only an approved epic. Each issue's title is the task's
  identifier and title, and its body cites the epic, the requirements the task
  closes by identifier, and the task's dependencies with their reasons, and
  ends with a marker naming the task and the fingerprint it was projected at,
  so a write from a synchronisation is marked as one.
- The mapping lives on the task: `issue:` holds the issue's number and
  `projected:` the fingerprint of what was projected, and nothing else keeps
  it. It reads each issue it created back from GitHub and reports one whose
  title or body isn't what it wrote.
- A task whose fingerprint matches its `projected:` and whose issue still
  reads as projected needs nothing, so a second run changes nothing. A task
  changed since it was projected updates its issue, because the record owns
  the title and the body. An issue edited on GitHub while the task is
  unchanged is reported, never overwritten, and an issue closed on GitHub
  while the epic leaves its task unmarked is reported as a disagreement. The
  issue's open or closed state belongs to the tracker, and the pack never
  writes it.
- It polls when run and waits for no notification.

`meow-method check frozen` lets an approved task's `projected:` change, as it
lets `issue:` change. The docs give the `gh` commands that produce the same
issue and the same two fields by hand.

After this decision a repository that uses GitHub gets one issue per approved
task, kept in step with the record by a command it can replay. What still
doesn't work: the epic doesn't project onto a milestone or a project board,
and a dependency isn't marked blocking or not on the tracker.

## Why

RES-0025 found that the record is the system of record and the tracker a
projection, that a program performs the sync deterministically and
idempotently, that conflict authority is per field with disagreement on a
repository field reported and never merged, that the mapping lives on the task
with sync state computed from a fingerprint, that writes flow record to
tracker with done the one exception, that echo suppression is explicit, and
that it polls on demand. RES-0022 found that a keyword in a description is a
claim and the tracker's view of the link is the fact, so a link is read back.

This repository files each task as an issue today through a script outside
the harness; the pack does what that script does, from the harness.

The strongest objection: updating an issue whenever its task changes can
overwrite a note someone added on GitHub. It can't: the pack compares the
issue with what it last wrote, and an issue someone edited is reported and
left as it is.

## Alternatives

| Option                                              | Better at                                   | Why it lost                                                  |
| --------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| A pack command, mapping and fingerprint on the task | Replayable, recoverable from the repository | Chosen                                                       |
| A registry file mapping tasks to issues             | One place to look                           | Outlives the tasks it maps, which REQ-1382 forbids           |
| The model files issues from a prompt                | Nothing to build                            | Neither deterministic nor idempotent, which REQ-1355 forbids |
| Do nothing                                          | Costs nothing                               | Work items stay a script outside the harness                 |

## What it costs

A `project` command with a check mode in the pack, a profile section, a field
the frozen check allows, and a docs section.

## What would reverse it

- A second tracker arrives, and the projection's fields move into a mapping
  both packs read.

## Consequences

- `meow-github project` and `project --check` exist.
- A projected task carries `issue:` and `projected:`.

## How I will know it was realised

1. Fixtures with a stand-in `gh` show `project` creating one issue per task of
   an approved epic, citing its requirements and dependencies and carrying the
   marker, writing `issue:` and `projected:`, reading each back, refusing a
   draft epic, and changing nothing on a second run.
2. Fixtures show a changed task updating its issue, an edited issue reported
   and not overwritten, and a closed issue on an unmarked task reported, with
   `--check` writing nothing.
3. A fixture shows a profile with no tracker reported with nothing done, and
   `check frozen` passing an approved task whose `projected:` changed.
4. Every requirement ADR-1310 addresses lands in exactly one closed task.

## What this does not settle

- Projecting the epic onto a milestone or a board.
- Marking a dependency blocking or not on the tracker.
