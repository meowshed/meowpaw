---
id: BUG-1580
artifact: bug
status: approved
severity: minor
violates: REQ-1429
enters: design
found: 2026-10-11
revised: 2026-10-11
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The ledger copies the index into the temporary directory to bind a result to a tree

SPC-1080 lists what the harness writes: its run state, the record and the
repository. `meow verbs` copies the repository's index to a temporary file in the system's temporary directory to compute the tree id of the working tree, which is a write outside the run state and the record that SPC-1080 doesn't list.

## Reproduction

Seen on the trunk after pull request 1047.

1. Run the crate's write test, `no_subcommand_writes_outside_the_state_the_repository_and_the_record`
   in `crates/meow/tests/writes.rs`, with `TMPDIR` pointed at a fixture directory.
2. Read the `WRITES` table beside it, which names the call by file.

## What the system does

The call writes under the temporary directory and removes what it wrote. The
test's temporary directory is empty again afterwards, so the write is found
only by reading the source, which the table does.

## What it should do, and why

REQ-1429 says the harness writes nothing outside its run state and the record,
because a file in a shared directory is a file another process can read or
replace. The write belongs under `<state>/meowpaw/`, or SPC-1080 names the
temporary directory as one of the places the harness writes.

## Triage

It enters at design, because moving the write under the run state fails where
state writing is off (`MEOWPAW_STATE=off`), and the choice between a place in
the repository, the temporary directory named in the specification and a
different way to compute the tree is a decision. Severity is minor: the file
is removed at once and holds a copy of what the repository already holds.

## Closed by

The write moved or the specification amended, and its entry in the `WRITES`
table of `crates/meow/tests/writes.rs` naming where it goes.
