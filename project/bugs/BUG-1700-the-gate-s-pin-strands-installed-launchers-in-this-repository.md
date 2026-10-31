---
id: BUG-1700
artifact: bug
status: approved
severity: major
violates: REQ-4504
enters: implement
found: 2026-10-31
revised: 2026-10-31
issue: 1137
projected: dd17439e01e7
tracked: 6ab04f0d78c3
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The gate's pin stops every installed launcher working in this repository

`mise.toml` sets `CLAUDE_PLUGIN_DATA` under `[env]`, so a shell that activates
mise carries the gate's empty data directory into everything it starts, and an
installed launcher run from this repository finds no `meow-core`.

## Reproduction

macOS, Darwin, arm64, `meow-core` 0.11.0 and `meow-flow` 0.54.0 installed from
the marketplace, this repository at `6276d0c0`, in a shell with mise activated:

1. Run `echo $CLAUDE_PLUGIN_DATA`. It prints `target/gate-data/unit` under the
   checkout.
2. Run `~/.claude/plugins/cache/meowpaw/meow-flow/0.54.0/bin/paw upgrade`.
3. Run the same command with the variable removed from its environment:
   `env -u CLAUDE_PLUGIN_DATA ~/.claude/plugins/cache/meowpaw/meow-flow/0.54.0/bin/paw upgrade`.

## What the system does

Step 2 exits 3 and prints "no paw executable was found for this machine, Darwin
on arm64; install meow-core", although `meow-core` is installed. Step 3 exits 0.
The launcher looks for `meow-core-*/meow-root` in the parent of
`CLAUDE_PLUGIN_DATA`, and `target/gate-data` holds none. Every skill that calls
its unit's launcher fails the same way, so `/meow-flow:upgrade` stopped at its
first command, and the message sends the person to an install that already ran.

## What it should do, and why

An installed launcher finds the shared binary through the path the platform
documents, as REQ-4504 says, wherever the session runs. The pin exists for
REQ-2928, because a launcher preferred the installed release over the checkout's
build, and only a launcher in a checkout needs that answer reversed.

## Triage

Enters at implement, because REQ-4504 and REQ-2928 both state the behaviour and
the launcher's probe order is what breaks them. Preferring the build beside the
launcher holds REQ-2928 without a pin: an installed unit has no `meow-core`
beside it, so it resolves as before, and each gate task that runs a launcher
already depends on `build`. Major, because every installed skill that calls a
launcher fails in this repository for anyone with mise activated, and the
message names the wrong cause.

## Closed by

The reproduction's step 2 now exits 0 in a shell under this repository's mise
configuration, because that configuration no longer sets `CLAUDE_PLUGIN_DATA`.
`tools/test_generate_launchers.py::CheckoutBuild` guards both halves:
`test_the_build_beside_the_launcher_wins_over_an_installed_core` holds REQ-2928
without the pin, and `test_the_repository_sets_no_data_directory_for_every_process`
fails if the pin returns.

## Plan

1. Prefer the build beside the launcher in `tools/generate_launchers.py`,
   regenerate the launchers, and remove the `[env]` pin from `mise.toml`.
