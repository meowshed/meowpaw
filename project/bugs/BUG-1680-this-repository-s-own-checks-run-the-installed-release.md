---
id: BUG-1680
artifact: bug
status: approved
severity: major
enters: requirements
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# This repository's own checks run the installed release, not the checkout

Every launcher prefers the installed `meow-core` it finds through the data
directory and falls back to the build beside it, so this repository's own
record checks and test suites measure the released binary, not the tree under
review. Two defect records, BUG-1650 and BUG-1660, were written on this day
from what the installed 0.9.0 binary printed, and neither defect holds
against a fresh build.

## Reproduction

macOS 15 (aarch64), the harness installed from the marketplace at
`meow-core` 0.9.0, this repository checked out at `9da861f2`:

1. Run `plugins/meow-flow/bin/paw check` from the checkout.
2. Read its output: it reports
   `project/specs/SPC-1300-the-pi-packages.md: rests on REQ-4110, which is
withdrawn`, and exits 1.
3. Run it again with `CLAUDE_PLUGIN_DATA` pointed at an empty directory.
4. Read its output: 0 findings, exit 0.

The difference is the binary: the launcher resolves
`~/.claude/plugins/data/meow-core-*/meow-root`, which names the installed
0.9.0, and reaches the build beside it only where that is missing.

## What the system does

`plugins/meow-flow/bin/paw status` counts a defect's `violates` link as a
provider, so it flags a living specification resting on a withdrawn
requirement through the defect, and `paw check` exits 1 on the trunk. The
installed 0.9.0 predates the exclusion TSK-5500 made, so the check and every
suite that runs through a launcher measured a checker the change under
review didn't build. `plugins/meow-author`'s suite sets an empty
`CLAUDE_PLUGIN_DATA` for exactly this reason; `meow-flow`'s record suite
sets none, so its result depends on which release the machine has
installed.

## What it should do, and why

No requirement in force states it, which is the gap this defect names: a
check this repository runs against its own tree must measure the tree under
review, because evidence about a binary the change didn't produce reads as
evidence about the change. The installed-release preference is right for a
repository using the harness, whose tree carries no build; the harness's own
repository is the exception, and its suites and stages say which binary they
run.

## Triage

Enters at requirements, because no requirement in force states the
obligation the fix would hold, so the requirement is written first and the
fix follows it. The fix itself is the record suite and the other
launcher-based checks pinning the launcher's data directory the way
`meow-author`'s suite does, with a test that holds it. Major, because the
false output reached two defect records and silently stood in for the gate
on a developer machine; CI was never wrong, which is the only reason the
error stopped there.

## Closed by

Not yet.
