---
id: TSK-5060
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2555
closes: [REQ-0133, REQ-3048]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Activate each pack where its marker is

`meow-markdown`, `meow-mise` and `meow-gotask` each detect their toolchain by
a marker file git tracks and report once for each directory holding one,
naming that directory, as SPC-1190 states under "Detection". One task, one
branch, one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with a `mise.toml` in `a/` and none at the
   root, when `meow-mise status` runs, then it reports for `a/` alone,
   naming the directory, and reports nothing for the root (REQ-0133,
   REQ-3048). Closed by: a crate test naming REQ-3048, seen failing first.
2. Given a fixture with Markdown markers in two directories, when
   `meow-markdown status` runs, then it reports once per directory, each
   naming its directory. Closed by: a crate test naming REQ-0133.
3. Given a fixture with a `Taskfile.yml` in one part of a repository that
   declares two parts, when `meow-gotask status` runs, then its report names
   the part and its directory. Closed by: a crate test.

## What to do

Change each pack's detection in `crates/meow/` from once per work tree to
once per directory holding its marker, starting none of the tool to decide.
Where the root profile declares `[parts]`, name the part as well as the
directory, through the reader TSK-5050 adds; without it, name the directory.
Document the change on each pack's page; SPC-1190's failure rows stay as they are.

## Depends on

- TSK-5050 (not blocking): a report names the part where one is declared,
  and names the directory without it.

## Evidence

Not yet.

## Left alone

The language packs SPC-1190 orders, which detect per marker from their first
release under EPC-2560's tasks.
