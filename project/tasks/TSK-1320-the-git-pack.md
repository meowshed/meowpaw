---
id: TSK-1320
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1060
closes: [REQ-0079, REQ-1292, REQ-1326, REQ-2530]
issue: 136
---

# Refuse a commit on the trunk, and check a branch before it is pushed

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-git/` as SPC-1060 states: `hooks/hooks.json` with the two
`PreToolUse` command hooks, each matched by an `if` rule to its own command;
the launcher `bin/meow-git`; and the program with `commit-guard` and
`push-guard`, which read the hook's input from standard input and block by
exiting 2 with the reason on standard error.

Block a commit on the declared trunk (REQ-1292). On push, check every commit
the push would publish through `meow-scm check-message`, found as SPC-1060
states, and report the check as unrun where it isn't found (REQ-0079). Where
signatures are required, pass only a good signature from a trusted key, and
report missing key material as unverifiable (REQ-1326, REQ-2530).

Write a fixture for every row of SPC-1060's failure paths and each of
ADR-1090's five checks, over scratch repositories with signing turned off for
the ones that don't test it, each seen failing first against a program that
returns nothing (REQ-2072).

Add the pack's budget of 0 characters, its page in `docs/`, its entry in the
marketplace and in `docs/README.md`, and this repository's `[git]` table:
`trunk = "main"` and `require_signatures = true`. Add the pack's fixtures to
the repository's `test` verb.

## Depends on

Nothing. ADR-1090 and SPC-1060 are approved, and `meow-scm` exists.

## Evidence

Not yet. The task closes on the fixtures passing, each shown first failing,
and on this repository's own branch being pushed through the hook.

## Left alone

Worktrees, stacked branches and the squash merge.
