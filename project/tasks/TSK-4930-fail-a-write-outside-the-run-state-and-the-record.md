---
id: TSK-4930
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2525
closes: [REQ-1429]
issue: 969
projected: 734fbb40a654
tracked: 6b65141732e8
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a write outside the run state and the record

A crate test fails where a subcommand writes a file outside the repository
other than under the run state, `<state>/meowpaw/`, and the record's declared
root, as SPC-1080 states under "What the harness writes and reads". One task,
one branch, one pull request, one review: the tests first, then the change,
its documentation and its marks.

## Acceptance criteria

1. Given every subcommand the crate ships, run on a fixture repository with
   its home, state and temporary directories pointed at fixture paths, when
   the test compares those paths before and after, then the only files
   created or changed outside the repository are under the state directory or
   the record root the fixture's profile declares (REQ-1429). Closed by: a
   crate test naming REQ-1429, seen failing first against a fixture
   subcommand that writes to the home directory.
2. Given a source file in the crate that opens a path for writing, when the
   test reads the source, then each such call goes through the run state's
   helper, the record writer or a path under the repository. Closed by: a
   crate test.

## What to do

Add the test to `crates/meow/`. Where a subcommand writes elsewhere today,
such as a temporary file outside the state directory, move the write or
record a defect naming it. Lock files under `$XDG_RUNTIME_DIR` count as run
state, as SPC-1040 states.

## Depends on

Nothing.

## Evidence

The tests in `crates/meow/tests/writes.rs` pinned what the crate already did, so they passed when
they were written, and each can fail. `the_comparison_finds_a_write_to_the_home_directory` shows the
snapshot comparison finds a file created in the home directory, and
`no_subcommand_writes_outside_the_state_the_repository_and_the_record` closes criterion 1 (REQ-1429):
it runs seventeen calls of seven units with home, temporary and state directories of its own
and finds nothing changed outside the state and the repository, and no change to the repository
from a read-only subcommand. `each_write_in_the_source_is_one_the_table_names` closes criterion 2:
a table names the file, the number of calls that write and where each writes, so a new call fails
until a person reads where it goes. `mise run all` passed with exit status 0.

## Left alone

The shell launchers and the release scripts, which write only build output
inside the repository, and the platform's own files.
