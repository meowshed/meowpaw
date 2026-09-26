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

`meow record` is `meow-method`'s program, behind the `record` feature, with its
launcher and `lib/layout.toml`. It reads `[record] root`, runs the six checks,
and writes nothing. Its eighteen fixtures pass against the binary and fail
against a program that returns nothing:

```text
$ python3 -m unittest discover -s plugins/meow-method/tests
Ran 18 tests in 0.768s
OK

$ MEOW_METHOD_BIN=stub/meow-method python3 -m unittest discover -s plugins/meow-method/tests
FAILED (failures=18)
```

There is a fixture for each check's planted defect, with its file and line, and
one for the clean record. Others cover a root outside the repository, given
both as an absolute path and as a relative one, a root that doesn't exist, an
unknown check, a file of no known kind, and the tree hashed before and after a
run. The crate's tests report `6 passed`, and the `record` binary for
`aarch64-apple-darwin` is 1,367,648 bytes.

The parity run, on the tree with BUG-1110's fix (#165) at the same revision:

```text
$ python3 tools/check_front_matter.py    1290 artifacts, 0 front matter failures
$ python3 tools/check_ids.py             1079 requirements, 0 failures
$ python3 tools/check_coverage.py        0 coverage failures
$ python3 tools/check_research.py        131 research artifacts, 0 missing sections
$ meow-method check
front-matter: 0 findings    identifiers: 0 findings    relations: 0 findings
index: 0 findings           coverage: 0 findings       shape: 0 findings
```

Before that fix, the relations check reported eight findings that none of the
four scripts reads: eight requirements elaborated research that never existed.
BUG-1110 records them.

## Left alone

This repository's switch to the unit, which TSK-1340 makes.
