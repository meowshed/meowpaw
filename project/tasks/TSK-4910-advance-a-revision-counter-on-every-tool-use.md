---
id: TSK-4910
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2520
closes: [REQ-2728]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Advance a revision counter on every tool use, a failed one included

`meow-checks` gains a `revision` subcommand that adds one to a counter per
work tree in its run state, run by `PostToolUse` and `PostToolUseFailure`
hooks on Bash, Edit, Write and NotebookEdit, as SPC-1040 states under "The
revision counter". One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture work tree with the counter at 4, when `meow-checks
revision` runs with a `PostToolUseFailure` input, then the counter reads 5,
   and the same for a `PostToolUse` input (REQ-2728). Closed by: a crate test
   naming REQ-2728, seen failing first.
2. Given `plugins/meow-checks/hooks/hooks.json`, when a test reads it, then
   both events run `revision` on Bash, Edit, Write and NotebookEdit. Closed
   by: a test under `plugins/meow-checks/tests/`.
3. Given a `run` recorded at counter 5 and two tool uses after it, when
   `evidence` runs, then it prints the record's revision 5 and the current 7,
   and the tree id alone decides whether the record is current. Closed by: a
   crate test.
4. Given `MEOWPAW_STATE=off`, when `revision` runs, then it writes nothing and
   exits 0. Closed by: a crate test.

## What to do

Add `revision` to the `verbs` feature of `crates/meow/`, keeping the counter
beside the ledger under the same lock and the same temporary-file rename
SPC-1040 states under "The ledger as run state". It writes the count and
nothing from its input (REQ-2724). Add the hooks file and its `## Hooks`
sentence, and hold the hook to SPC-1240. Document the counter on
`plugins/meow-checks/README.md`.

## Depends on

- TSK-4900 (not blocking): the new hook has to pass the hook check, and its
  rules can be met by hand before the check lands.

## Evidence

Not yet.

## Left alone

Staleness, which stays decided by the tree id, because an edit made outside
the session advances no counter.
