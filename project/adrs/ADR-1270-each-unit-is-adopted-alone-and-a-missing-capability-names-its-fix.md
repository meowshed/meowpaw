---
id: ADR-1270
artifact: adr
status: approved
revised: 2026-09-26
addresses:
  [
    REQ-0010,
    REQ-0012,
    REQ-0014,
    REQ-0016,
    REQ-0018,
    REQ-0022,
    REQ-0024,
    REQ-0026,
    REQ-0028,
    REQ-0030,
    REQ-0034,
    REQ-0036,
    REQ-0038,
    REQ-0040,
  ]
supersedes: []
---

# 1270. Each unit is adopted alone, and a missing capability names what would supply it

## Decision

A repository adopts any subset of the units, and each unit is a working
harness on its own. Two things change so that holds by check and not by
habit:

- A check, `tools/check_standalone.py`, reads every file a unit ships and
  reports a path that leaves the unit's own directory, through
  `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}` or a relative climb, and
  any reference to another unit's directory. A unit may name another unit in
  prose, as something to install, never as a path it runs. The docs index
  states the adoption levels: each unit alone, in any combination.
- Every report of a capability that isn't available names what would make it
  available. An undeclared verb says to declare it under `[verbs]` in
  `.meowpaw/profile.toml`, a verb whose value isn't one command says to write
  one, and a launcher that finds no binary for the machine names the machine
  and says to reinstall the unit. None of them substitutes a weaker check,
  and each still reports unresolved or unchecked.

The evidence is recorded for what already holds: installing adds nothing to
the repository, the record is optional and the other units work without it,
the harness names no language, the artifacts are plain text, and a repository
overrides a convention with a file of its own that wins over the unit's.

After this decision a person can install one unit, see what it can't do and
what would fix it. What still doesn't work: a report that runs across every
unit at once, a doctor, which RES-0160 describes and which the verbs' status
covers for the verbs alone.

## Why

RES-0002 found six repositories running diverged copies of one harness,
because nobody installs or upgrades a document, which is why the harness ships
as units a repository installs. RES-0012 found that the record, the verbs and
the conventions are separate disciplines a repository adopts separately.
RES-0160 found that a report of an unresolved verb must say what would resolve
it, which turns the outcome into an action, and must tell a configuration gap
from a machine gap, because each has a different fix.

Measured at this revision: `meow-verbs status` reports an undeclared verb as
"the profile doesn't name it", and each launcher reports a missing binary as
"no meow binary was found for this machine"; neither says what to do.

The strongest objection: a path check is weaker than installing each unit
alone and running it. It is, and running a unit alone needs a Claude Code
session, which CI doesn't run; the path check catches the way a unit comes to
depend on another, which is by calling its files.

## Alternatives

| Option                                          | Better at                  | Why it lost                                                    |
| ----------------------------------------------- | -------------------------- | -------------------------------------------------------------- |
| A path check, and reports naming the fix        | Holds in CI, with no model | Chosen                                                         |
| Install each unit alone in a session and run it | Closest to a user          | Needs a model in CI, which this repository runs none of        |
| A doctor across every unit                      | One report                 | Larger than this need; the verbs' status covers the first half |
| Do nothing                                      | Costs nothing              | A missing capability says what's wrong and not what to do      |

## What it costs

A check in `tools/`, three messages in the native tool, four in the launchers,
a section in the docs index, and a task of recorded evidence.

## What would reverse it

- A doctor reporting every unit's capabilities arrives, and the messages move
  into it.

## Consequences

- `tools/check_standalone.py` runs in the `test` verb and fails on a path
  leaving a unit.
- An unresolved verb and a missing binary each name what would supply them.

## How I will know it was realised

1. A fixture shows `check_standalone.py` reporting a path that climbs out of
   a unit and one naming another unit's directory, and this repository
   passes it.
2. Fixtures show `meow-verbs status` naming `.meowpaw/profile.toml` for an
   undeclared verb, and a launcher with no binary naming the machine and the
   reinstall, each still reported unresolved or unchecked.
3. Each requirement that already holds has its evidence recorded in the task
   that closes it.
4. Every requirement ADR-1270 addresses lands in exactly one closed task.

## What this does not settle

- A doctor that reports every unit's capabilities at once.
