---
id: TSK-2100
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1370
closes: [REQ-3004]
issue:
---

# `meow-method` 0.30.0 is a stub that says where the unit went

The catalogue keeps `meow-method` for one release as a stub whose
`SessionStart` hook tells the session the unit is now `meow-flow`, with the
two commands that move an install, and whose page names the release that
removes it. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given the stub, when its `SessionStart` hook runs, then it prints that
   `meow-method` is now `meow-flow`, with `claude plugin install
meow-flow@meowpaw` and `claude plugin uninstall meow-method@meowpaw`, and
   exits 0. Closed by: a fixture naming REQ-3004, seen failing first.
2. Given the stub's page, when a reader opens it, then it says the unit was
   renamed, what to run, and which release removes the stub. Closed by: the
   page, which `tools/check_docs.py` holds.

## What to do

Create `plugins/meow-method/` holding a manifest at 0.30.0, a page, a budget
of no context on every turn, and a `SessionStart` hook printing the notice.
It ships no skill and no program. Keep its catalogue entry. Describe it in
SPC-1070 with REQ-3004.

## Depends on

TSK-2090, because the stub names the unit it creates and takes over the
directory it empties.

## Evidence

Not yet.

## Left alone

Removing the stub, which is a task of the release after 0.31.0.
