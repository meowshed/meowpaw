---
id: TSK-4640
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2420
closes: [REQ-2194]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Report the trunk's protections with `meow-github protections`

`meow-github protections` reads the declared trunk's protection and the rules
in force on it through the request layer and prints each of six protections
as in force or absent, writing nothing, as SPC-1080 states under "Reporting
the trunk's protections". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a stand-in `gh` answering with a protection that blocks force pushes
   and requires signed commits, when `protections` runs, then it prints the
   six lines in order, those two as `in force` and the other four as
   `absent`, and exits 0 (REQ-2194). Closed by: a crate test naming REQ-2194,
   seen failing first.
2. Given a stand-in answering 404 for the protection and a ruleset requiring
   linear history, when `protections` runs, then `linear history: in force`
   and the rest `absent`. Closed by: a crate test.
3. Given a stand-in answering 403 for the rules, when `protections` runs,
   then each protection it couldn't read is named as unread, none as absent,
   and it exits 3. Closed by: a crate test.
4. Given the stand-in's record of the requests it received, when any of the
   runs above ends, then every request is a `GET`. Closed by: a crate test.

## What to do

Add `protections` to the `github` feature of `crates/meow/`, sending both
reads through `crates/meow/src/github/request.rs`. Read the trunk from
`[git] trunk`. Pin its output lines in the subcommand's own test, as
SPC-1080's "Each subcommand makes one determination" asks, and give its help
the manual equivalent, the two `gh api` reads. Document it on
`plugins/meow-github/README.md`.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

Changing any protection, which ADR-2520 leaves to the owner, and the
governance guard, which already asks before a write to
`branches/{b}/protection`.
