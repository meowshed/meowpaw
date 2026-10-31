---
id: BUG-1710
artifact: bug
status: done
pr: 1140
severity: minor
violates: REQ-4506
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue: 1139
projected: 423506813f5f
tracked: 0328c3c288f6
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `meow-github` prints its usage where no binary resolves

With no binary, `meow-github project`, `sync` and `upgrade` print the usage line
and exit 2, so a correct command reads as a mistyped one and the output hides
that nothing ran.

## Reproduction

macOS, Darwin, arm64, `meow-github` 0.18.0, this repository at `6276d0c0`:

1. Set `CLAUDE_PLUGIN_DATA` to a directory with no `meow-core` beside it.
2. Run `~/.claude/plugins/cache/meowpaw/meow-github/0.18.0/bin/meow-github upgrade --check`.

## What the system does

Step 2 prints `usage: meow-github history [--wait] ...`, which lists the exact
form that was typed, and exits 2. `/meow-flow:upgrade` hit this at its issue
stage, and adding `<owner>/<name>` gave the same line. The launcher's tail
handles `governance-guard` and `history` and sends everything else to the usage
line, in both the Claude and the Pi launcher.

## What it should do, and why

REQ-4506 says a unit whose launcher finds no shared binary reports each of its
checks as unresolved, naming the core unit. `project`, `sync` and `upgrade`
should exit 3 with that reason, as `history` does, because exit 2 and a usage
line send the person to their own command.

## Triage

Enters at implement, because REQ-4506 states the behaviour and only the tail in
`tools/launchers.toml` breaks it. Minor, because nothing is written and the
command does fail, so the harm is the time spent on the wrong cause.

## Closed by

The reproduction's step 2 now exits 3 and prints
`meow-github upgrade: unresolved:` with the reason.
`tools/test_generate_launchers.py::Unresolved::test_each_command_exits_3_naming_the_core_unit`
guards `project`, `sync` and `upgrade` on both the Claude and the Pi launcher.

## Plan

1. Report `project`, `sync` and `upgrade` as unresolved in both of the
   `meow-github` tails in `tools/launchers.toml`, and regenerate the launchers.
