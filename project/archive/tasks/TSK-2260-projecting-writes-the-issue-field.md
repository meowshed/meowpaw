---
id: TSK-2260
artifact: task
status: done
revised: 2026-09-27
bug: BUG-1210
closes: [REQ-1382, REQ-1386]
issue: 508
---

# `meow-github project` writes `issue:` into a task that lacks the field

The writer adds `issue:` where the task's front matter has none, as it does
for `projected:`, so a replay finds the mapping. One task, one branch, one
pull request, one review.

## Acceptance criteria

1. Given an approved task with no `issue:` line, when `meow-github project`
   runs, then the task carries `issue:` with the new issue's number beside
   `projected:`, and a second run opens nothing. Closed by: a fixture naming
   REQ-1382 and REQ-1386, seen failing first.

## What to do

Make the mapping writer add `issue:` before the closing fence where the front
matter has none, in `crates/meow/src/github/project.rs`, and move
`meow-github` to its next patch version.

## Depends on

Nothing. BUG-1210 is approved.

## Evidence

Closes REQ-1382 and REQ-1386 again, as BUG-1210 asks.
`Project.test_a_task_with_no_issue_field_gets_one_and_a_replay_opens_nothing`
in `plugins/meow-github/tests/test_github.py` failed before the change, with
the task carrying `projected:` and no `issue:`, and passes after it. The
`meow-github` fixtures run OK, and `plugins/meow-verbs/bin/meow-verbs run format
lint test` exits 0 with `summary: format passed, lint passed, test passed`.

## Left alone

The task template, which already carries the field.
