---
id: TSK-1930
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1310
closes:
  [
    REQ-1350,
    REQ-1352,
    REQ-1354,
    REQ-1355,
    REQ-1356,
    REQ-1360,
    REQ-1368,
    REQ-1382,
    REQ-1386,
    REQ-1396,
  ]
issue: 371
---

# Project an approved epic's tasks onto issues

Project an approved epic's tasks onto issues, as ADR-1310 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given an approved epic with two tasks, when `project` runs, then it creates two issues citing each task's requirements and dependencies with the marker, writes `issue:` and `projected:` on each task, and reads both back. Closed by: a fixture.
2. Given the same epic, when `project` runs again, then it creates and changes nothing. Closed by: a fixture.
3. Given a draft epic, when `project` runs, then it creates nothing. Closed by: a fixture.
4. Given an approved task whose `projected:` changed, when `check frozen` runs, then it passes. Closed by: a fixture.

## What to do

Add `meow-github project <epic>`: refuse an epic that isn't approved; for each task create an issue titled with its identifier and title, its body citing the epic, the requirements it closes and its dependencies with their reasons, ending with a marker naming the task and its fingerprint; write `issue:` and `projected:` on the task; read each issue back and report a mismatch; and change nothing for a task already projected at its fingerprint. Let `meow-method check frozen` accept a change to an approved task's `projected:`.

## Depends on

Nothing. ADR-1310 is approved.

## Evidence

`meow-github project <epic> [<owner>/<name>]` projects an approved epic's
tasks. Four fixtures run it against a stand-in `gh` that keeps its issues in a
file:

- On an approved epic with two tasks it creates two issues titled with each
  task's identifier and title. The second's body names its epic and the
  decision the epic realises, lists both requirements it closes by
  identifier, quotes its dependency with the reason, and ends with the marker
  naming the task and a twelve-digit fingerprint. Each task gains `issue:` and
  `projected:`, and each issue is read back with a GET of its own address.
- The fingerprint matches the first twelve hex digits of the SHA-256 of the
  title, a newline and the body without the marker, computed separately, so a
  person reproduces it with `shasum -a 256`.
- A second run makes no write to the tracker, leaves the task byte for byte,
  and reports each task unchanged.
- A draft epic projects nothing and says so, and `gh` is never called.

`meow-method check frozen` now lets an approved task's `projected:` change, as
it lets `issue:`: a fixture adding `projected:` to an approved task failed with
the change stashed and passes with it.

```text
$ python3 -m unittest discover -s plugins/meow-github/tests
Ran 8 tests in 0.744s
OK

$ MEOW_GITHUB_BIN=stub python3 -m unittest discover -s plugins/meow-github/tests
FAILED (failures=3, errors=4)

$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 117 tests in 7.668s
OK

$ cargo test --all-features
test result: ok. 6 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Left alone

Projecting the epic onto a milestone or a board, which ADR-1310 leaves.
