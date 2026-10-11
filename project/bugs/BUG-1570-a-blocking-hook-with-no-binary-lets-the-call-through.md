---
id: BUG-1570
artifact: bug
status: approved
severity: major
violates: REQ-1426
enters: implement
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A blocking hook whose launcher finds no binary exits 0 and lets the call through

ADR-2710 decides a blocking hook with no program denies with exit 2, naming the
unit, the machine's target and the install command. The launchers of
`meow-git`, `meow-github`, `meow-loop` and `meow-prose-gate` exit 0.

## Reproduction

Seen on the trunk after pull request 1046, on macOS arm64.

1. Copy a unit's launcher, such as `plugins/meow-git/bin/meow-git`, to a
   directory with no binary beside it and no `meow-core` data directory.
2. Run it with the hook's subcommand and `{}` on standard input, with an
   environment of `PATH`, `HOME` and `CLAUDE_PLUGIN_DATA` only.

## What the system does

`meow-git commit-guard` and `push-guard` and `meow-prose-gate check` print
`unrun (no meow binary was found ...)` and exit 0, and `meow-github
governance-guard` and `meow-loop guard` print nothing and exit 0. The call goes
through, which is the call each hook exists to stop.

## What it should do, and why

REQ-1426 says an automatic check fails with a diagnostic when its tool is
absent and doesn't skip silently, and SPC-1240 "A hook whose program is
missing" says a blocking hook denies with exit 2, because a guard that lets a
call through for a missing binary lets through the call it exists to stop.

## Triage

It enters at implement, because the requirement and the decision are right and
the launchers do the opposite. Severity is major: the repository's trunk rule,
its commit convention, its governance and a run's own state are unguarded on a
machine with no binary, with a message only the first three of five print.

## Closed by

A test per blocking unit that runs its launcher with no binary and reads exit 2
and a reason naming the unit, the target and the install command.
