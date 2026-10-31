---
id: TSK-1940
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1310
closes: [REQ-1353, REQ-1378, REQ-1388, REQ-1392, REQ-1394, REQ-1400]
issue: 372
---

# Report where the record and the tracker disagree

Report where the record and the tracker disagree, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a task changed since it was projected, when `project` runs, then it updates the issue and `projected:`. Closed by: a fixture.
2. Given an issue edited on GitHub, when `project` runs, then it reports the disagreement and leaves the issue as it is. Closed by: a fixture.
3. Given an issue closed while its task is unmarked, when `project --check` runs, then it reports it and writes nothing. Closed by: a fixture.

## What to do

Make `project` update the issue of a task changed since it was projected, report an issue edited on GitHub while its task is unchanged without overwriting it, and report an issue closed on GitHub while the epic leaves its task unmarked. Add `--check`, which reports each task's state and writes nothing. Never write an issue's state.

## Depends on

TSK-1930, whose command this extends.

## Evidence

Each run reads every projected task's issue and computes its state from two
fingerprints, the task's `projected:` and the one the issue's title and body
carry, and stores nothing (REQ-1388). Three fixtures, against the stand-in
`gh`:

- A task retitled after it was projected updates its issue with one `PATCH`,
  its only write, and `projected:` moves to the new fingerprint.
- An issue whose body a person rewrote on GitHub is reported as edited since
  it was projected, exit 1, and left exactly as the person wrote it, with no
  write.
- With `--check`, an issue closed on GitHub while the epic leaves its task
  unmarked is reported as a disagreement, and a retitled task is reported as
  one that would be updated; no write reaches the tracker, and neither task
  file changes.

The pack never writes an issue's state: the only writes are `POST` for a new
issue and `PATCH` of its title and body. It polls when run.

```text
$ python3 -m unittest discover -s plugins/meow-github/tests
Ran 11 tests in 1.340s
OK

$ MEOW_GITHUB_BIN=stub python3 -m unittest discover -s plugins/meow-github/tests
FAILED (failures=3, errors=7)
```

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
