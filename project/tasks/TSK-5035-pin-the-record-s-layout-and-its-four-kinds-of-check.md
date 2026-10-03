---
id: TSK-5035
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2570
closes: [REQ-1660, REQ-1662, REQ-1668]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin the record's layout and the four kinds of check

A crate test fails where a file under this repository's record root sits
outside the layout `paw template` gives its users, and a test pins that the
front matter check fails a requirement whose `verification` names a fifth
kind, as SPC-1090 and SPC-1070 state. One task, one branch, one pull request, one review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a copy of this repository's record with one file added under the record root in no kind's directory, when the crate test runs, then it fails naming the file (REQ-1668, REQ-1660). Closed by: a crate test naming REQ-1668, seen failing first.
2. Given this repository's own record, when the same test runs, then it passes. Closed by: the `test` verb's output.
3. Given a fixture requirement with `verification: manual`, when `paw check` runs, then the front matter check reports it and exits 1 (REQ-1662). Closed by: a crate test naming REQ-1662.

## What to do

Add both tests to the `record` feature of `crates/meow/`, reading the layout
from `plugins/meow-flow/lib/layout.toml` and never from a list of their own.
The record's checks already run in this repository's gate, so no profile
change is needed.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The record's contents, which the method's checks already hold.
