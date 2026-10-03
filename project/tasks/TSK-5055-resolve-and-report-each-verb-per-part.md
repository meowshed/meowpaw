---
id: TSK-5055
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2555
closes: [REQ-0078, REQ-3042, REQ-3043, REQ-3044]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Resolve and report each verb per part

`meow-checks` resolves each verb from the part's layered profile, takes
`--part <name>`, prints a `scope:` line on every report and records the
directory each run started in, as SPC-1040 states under "A verb in each
part". One task, one branch, one pull request, one review: the tests first,
then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository with two parts whose profiles bind `test` to
   different commands, when `meow-checks run test --part <name>` runs for
   each, then each runs its own part's command, and run from inside a part's
   directory with no `--part` it runs that part's (REQ-0078, REQ-3042).
   Closed by: a crate test naming REQ-3042, seen failing first.
2. Given the same fixture, when `status`, `run` or `evidence` reports, then
   its output carries `scope: <part> <directory>`, and in a repository with
   no `[parts]` it carries `scope: repository` (REQ-3043). Closed by: a
   crate test naming REQ-3043.
3. Given a run started in a part's directory, when its ledger record is read,
   then it carries the directory the run started in beside its scope
   (REQ-3044). Closed by: a crate test naming REQ-3044.
4. Given `--part` naming no declared part, when `run` starts, then it exits
   with an error naming the declared parts and runs nothing. Closed by: a
   crate test.

## What to do

Change the `verbs` feature of `crates/meow/` to resolve a verb per part from
the reader TSK-5050 adds, add `--part` to `status`, `run` and `evidence`,
and print the scope line as each report's first line after the profile's
state. Add the starting directory to the ledger record, keeping a record
without it readable as SPC-1040's "The ledger as run state" requires. Pin
the new lines in each subcommand's output test. Document the scope line and
`--part` on `plugins/meow-checks/README.md` and in the `verify` skill.

## Depends on

- TSK-5050 (blocking): a part's verbs come from the layered profile it reads.

## Evidence

Not yet.

## Left alone

`doctor`, which reports each part's verbs and which its own task builds, and
gating a change across two parts, which ADR-2650 leaves open.
