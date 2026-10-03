---
id: TSK-4670
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2430
closes: [REQ-1818, REQ-1820, REQ-1822, REQ-1830, REQ-1842]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read a changed base back, report its checks as not run, and review one layer's diff

After it changes a pull request's base, the implement step reads the base
back, reports the required checks as not run until a run started after the
change completes, and reports the layers above a closed or ejected one as
blocked; the review step reads one layer against its own base, as SPC-1090
states. One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given `steps/implement.md`, when a fixture reads it, then it says to run
   `gh pr view <n> --json baseRefName` after every base change and to report
   a base that reads back unchanged as not changed (REQ-1818). Closed by: a
   fixture under `plugins/meow-flow/tests/` naming REQ-1818, seen failing
   first.
2. Given the same file, when the fixture reads it, then it reports each
   required check as not run on the new base until a run that started after
   the change has completed, and forbids citing one that passed on the old
   base (REQ-1820, REQ-1822). Closed by: the same fixture.
3. Given the same file, when the fixture reads it, then it reports every task
   above a layer whose pull request is closed or ejected from a merge queue as
   blocked, naming that layer (REQ-1830). Closed by: the same fixture.
4. Given `steps/review.md`, when the fixture reads it, then it reads a stacked
   layer's diff against the layer below and never the whole stack's
   (REQ-1842). Closed by: the same fixture.

## What to do

Add the rules to `plugins/meow-flow/skills/method/steps/implement.md` beside
the stacking rules TSK-4660 writes, and the one-layer rule to
`plugins/meow-flow/skills/method/steps/review.md`, each held to SPC-1030 and
the unit's `budget.toml`.

## Depends on

- TSK-4660 (blocking): these rules extend the stacking rules it writes into `steps/implement.md`.

## Evidence

Not yet.

## Left alone

`paw status`'s stack lines, which TSK-4690 adds, because the record and not
the code host holds a dropped layer.
