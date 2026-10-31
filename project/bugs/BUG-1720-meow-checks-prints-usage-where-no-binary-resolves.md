---
id: BUG-1720
artifact: bug
status: approved
severity: major
violates: REQ-4506
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue: 1142
projected: c1e298608386
tracked: e80b83d2a7f3
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# `meow-checks` prints its usage where no binary resolves

With no binary, `meow-checks evidence`, `state`, `tree`, `local` and `doctor`
print a usage line that omits them and exit 2, so a request for evidence reads
as a mistyped command and the output hides that nothing was checked.

## Reproduction

macOS, Darwin, arm64, `meow-checks` 0.15.0:

1. Set `CLAUDE_PLUGIN_DATA` and `HOME` to directories with no `meow-core`.
2. Run `~/.claude/plugins/cache/meowpaw/meow-checks/0.15.0/bin/meow-checks evidence test`.

## What the system does

Step 2 prints `usage: meow-checks status [--json] | meow-checks run <verb>...`
and exits 2. The launcher's tail handles `status`, `revision` and `run` and sends
every other command to the usage line, in both the Claude and the Pi launcher.

## What it should do, and why

REQ-4506 says a unit whose launcher finds no shared binary reports each of its
checks as unresolved, naming the core unit. These five commands should exit 3
with that reason, because `evidence` is what a person cites before calling work
done, and exit 2 with a usage line names the wrong fault.

## Triage

Enters at implement, because REQ-4506 states the behaviour and only the tail in
`tools/launchers.toml` breaks it. Major, because the verify skill stops on this
output, and the output sends the person to their own command.

## Closed by

`tools/test_generate_launchers.py::UnresolvedChecks::test_each_command_exits_3_naming_the_core_unit`
guards all five commands on both the Claude and the Pi launcher, and the
reproduction's step 2 now exits 3 with `meow-checks evidence: unresolved:`.

## Plan

1. Report `evidence`, `state`, `tree`, `local` and `doctor` as unresolved in both
   of the `meow-checks` tails in `tools/launchers.toml`, and regenerate the
   launchers.
