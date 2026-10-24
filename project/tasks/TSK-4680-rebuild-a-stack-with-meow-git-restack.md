---
id: TSK-4680
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2430
closes: [REQ-1824, REQ-1826, REQ-1828]
issue: 952
projected: 05a36930a8a4
tracked: d813f6e9eed1
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Rebuild a stack with `meow-git restack`

`meow-git restack <branch>...` rebases each layer onto the one below, signs
again where the profile asks, stops on a conflict with neither side
discarded, and prints each branch it updated with its lease push, pushing
nothing, as SPC-1060 states under "Restacking". One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given a scratch repository with a trunk and a stack of three branches whose
   bottom's base moved, when `restack` runs on the three, then each is rebased
   onto the one below, `updated:` names all three with the lease push
   `git push --force-with-lease=<branch>:<revision> origin <branch>`, and no
   remote ref changed (REQ-1828). Closed by: a crate test naming REQ-1828,
   seen failing first.
2. Given the same stack with a conflict in the middle branch, when `restack`
   runs, then it aborts that rebase, prints `conflict:` with the branch and
   its files, `updated:` for the bottom and `not updated:` for the other two,
   leaves the middle branch at its old revision and exits 1 (REQ-1824,
   REQ-1826). Closed by: a crate test naming both.
3. Given `require_signatures = true` and a signing key in the scratch
   repository, when `restack` rewrites a branch, then each rewritten commit
   carries a good signature (REQ-2614). Closed by: a crate test.
4. Given a branch in the stack with uncommitted changes, when `restack` runs,
   then it rewrites nothing and names that branch. Closed by: a crate test.

## What to do

Add `restack` to the `git` feature of `crates/meow/`, running git through the
one helper SPC-1060 states under "Source-control discipline". Read the
remote-tracking revision of each branch before rewriting it, because that is
the revision the lease names. Pin its output lines and name its manual
equivalent in its help, as SPC-1080's "Each subcommand makes one
determination" asks. Document it on `plugins/meow-git/README.md`.

## Depends on

Nothing.

## Evidence

`crates/meow/tests/restack.rs` closes each criterion against a scratch
repository with a local bare remote, and each test failed before `restack`
existed. Criterion 1 is closed by
`each_layer_is_rebased_onto_the_one_below_and_nothing_is_pushed` (REQ-1828),
criterion 2 by `a_conflict_stops_the_restack_and_names_the_branch` (REQ-1824,
REQ-1826), criterion 3 by `a_rewritten_commit_is_signed_where_the_profile_asks`
(REQ-2614) and criterion 4 by
`a_branch_with_uncommitted_changes_stops_it_before_any_rewrite`. Two more tests
hold what SPC-1060 adds: a branch checked out in another working tree stops the
restack, and a branch whose base hasn't moved is left as it is. The help and
its pinned first words are held by `crates/meow/tests/unit_help.rs`.

Every stage passed in pull request #1072.

## Left alone

Pushing, which this repository's permissions deny for a forced push and which
ADR-2550 leaves to a later decision, so the command prints the lease push for
a person to run.
