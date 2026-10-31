---
id: TSK-5165
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2610
closes: [REQ-1426]
issue: 1013
projected: f7fbbc45089c
tracked: 2ae621469738
---

# Deny from a hook whose program is missing

Every blocking launcher denies and names its install command when its binary
is absent.

## Acceptance criteria

1. Given each launcher ADR-2710 names with its binary absent, the blocking
   hook denies with the install command and the stated non-blocking exception
   still allows. Closed by: launcher fixtures for REQ-1426.

## What to do

Share the missing-program response across the hook launchers.

## Depends on

Nothing.

## Evidence

The tests came first, in a commit of their own, where five failed: the
launchers of `meow-git`, `meow-github`, `meow-prose-gate` and `meow-loop`
exited 0 with no binary. The tests are
`test_a_missing_binary_names_the_machine_and_the_reinstall` and
`test_no_program_denies_the_commit_and_says_how_to_install` in `test_git.py`,
`test_a_missing_binary_denies_every_bash_call_and_says_how_to_install` in
`test_github.py`,
`test_a_launcher_with_no_binary_denies_the_publish_and_says_how_to_install` in
`test_gate.py` and `MissingBinary` in `test_loop.py`. They close the criterion
(REQ-1426): each blocking launcher exits 2 with a reason naming the unit, the
machine and `claude plugin install meow-core@meowpaw`, and `meow-loop`'s
`prompt` and `stop`, which stop no call and where a denial would erase the
person's prompt, still let the session go on. `meow-flow` and `meow-checks`
block nothing and keep their messages. SPC-1010's failure table now says so,
and the four READMEs. `mise run all` passed with exit status 0.

## Left alone

Programs invoked outside hooks.
