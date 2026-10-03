---
id: TSK-4915
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2520
closes: [REQ-2730]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin that the `SessionStart` hook names a pending gate

A test holds what `meow-flow` already does: its `SessionStart` hook runs
`paw status --waiting`, whose output the platform adds to the model's
context, so a pending gate reaches the model without a file it has to read,
as SPC-1240 states under "A pending gate". One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a fixture record with one draft decision waiting for approval, when
   the command `plugins/meow-flow/hooks/hooks.json` declares for
   `SessionStart` runs, then its standard output names that decision and the
   gate it waits at (REQ-2730). Closed by: a test under
   `plugins/meow-flow/tests/` naming REQ-2730.
2. Given the same fixture with nothing waiting, when the command runs, then
   it prints nothing and exits 0. Closed by: the same test.

## What to do

Read the hook's command from `hooks.json` in the test, so a change to the
declaration breaks it, and run it against the fixture. Change no behaviour.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

What `paw status --waiting` prints, which SPC-1090 states and its own tests
pin.
