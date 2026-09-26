---
id: TSK-1330
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1070
closes:
  [
    REQ-0137,
    REQ-0145,
    REQ-0246,
    REQ-0520,
    REQ-0521,
    REQ-0524,
    REQ-0573,
    REQ-0590,
    REQ-0656,
  ]
issue: 144
---

# Check the record where the repository declares it

**Amended by ADR-1110.** The program is the `record` subcommand of the native
tool `meow`, behind `meow-method`'s feature, with a launcher as SPC-1080
states, and this task depends on TSK-1350, which builds the crate. The rest
stands.

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-method/` with its manifest, licence headers and a budget
of 0. Write the layout SPC-1070 states as `lib/layout.toml`, and the program
with `check` and `check <name>`, reading `[record] root` (REQ-0520, REQ-0521)
and running the six checks SPC-1070 lists: front matter with the status
vocabulary (REQ-0573, REQ-0590), identifiers, relations (REQ-0656), the record
index (REQ-0524), coverage (REQ-0246) and shape (REQ-0145). No check writes a
file (REQ-0137).

Write a fixture per check that plants a defect in a scratch record and one
that runs every check on a clean record, one with `root` outside the
repository, and one that compares the tree before and after, each seen failing
first against a program that returns nothing (REQ-2072).

Run the program and the four scripts it replaces on this repository at the
same revision, and publish both outputs.

## Depends on

Nothing. ADR-1100 and SPC-1070 are approved.

## Evidence

Not yet. The task closes on the fixtures, each shown first failing, and the
parity run.

## Left alone

This repository's switch to the unit, which TSK-1340 makes.
