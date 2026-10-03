---
id: TSK-4930
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2525
closes: [REQ-1429]
issue:
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

Not yet.

## Left alone

The shell launchers and the release scripts, which write only build output
inside the repository, and the platform's own files.
