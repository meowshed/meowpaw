---
id: TSK-5300
artifact: task
status: done
revised: 2026-10-10
epic: EPC-2780
closes: [REQ-4500]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The core unit ships the one build and writes where it is

`meow-core` carries the binary built with every unit's feature for each platform,
and a session start hook writes the path of its installed root to its data
directory.

## Acceptance criteria

1. Given a build, when `crates/meow/build-units` finishes, then
   `plugins/meow-core/bin/<target>/meow` exists for the machine's target and runs
   every unit's subcommand. Closed by: a test in `tools/`.
2. Given the core unit's session start hook, when it runs, then the file
   `meow-root` in `${CLAUDE_PLUGIN_DATA}` holds the installed root. Closed by:
   a test of the hook script in `plugins/meow-core/tests`.

## What to do

Build the full-feature binary into `plugins/meow-core`, add the hook, and keep
`meow-core`'s character budget (`budget.toml`).

## Depends on

Nothing.

## Evidence

Pull request 881. The tests are `tools/test_shared_binary.py`,
`plugins/meow-core/tests/test_root_hook.py` and `tools/test_check_kernel.py`:

- Criterion 1: `tools/test_shared_binary.py`, which names all 13 subcommands as
  carried by `plugins/meow-core/bin/<target>/meow`.
- Criterion 2: the four tests of `test_root_hook.py`.

The kernel check read the shipped binary as text and failed, so it now skips a
file that isn't text, with a test in a commit of its own.

## Left alone

The units' own builds, which EPC-2790 removes.
