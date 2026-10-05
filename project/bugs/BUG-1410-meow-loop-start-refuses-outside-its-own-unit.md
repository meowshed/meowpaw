---
id: BUG-1410
artifact: bug
status: approved
severity: minor
violates: REQ-0894
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# meow-loop start refuses where the binary ships in another unit's package

`runloop.rs`'s `own_unit` resolves the loop unit from the binary's own
path: it walks to `<exe unit>/.claude-plugin/plugin.json` and requires the
manifest to name `meow-loop`. ADR-2810 ships the meow binary with the core
package alone, so the binary's exe unit is `meow-core`, whose manifest
names `meow-core`: `own_unit` returns nothing, and `meow-loop start`
refuses with "meow-loop's own directory can't be found from its program's
path" on every npm install.

## Reproduction

Pi 1.0.2 on macOS 15 (aarch64), the packages installed from npm at
`f3b92ad2`:

1. `pi install npm:@meowshed/meow-loop && pi install npm:@meowshed/meow-core`.
2. In a Pi session, run `meow-loop start --step research` with the Bash
   tool.
3. The loop guard denies the command as designed (REQ-0894); running the
   launcher from a terminal instead answers
   `meow-loop's own directory can't be found from its program's path`.

## What the system does

The loop's `start` subcommand refuses on every install where the binary's
exe unit is not the meow-loop package, which is every install under
ADR-2810's layout. The in-session `guard` subcommand is unaffected: it
reads its event from standard input and never calls `own_unit`.

## What it should do, and why

The start command resolves the loop unit the way the git guard resolves
its scm launcher: an env override (`MEOW_LOOP_UNIT`), or the sibling
package whose manifest names `meow-loop`, falling back to the exe-relative
walk. The runner drives the method's chain, and a runner that refuses on
the designed install layout blocks unattended runs wherever the core
package ships the binary.

## Triage

Enters at implement, because REQ-0894 names the start command and the
resolution it needs exists in the sibling lookup `git.rs` already does.
Minor, because unattended runs on Pi are a design question the loop
specification has not settled for Pi (SPC-1201 covers the Claude Code
session), and the in-session guard is unaffected.

## Closed by

Not yet closed.
