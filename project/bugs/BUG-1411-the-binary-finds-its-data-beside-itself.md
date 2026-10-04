---
id: BUG-1411
artifact: bug
status: approved
severity: minor
violates: REQ-4144
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The binary finds its data beside itself, where the npm layout doesn't hold it

Three of the binary's file lookups walk from the executable's path to the
unit that ships it: `record` reads `<unit>/lib/layout.toml`, `prose` reads
`<unit>/fragments/judge.md`, and the git guard looks for the scm launcher
at `<unit>/../meow-scm/bin/meow-scm`. ADR-2810 ships the binary with the
core package alone, so the executable's unit is `meow-core` while the
layout lives in `meow-flow`, the fragments in `meow-prose-gate`, and the
scm launcher in `meow-scm`: every lookup misses on an npm install, and
`paw ready` answers "the record was not checked: ... layout.toml: No such
file or directory".

## Reproduction

macOS 15 (aarch64), the packages installed from npm at 0.6.1/0.47.1/0.3.0:

1. `pi install npm:@meowshed/meow-core && pi install npm:@meowshed/meow-flow`.
2. From a session, run `meow-flow/bin/paw ready research`.
3. The launcher falls back to `command -v meow`, which finds the core
   binary, and `meow record ready research` answers
   `the record was not checked: .../meow-core/lib/layout.toml: No such
file or directory`.

## What the system does

`record`, `prose` and the git guard each resolve their unit's file from
the executable's path and fail on the designed install layout. The env
overrides `MEOW_LAYOUT` and `MEOW_SCM` exist but nothing sets them, and
the fragments have no override at all.

## What it should do, and why

The launcher sets the override it owns before it execs: `paw` exports
`MEOW_LAYOUT` naming its own `lib/layout.toml`, and the git extension
exports `MEOW_SCM` naming the sibling scm package's launcher. The
fragments travel with the binary, because the binary is the thing that
reads them, and meow-core ships `fragments/` beside `bin/`. A lookup that
resolves beside the executable still works where the binary and its unit
share a package, as the Claude Code plugin layout holds.

## Triage

Enters at implement, because REQ-4144 names the core package as where the
binary ships and REQ-4130 names the files a package loads as what it
bundles; the resolution the git guard already does for `MEOW_SCM` is the
pattern the launchers follow. Minor, because the failure is a degraded
report rather than a wrong pass: `paw` exits 3 and says what it couldn't
check, and the gate's judge never runs against text it can't find.

## Closed by

The launcher, extension and fragments changes this defect names, shipped
in meow-flow 0.47.2, meow-git 0.3.1 and meow-core 0.6.2.
