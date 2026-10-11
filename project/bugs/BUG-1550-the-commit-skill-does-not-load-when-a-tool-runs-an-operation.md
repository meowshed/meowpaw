---
id: BUG-1550
artifact: bug
status: approved
severity: major
violates: [REQ-1146, REQ-2610, REQ-2618]
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The commit skill does not load when a tool runs a composite command or removes a working tree

The `commit` skill carries the rules that bound a tool's source control
operations (T1 to T7), and its description routes it only on writing a commit
message, so a session that runs `wt merge` or removes a working tree never
loads them.

## Reproduction

Seen with `meow-scm` at revision `224c9462`.

1. Start a session on a repository with the `meow-scm` unit installed, and ask
   Claude Code to merge a branch with `wt merge`, or to remove a working tree.
2. Read the skills the session loaded before the command ran.

## What the system does

The `commit` skill's description ends "before any commit message, squash
message or pull request title is written, rewritten or reworded". A request
that names a merge, a rebase or the removal of a working tree matches none of
those words, so the skill isn't loaded and rules T1, T4, T6 and T7 are absent
at the moment they apply.

## What it should do, and why

REQ-1146 says a description names each verb a request uses for the work the
unit governs, and the unit now governs running a composite command, rebasing
and creating or removing a working tree as well. REQ-2610 and REQ-2618 forbid
calling a bundling command and removing a working tree in the background, and
a rule the model doesn't have in context holds only by luck.

## Triage

It enters at implement, because the requirements are right and the
description is what doesn't state the obligation. Severity is major: the
bounds exist and are tested, and they fail silently on exactly the operations
they were written for.

## Closed by

A test that reads the skill's description and finds the verbs the rules
govern, and `mise run budget` passing with the longer description counted.

## Tasks

- [x] T-001 TSK-5370 name the operations the commit skill governs in its description (done: pull request 1046)
