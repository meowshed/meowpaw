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

The static test was written first and seen failing for four suites in
`45c49a6e`, and passes after `fb3853e1`. Criterion 2 closes with
`tools.test_plugin_contract.PinnedSuites.test_every_launcher_running_suite_pins_the_data_directory`,
naming REQ-2928. Criterion 1 closes with the record suite and the three
other suites passing while an installed `meow-core` 0.9.0 is present on this
machine: the pin makes every launcher resolve the build beside the unit, so
the suite is indifferent to the install. The suites whose subject is the
resolution stay unpinned, as the task's Left alone states. The five stages
passed at tree `9e0982c0c387`, each bound by `meow-checks run` and
confirmed by `meow-checks evidence`, exit 0: format `d754141f52dc`, check
`3b85d3cd898f`, lint `c2f4abc89f20`, test `63c3e6c338b7`, build
`29d6a474fe7b`.

## Left alone

The suites whose subject is how a launcher finds its binary, the unattended
unit's resolution tests and `tools/test_shared_binary.py`, which measure the
preference itself.
