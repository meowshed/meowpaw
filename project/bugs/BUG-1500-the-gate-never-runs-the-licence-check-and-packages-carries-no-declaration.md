---
id: BUG-1500
artifact: bug
status: approved
severity: major
violates: REQ-1008
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The gate never runs the licence check, and packages carries no declaration

`mise run all`, the gate CI runs, omits the licence check that the profile's
`lint` verb runs, and `packages/`, the sixteen unit mirrors #856 added, carries
no licensing declaration. A person who runs the verbs sees 100 findings; CI
passes the same tree and merges the gap, so the packages that publish to npm
under ADR-2800 distribute files with no licensing at all.

## Reproduction

Seen on a tree carrying #859 (466751bb) on Darwin arm64, and CI run
37228417528 on the same revision under Linux passes. From a checkout of
`main`:

1. `meow-checks run lint`, which runs `plugins/meow-licence/bin/meow-licence
check`, exits 1 with `2688 files, 100 licensing findings`, each a file under
   `packages/` reported as `no licensing declaration covers it`.
2. `mise run all` on the same tree exits 0, because no task in its `depends`
   runs the licence check, and so does CI's `mise run all`.

## What the system does

`meow-licence check` reports every file under `packages/` as uncovered, among
them `packages/meow-unattended/README.md` and `packages/meow-scm/skills/
commit/SKILL.md`, and the gate that would stop the merge never runs it.

## What it should do, and why

Every file the repository carries sits under the licensing the corpus
declares, which REQ-1008 asks of code and the bulk declaration delivers for
`plugins/**`; the mirrors under `packages/**` are the same class of file and
fell outside it. The gate catches this, because a check that runs nowhere
gates nothing.

## Triage

It enters at `implement`, because REQ-1008 holds and what is missing is
coverage and a gate task. Severity major: the gap publishes to npm, where a
file without licensing reaches everyone who installs a package, and the gate
that should have caught it never runs.

## Closed by

TSK-5220 adds `packages/**` to the bulk declaration in `REUSE.toml` and a
`licence` task to `mise run all`, and `meow-licence check` reports 0 findings
on the change's tree.

## Tasks

- [x] T-001 TSK-5220 cover `packages/` with the declared licensing, and hold
      `mise run all` to the licence check
