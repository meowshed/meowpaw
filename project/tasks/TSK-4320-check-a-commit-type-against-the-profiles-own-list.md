---
id: TSK-4320
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2320
closes: [REQ-2952]
issue: 939
projected: f48e239cbd56
tracked: 74abb62dc0b6
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Check a commit type against the profile's own list

`meow-scm check-message` accepts a type only where the profile's
`[commits.types]` declares it, and holds no list of types of its own, as
SPC-1050 states. One task, one branch, one pull request, one review: the
tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a profile whose `[commits.types]` declares `spec` and `chore` only,
   when `check-message` reads `feat: add a verb`, then it reports the
   `declared type` check failed and exits 1 (REQ-2952). Closed by: a crate
   test naming REQ-2952, seen failing first or, where it passes before the
   change, cited as the test that holds the rule.
2. Given the same profile, when `check-message` reads `spec: state the
profile`, then it reports no violation of the type check (REQ-2952).
   Closed by: a crate test naming REQ-2952.
3. Given the `scm` feature's source, when a test searches it, then it finds
   no list of conventional types the type check reads. Closed by: a crate
   test naming REQ-2952.

## What to do

Read the type check in the `scm` feature of `crates/meow/` and confirm it
reads `[commits.types]` alone. Where any built-in list feeds it, remove that
path. Where none does, the tests above pin the behaviour, because ADR-2370
asks that the rule be held by a test and the tree may already meet it.

## Depends on

Nothing.

## Evidence

Closed in pull request 1039. The type check already read `[commits.types]`
alone, so no test could fail first, and each is cited as the test that holds
the rule. All are in `crates/meow/tests/commit_types.rs`:

1. `a_type_the_profile_doesnt_declare_fails_the_declared_type_check`
   (REQ-2952), over a plain, a scoped and a `!` subject.
2. `every_conventional_type_the_profile_leaves_out_fails_the_check`
   (REQ-2952), over twelve conventional names, so a built-in list in any form
   lets one through and fails it.
3. `a_declared_type_passes_the_declared_type_check` and
   `a_type_no_list_holds_passes_when_the_profile_declares_it` (REQ-2952), which
   hold the other direction, a name outside every list included.
4. `no_declared_type_means_no_fallback_list` (REQ-2952), over an empty table, a
   `types` that isn't a table and a meaning that isn't one of the four.
5. `the_scm_source_holds_no_list_of_conventional_types` (REQ-2952), a search
   of the program part of `scm.rs` for the twelve names as literals.

Under a mutation of the check that accepts `feat` and `fix` whatever the
profile declares, tests 1, 2 and 5 failed, and 3 and 4 passed, as they hold
what the mutation doesn't touch. The source search reads only literals, so
test 2 is the one that holds the rule against any other form of list.

Stages: the pull request's `gate` check, and `paw check`, which printed 0
findings. No documentation changed, because the behaviour didn't.

## Left alone

The attribution check, which runs whatever the profile says, and the
undeclared convention, which keeps exit 3 as SPC-1050 states.
