---
id: TSK-5220
artifact: task
status: done
revised: 2026-10-04
bug: BUG-1500
closes: [REQ-1008]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Cover packages with the declared licensing, and hold the gate to the licence check

`REUSE.toml` covers `packages/**` by the bulk declaration, and `mise run all`
runs `meow-licence check` through a new `licence` task, so a file the corpus
declares no licensing for fails the gate CI runs instead of reaching npm
unnoticed, as BUG-1500 reproduces. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given this repository's tree, when `meow-licence check` runs, then it exits
   0 with no finding naming a file under `packages/` (REQ-1008). Closed by:
   the check's output in the pull request, with the 100 findings it printed
   before the change.

## What to do

Add `packages/**` beside `plugins/**` in `REUSE.toml`'s bulk annotation,
because the mirrors are the same class of file. Add a `[tasks.licence]` task
that depends on `build`, because the check runs through the unit's binary,
and name it in `[tasks.all]`'s depends. Add the `licence` row to the gate
table in `CLAUDE.md`, which states what the gate fails on.

## Depends on

Nothing. BUG-1500 is approved.

## Evidence

`meow-licence check` printed `2688 files, 100 licensing findings` before the
change and exits 0 with `2688 files, 0 licensing findings` after it, on the
change's tree. `mise run all` exits 0 with the `licence` task among its
steps, and the `lint` verb, whose findings BUG-1500 reproduces, exits 0
again. The outputs stand in the pull request.

## Left alone

The per-unit `package.json` licence fields, which npm reads on its own, and
every file the check already covered.
