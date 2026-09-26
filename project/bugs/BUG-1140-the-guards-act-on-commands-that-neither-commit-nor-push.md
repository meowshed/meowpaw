---
id: BUG-1140
artifact: bug
status: draft
severity: major
violates: REQ-1292
found: 2026-09-26
revised: 2026-09-26
issue: 186
---

# The guards acted on commands that neither commit nor push

## Reproduction

With `meow-git` 0.1.0 installed and the session in a checkout on `main`, run a
command that only reads, with a substitution in it:

```bash
gh pr list --search "$i in:body" | tr a b
```

Claude Code runs `commit-guard`, which refuses it:

```text
meow-git: refused a commit on `main`, the trunk this repository declares. Take a branch and commit there.
```

The same guard refuses `cd <worktree on a branch> && git commit ...`, because
it judges the session's checkout on `main`.

## What the system does

The hooks are matched by `if` rules, `Bash(git commit *)` and `Bash(git push
*)`, and each guard trusted the rule and never read the command. Claude Code's
hooks documentation says that when it can't tell which commands a shell input
runs, it runs the hook "regardless of the pattern", and that a pattern naming
more than the command runs it on any `$()`, backticks or `$VAR`. So on the
trunk every such command was refused, reads included, and the push guard
checked commits for commands that pushed nothing. Each guard also judged the
session's directory, not the one the command committed in.

## What it should do, and why

REQ-1292 asks the harness to refuse a commit on the trunk, which is a commit,
not every command the platform couldn't parse. A guard that refuses reads
teaches its user to route around it, and SPC-1060 said the hooks ran "for that
command and for no other", which the platform doesn't promise.

## Triage

Implementation, and a correction to SPC-1060. `meow-git` is released as 0.1.1.

## Closed by

Each guard reads the command from the hook's input, checks nothing where it
doesn't run `git commit` or `git push`, and judges the directory a `cd` or
`git -C` names where that directory exists. Five fixtures cover it: a command
that doesn't commit runs on the trunk, every form of a commit is still refused
there, a commit in a worktree on a branch is judged there, a command that
doesn't push checks nothing, and the unchanged fixtures still pass. All 16 run
`OK`, and against a program that returns nothing all 16 fail.
