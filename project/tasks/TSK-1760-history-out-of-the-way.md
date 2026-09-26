---
id: TSK-1760
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1230
closes: [REQ-0530, REQ-0552, REQ-0554, REQ-0555]
issue: 300
---

# Withdrawn statements are collected and nothing is archived

Withdrawn statements are collected and nothing is archived, as ADR-1230 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a specification citing a withdrawn requirement in its body, when `check shape` runs, then it reports the line, and passes once the citation sits under Withdrawn. Closed by: a fixture.
2. Given a directory named `archive` under the root, when `check shape` runs, then it reports it. Closed by: a fixture.
3. Given REQ-0530 and REQ-0554, when their evidence is gathered, then the task records the file and line that shows each holds. Closed by: the evidence table.

## What to do

In `check shape`, report a living document citing a withdrawn requirement outside a section headed Withdrawn, and a directory under the record's root whose name contains `archive`. Record the evidence that the constitution outranks every artifact and that a superseded record names what replaced it.

## Depends on

Nothing. ADR-1230 is approved.

## Evidence

Two fixtures, each seen passing against the program and failing against a
stub that returns nothing. `check shape` reports a specification's body citing
a withdrawn requirement at its line, and passes once the citation sits under a
section headed Withdrawn. It reports a record kept in `research/archive/`,
naming the directory. This repository reports `shape: 0 findings`.

| Requirement | Evidence                                                                                                                                                                                                                                                                                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REQ-0530    | The constitution template opens with "The root policy for this repository, and what outranks it", `plugins/meow-method/templates/constitution.md:13`, and this repository's `CLAUDE.md:7` says that where a document disagrees with it, it wins.                                                                                                                                    |
| REQ-0552    | `check shape` reports a withdrawn citation in a living document outside a Withdrawn section, as the first fixture shows.                                                                                                                                                                                                                                                            |
| REQ-0554    | A record replaced by a later one takes the stored status `superseded`, which every numbered kind in `lib/layout.toml` declares and `check frozen` accepts as a change to an approved record, and the later record names it in `supersedes`, which `show` reports under "Cited by". Relations are authored upward, so the replacement names the replaced record and not the reverse. |
| REQ-0555    | `check shape` reports a record in an archive directory, as the second fixture shows, and no such directory exists under `project/`.                                                                                                                                                                                                                                                 |

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 98 tests in 6.527s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=95, errors=3)
```

## Left alone

Splitting approved requirements that carry two obligations, which ADR-1230
leaves to the amendment path.
