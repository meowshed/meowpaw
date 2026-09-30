---
id: TSK-4020
artifact: task
status: approved
revised: 2026-09-30
realises: ADR-2320
closes: [REQ-3322]
issue:
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

Not yet.

## Left alone

The refusal lines and the stop after a 401, which TSK-4030 changes.
