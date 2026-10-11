---
id: TSK-4410
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2340
closes: [REQ-1738]
issue: 945
projected: 795b0026b2e3
tracked: 8d76b079a859
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Stop a launcher on a platform older than its unit's `claude_code`

Each unit's launcher compares the platform version it runs under with the
`claude_code` its `requires.toml` names, and on an older one prints both
versions and exits 3 without running the binary, as SPC-1080 states. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a unit whose `requires.toml` names `claude_code = "2.1.283"` and a
   platform that reports `2.1.200`, when its launcher runs, then it prints
   both versions, runs no binary and exits 3 (REQ-1738). Closed by: a
   launcher fixture naming REQ-1738, seen failing first.
2. Given a platform that reports `2.1.283` or later, when the launcher runs,
   then it runs the binary as before. Closed by: a launcher fixture.
3. Given a platform whose version the launcher can't read, when it runs,
   then it prints that the version is unknown and runs the binary. Closed by:
   a launcher fixture.

## What to do

Read the running platform's version in the POSIX shell launcher every unit
with a binary ships, by the means the platform documents, and cite that
documentation in the pull request. Find the documented means first, and
where the platform documents none, stop and report it, because a guessed
source makes the check pass or fail on nothing. Keep the launcher under
`shfmt` and `shellcheck` as SPC-1080 states.

A unit with no launcher, such as `meow-core`, runs no program, so this rule
reaches only the units with a binary. Say so in each such unit's README.

## Depends on

Nothing.

## Evidence

The tests were written first and seen failing in `794713a7`, and pass after
`8d8e321c`. They live in `tools/test_launchers.py`, and each names REQ-1738:
the older platform stops the launcher naming both versions, the tested and
newer platforms run the binary, an unreadable version prints unknown and
runs the binary, and every launcher in the tree carries the stop. The
documented means is `claude --version`, which the platform's command-line
reference lists; the stubs that stand in for it answer at once, because the
real one costs more than a second. Each launcher-carrying unit's README says
its launcher stops. The five stages passed at tree `dc741c41414b`, each
bound by `meow-checks run` and confirmed by `meow-checks evidence`, exit 0:
format `c97f46c46d07`, check `5fd194c8283c`, lint `48e163d2686b`, test
`c82df3e51f2c`, build `dc756eb1f1ba`.

## Left alone

A unit with no binary, which has no launcher to stop. The tested version in
each `requires.toml`, which stays as it is.
