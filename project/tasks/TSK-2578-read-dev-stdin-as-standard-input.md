---
id: TSK-2578
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1268
closes: []
issue: 731
---

# Read `/dev/stdin` and `/dev/fd/0` as standard input in the prose gate

Make `meow-prose-gate check` read a file argument of `/dev/stdin` or
`/dev/fd/0` as it reads `-`, so the heredoc that feeds the command is checked
and never reported as a hidden file. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a `git commit -F /dev/stdin` fed by a heredoc holding
   `Cache pages`, when the launcher runs `check`, then it exits 0 and prints
   nothing. Closed by:
   `ReadableTexts.test_a_heredoc_read_through_dev_stdin` in
   `plugins/meow-prose-gate/tests/test_gate.py`.
2. Given a `gh pr create --body-file /dev/fd/0` fed by a heredoc holding a
   plain paragraph, when the launcher runs `check`, then it exits 0. Closed
   by: `ReadableTexts.test_a_body_read_through_dev_fd_0`.
3. Given a `git commit -F /dev/stdin` fed by a heredoc holding
   `a silver bullet`, when the launcher runs `check`, then it exits 2 with a
   P1 finding quoting `silver bullet`. Closed by:
   `TruePositives.test_p1_in_a_heredoc_read_through_dev_stdin`.

## What to do

In `publishing` in `crates/meow/src/prose.rs`, read `/dev/stdin` and
`/dev/fd/0` as standard input wherever `-` is read, so a file redirected with
`<` into such a command is still reported as P3. Write the three fixtures
first, in a commit of their own, and see them fail. State the
spellings in SPC-1010's section on the gate and in the unit's README, and
raise `meow-prose-gate`'s patch version, with each page's `describes:`.

## Depends on

Nothing. BUG-1268 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

Any other device path, such as `/proc/self/fd/0`: nobody reported one, and a
list of every spelling is a guess the gate doesn't need.
