---
id: TSK-2960
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1720
closes: [REQ-2572]
issue: 707
projected: b7a26f789f5c
---

# Read created issues back in one listing, and report a partial run as partial

`project` reads the issues it created back in one listing after its last
create, where it read each one back after creating it, and whenever it stops
before visiting every task it prints what it projected, what it created and
couldn't read back, and what it didn't project. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a stand-in `gh` failing the third of five creates, when `project`
   runs, then it sends the read-back listing, prints
   `partial: projected` with the first two tasks and `not projected` with the
   other three, and exits 3. Closed by:
   `Partial.test_a_failed_write_reads_back_and_reports_partial` in
   `plugins/meow-github/tests/test_github.py`.
2. Given the injected local clock two minutes ahead of the stand-in's `Date`,
   when the same run sends the listing, then its `since` is the `Date` of the
   run's first response and both created issues are read back. Closed by:
   `Partial.test_the_listing_starts_at_githubs_date` in
   `plugins/meow-github/tests/test_github.py`.
3. Given the stand-in answering the third create with a secondary throttle,
   when `project` runs, then it sends no listing, prints the first two tasks
   under `created, not read back` and the rest under `not projected`, and
   exits 3. Closed by:
   `Partial.test_a_throttle_sends_no_listing` in
   `plugins/meow-github/tests/test_github.py`.
4. Given a listing that omits a created issue, when `project` finishes, then
   that task goes under `created, not read back` with what the listing showed,
   and its task keeps `issue:`. Closed by:
   `Partial.test_an_issue_the_listing_omits_is_not_read_back` in
   `plugins/meow-github/tests/test_github.py`.
5. Given five tasks and a stand-in that creates every issue, when `project`
   runs, then the stand-in records one read-back listing and no read of a
   single created issue. Closed by:
   `Partial.test_created_issues_are_read_back_in_one_listing` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Replace the read after each create in `crates/meow/src/github/project.rs` with
one listing after the last create,
`repos/{r}/issues?state=all&since=<start>&per_page=100`, uncached and paged
through the layer, where `<start>` is the `Date` of the run's first response.
Match each created issue by number. The read of an issue already mapped to a
task stays as it is. Send the listing after a failed write or a refusal, and
not after a throttle or a ceiling, because a request sent while throttled
risks the integration.

Print the `partial:` line after the listing, where the listing runs, and exit
3, as SPC-1080's section "Projecting the record onto a tracker" states. A task
counts as projected when its issue was updated or found unchanged in this run,
or was created and read back matching the record. Replace the line
`stopped part way; the tasks above it were projected`.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:`. The README says the created
issues are read back in one listing and shows the `partial:` line.

## Depends on

- TSK-2940 (blocking): the listing goes through the layer, and the run stops
  at a throttle only once the layer does.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

A ceiling's stop, which TSK-2950 adds and which reaches the same `partial:`
line once both land. An issue created by a `POST` whose response was lost,
which ADR-1810 leaves unsettled. `history`, which keeps ADR-1290's rule of no
partial document.
