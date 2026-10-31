---
id: TSK-4020
artifact: task
status: done
revised: 2026-09-30
realises: ADR-2320
closes: [REQ-3322]
issue: 783
projected: fe9668217f1f
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Start the read-back listing at the earliest created issue's own `updated_at`

`project` starts its read-back listing at the earliest `updated_at` among the
run's create answers, and at the first response's `Date` only where no create
answer carries one, so a run given the repository's name reads back an issue
GitHub stamped a second before its answer. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a stand-in `gh` that writes each issue a second before the `Date` of
   the answer it sends, the repository named on the command line and two
   unmapped tasks, when `project` runs, then the listing's `since` equals the
   first issue's `updated_at`, both issues read back, no `partial:` line is
   printed, and the run exits 0. Closed by:
   `ReadBack.test_the_listing_starts_at_the_first_issues_own_time` in
   `plugins/meow-github/tests/test_github.py`.
2. Given the same stand-in with create answers carrying no `updated_at`, when
   `project` runs, then the listing's `since` equals the `Date` of the run's
   first response. Closed by:
   `ReadBack.test_with_no_updated_at_the_listing_starts_at_the_first_date` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Change where `<start>` comes from in `crates/meow/src/github/project.rs` and
the request layer, as SPC-1080's section "Projecting the record onto a
tracker" states. Keep `Partial.test_the_listing_starts_at_githubs_date`
passing: with the local clock ahead of GitHub's, the start still comes from
GitHub's clock.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:` and the two pages under `docs/`
that name it. The README says where the listing starts.

## Depends on

Nothing.

## Evidence

`read_back` in `crates/meow/src/github/project.rs` starts the listing at the
earliest `updated_at` among the run's create answers, which `run` keeps on
each created issue, and at `Layer::began` only where no answer states one.
A time is used only where it has GitHub's form, `2026-09-30T17:47:50Z`,
because it goes into the listing's address as it stands.

Each criterion is closed by the check it names, in
`plugins/meow-github/tests/test_github.py`:

1. `ReadBack.test_the_listing_starts_at_the_first_issues_own_time`
2. `ReadBack.test_with_no_updated_at_the_listing_starts_at_the_first_date`

No criterion rests on judgement. Criterion 1's check failed first, in the
commit that holds the checks alone, where the `test` verb exited 1. It also
requires no read by number, because TSK-4040's reads would otherwise find
the issue the listing missed and hide a wrong start. Criterion 2's check
passed there, as it should, because it pins the fallback, which is the start
the code had before this task. `Partial.test_the_listing_starts_at_githubs_date`
still passes: the stand-in's `updated_at` is on GitHub's clock, as the `Date`
was. `format`, `lint`, `check`, `test` and `build` each pass on the change's
tree, as the pull request cites.

I made one choice the task leaves open. An `updated_at` that isn't in
GitHub's form is ignored, as a missing one is.

`meow-github` goes to 0.12.0, and its README says where the listing starts.

## Left alone

The refusal lines and the stop after a 401, which TSK-4030 changes.
