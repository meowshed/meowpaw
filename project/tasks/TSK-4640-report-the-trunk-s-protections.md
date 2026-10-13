---
id: TSK-4640
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2420
closes: [REQ-2194]
issue: 949
projected: 2c2e61409820
tracked: ec199afe8c34
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

`meow-github protections`, in `crates/meow/src/github/protections.rs`, reads
`repos/{r}/branches/{trunk}/protection` and
`repos/{r}/rules/branches/{trunk}` through the request layer and prints the
six lines SPC-1080 states, closing REQ-2194. Each test is in
`crates/meow/tests/protections.rs`, runs `paw github protections o/r` against
a stand-in `gh` and compares the report's lines whole. Each failed first,
before the subcommand existed.

1. `a_classic_protection_reports_each_of_the_six` closes criterion 1: force
   pushes blocked and signed commits `in force`, the other four `absent`,
   exit 0.
2. `a_ruleset_counts_where_the_branch_has_no_protection` closes criterion 2:
   a 404 for the protection and a `required_linear_history` rule give
   `linear history: in force` and the rest `absent`.
   `every_ruleset_rule_counts` holds each of the six rule types to its line.
3. `a_refused_read_leaves_each_protection_it_holds_unread` closes criterion
   3: a 403 for the rules prints the layer's `refused:` line, names every
   protection it couldn't read `unread`, none `absent`, and exits 3. A
   protection the classic answer shows in force stays `in force`.
4. Every test above calls `every_call_reads`, which closes criterion 4: each
   call the stand-in logged is `gh api <endpoint>` with no `-X`,
   `--method`, `-f` or `-F`.

`no_trunk_is_reported_and_reads_nothing` holds SPC-1080's sentence on an
undeclared trunk. `unit_help.rs` holds the subcommand's lines to the first
words its help states, and the help gives the two `gh api` reads as the
manual equivalent. `docs/interface.md` lists the subcommand, and
`plugins/meow-github/README.md` documents it.

I made two choices the task leaves open. The report prints the credential
line first and the four budget lines last, as `project` and `sync` do,
because REQ-2568 and REQ-2582 hold every run of the request layer to them.
After a throttle or a rejected credential, the report sends no second read,
as the layer's other callers don't. The layer gained `get_unless_missing`,
which reads a 404 as an answer, because a 404 on the protection is how GitHub
says the branch has none.

SPC-1080 reads a 404 on the protection as no protection. Whether GitHub also
answers 404 to a credential without administration access, which would print
`absent` where the truth is unread, only a run against this repository with
such a credential shows.

Every stage passed in pull request #PR.

## Left alone

Changing any protection, which ADR-2520 leaves to the owner, and the
governance guard, which already asks before a write to
`branches/{b}/protection`.
