---
id: TSK-1990
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1320
closes: [REQ-2526, REQ-2528]
issue: 384
projected: 81d8df5aeada
---

# Source control is read with prompting and paging off

Source control is read with prompting and paging off, as ADR-1320 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given a stand-in git recording its environment, when a unit's program reads source control, then each read has prompting, paging, advice and machine-wide configuration turned off. Closed by: a fixture.

## What to do

Run every read of git in the native tool with `GIT_TERMINAL_PROMPT=0`, `GIT_PAGER=cat`, `GIT_ADVICE=0`, `GIT_CONFIG_NOSYSTEM=1` and no standard input, through one helper per module.

## Depends on

Nothing. ADR-1320 is approved.

## Evidence

`profile::reading_git()` builds every read of git in the native tool, with
`GIT_TERMINAL_PROMPT=0`, `GIT_PAGER=cat`, `GIT_ADVICE=0`,
`GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0` and no standard input. The
user's own configuration stays, because it holds their identity and keys,
which RES-0131 keeps for work that records authorship. The seven reads in
`git.rs`, `profile.rs`, `scm.rs` and `record.rs` use it, and a search for
another way of starting git finds 1.

A fixture puts a stand-in git on the `PATH` that records its environment and
runs the real one, then runs `status`, `check frozen` and `check coverage`:
every read it records has prompting, paging, advice and the machine-wide
configuration off. It failed with the change stashed and passes with it, and
every unit's fixtures and the crate's tests pass.

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 120 tests in 9.499s
OK
```

## Left alone

A version control tool other than git, which ADR-1320 leaves.
