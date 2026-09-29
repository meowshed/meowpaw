---
id: BUG-1340
artifact: bug
status: approved
severity: major
violates: REQ-2406
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 674
---

# `meow-unattended plan` leaves an approved record unprotected when its status is quoted, commented or in CRLF

`plan` writes an `Edit` deny rule only for a requirement or decision whose
front matter holds the exact text `status: approved` after a leading `---\n`.
A record that says the same thing as `status: "approved"`, as
`status: approved # frozen`, or with CRLF line endings gets no rule, and the
output doesn't say the record is unprotected.

## Reproduction

`main` at b42eaa1, with `meow-unattended` 0.2.0 built by
`crates/meow/build-units`.

1. In a scratch git repository, declare `[git] trunk = "main"`,
   `[record] root = "project"`, and an `[unattended]` table with
   `permission_mode = "dontAsk"`, `budget_usd = 1`, `gates = []` and one unit.
2. Add four approved requirements under `project/requirements/`, whose
   `status` lines read `status: approved`, `status: "approved"` and
   `status: approved # frozen`, and a fourth written `status: approved` with
   CRLF line endings.
3. Run `meow-unattended plan`.

## What the system does

`plan` exits 0 and prints one deny rule on the record, for the
plain form. The other three approved requirements get none, and nothing in
the output names them. `front_matter` in `crates/meow/src/unattended.rs`
returns nothing for a file that doesn't start with `---\n`, and `approved`
compares the raw value, quotes and comment included, with `approved`.

## What it should do, and why

`plan` denies `Edit` on every requirement and decision recorded `approved`,
whichever of these forms its front matter takes, as SPC-1200's section "The
snapshot" states. Those rules are how ADR-2000 keeps an unattended run from
amending an approved record, which REQ-2406 forbids unless the repository
declares `amend_approved = true`. `paw check` reads the quoted and commented
forms as `approved`, so today the checker calls a record frozen that the
run's deny rules leave open.

## Triage

It enters at implement, because REQ-2406, ADR-2000 and SPC-1200 are right and
the program reads the front matter more narrowly than YAML does. ADR-2000
postpones closing REQ-2406 until a run starts, but the deny rules it names as
the means are built now, and they miss these records. Major, because the
failure is silent: the plan reports protection it doesn't give.

## Closed by

The reproduction as a fixture in `plugins/meow-unattended/tests/test_unattended.py`,
`Snapshot.test_approved_in_every_front_matter_form`, which counts one deny
rule for each of the four approved forms and none for a quoted draft.

## Tasks

- [ ] T-001 TSK-3320 read an approved record's status the way `paw check`
      does, in `crates/meow/src/unattended.rs`
