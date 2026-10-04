---
id: TSK-1950
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1310
closes: [REQ-1351, REQ-1372, REQ-1376, REQ-1380, REQ-1384, REQ-1402]
issue: 373
---

# The tracker is declared, optional, and projectable by hand

The tracker is declared, optional, and projectable by hand, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a profile with no tracker, when `project` runs, then it reports the tracker undeclared, names the section to declare, and creates nothing. Closed by: a fixture.
2. Given each other requirement this task closes, when its evidence is gathered, then the task records the file, the fixture or the command that shows it holds. Closed by: the evidence table.

## What to do

Add `[tracker] kind` to the profile template and have `project` report a profile declaring no tracker and do nothing. Write the docs section giving the `gh` commands that produce the same issue and fields by hand. Record the evidence that the method completes with no tracker and that the mapping is recoverable from the repository.

## Depends on

TSK-1930, whose command this extends.

## Evidence

`meow-github project` now reads `[tracker] kind` from the profile, and a
fixture with a profile declaring none exits 3, says the profile declares no
tracker, names the section to declare, calls `gh` never and leaves the task
unmapped. The profile template gains a commented `[tracker]` section, and this
repository declares `kind = "github"`.

| Requirement | Evidence                                                                                                                                                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REQ-1351    | The profile's `[tracker] kind` names the tracker, and the fixture above shows an undeclared one refused. A second tracker is a second `kind` the projection maps to, not a change to the method.                                  |
| REQ-1372    | The record holds the tasks and decisions, and each issue is written from a task, never the other way; the only field that comes back is an issue's state, which the pack reads and never writes.                                  |
| REQ-1376    | The epic lists the tasks, and an issue closed while its task is unmarked is reported and not reconciled, which TSK-1940's fixture shows.                                                                                          |
| REQ-1380    | No step, gate or check of `meow-method` reads the tracker: `meow-method check` passes on a record with no `[tracker]`, as every meow-method fixture shows, and the fixture above shows the pack itself doing nothing without one. |
| REQ-1384    | `issue:` and `projected:` live on the task in the repository, and `--check` rebuilds each task's state from them and the issue alone.                                                                                             |
| REQ-1402    | `docs/meow-github.md` gives the `shasum` and `gh api` commands that file a task by hand with the same title, body, marker and two fields, and TSK-1930's fixture shows the fingerprint reproduced separately from the pack.       |

Run against this repository's own epic, whose tasks were filed by hand before
the pack existed:

```text
$ meow-github project EPC-1310 --check
TSK-1930: mapped to issue #371 by hand, with no fingerprint; left as it is
TSK-1940: mapped to issue #372 by hand, with no fingerprint; left as it is
TSK-1950: mapped to issue #373 by hand, with no fingerprint; left as it is

$ python3 -m unittest discover -s plugins/meow-github/tests
Ran 12 tests in 1.451s
OK

$ MEOW_GITHUB_BIN=stub python3 -m unittest discover -s plugins/meow-github/tests
FAILED (failures=4, errors=7)
```

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
