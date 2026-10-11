---
id: TSK-5610
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1680
closes: [REQ-2928]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin the suites that run a launcher to the checkout's build

Each suite that runs a unit's launcher pins the launcher's data directory the
way `meow-author`'s suite does, so the launcher resolves the build beside the
unit and never the installed release, as REQ-2928 states. One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a machine with an installed `meow-core` release, when the record
   suite runs, then it reads the same output a fresh build of the checkout
   prints. Closed by: `plugins/meow-flow`'s suite passing with and without
   the installed release present (REQ-2928).
2. Given every suite that runs a launcher, when a test reads their fixture
   code, then each pins `CLAUDE_PLUGIN_DATA` to a directory of its own.
   Closed by: a static test in `tools/` naming REQ-2928, seen failing first
   where a suite leaves it unset.

## What to do

The suites that run a unit's launcher and test nothing about how a launcher
finds its binary — `meow-flow`'s record suite first, then every unit's
fixture whose `Repository` sets an environment — set `CLAUDE_PLUGIN_DATA` to
an empty directory of their own in the environment they build. The suites
whose subject is the launcher's resolution, such as the unattended unit's
launcher tests and `tools/test_shared_binary.py`, are exempt, because what
they measure is the resolution itself. Add the static test to the profile's
`test` stage.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The suites whose subject is how a launcher finds its binary, the unattended
unit's resolution tests and `tools/test_shared_binary.py`, which measure the
preference itself.
