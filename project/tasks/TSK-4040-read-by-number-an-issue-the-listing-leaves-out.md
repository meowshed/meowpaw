---
id: TSK-4040
artifact: task
status: done
revised: 2026-09-30
realises: ADR-2340
closes: [REQ-3322]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Read by its number each created issue the read-back listing leaves out

After the read-back listing, `project` reads by number each issue it created
that the listing left out, and reports it as projected where it reads back as
written. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a stand-in `gh` that leaves the second of two created issues out of
   the listing and answers its read by number, when `project` runs, then both
   tasks print `read back`, the stand-in records one read of
   `repos/o/r/issues/2`, no `partial:` line is printed, and the run exits 0.
   Closed by: `ReadBack.test_an_issue_the_listing_leaves_out_is_read_by_number`
   in `plugins/meow-github/tests/test_github.py`.
2. Given the same stand-in answering that read with a different body, when
   `project` runs, then the second task is under `created, not read back` with
   `reads differently from what was written`, and the run exits 3. Closed by:
   `Partial.test_an_issue_the_listing_omits_is_not_read_back` in
   `plugins/meow-github/tests/test_github.py`.
3. Given five created issues all in the listing, when `project` runs, then
   the stand-in records no read of a single created issue. Closed by:
   `Partial.test_created_issues_are_read_back_in_one_listing` in
   `plugins/meow-github/tests/test_github.py`.
4. Given a secondary throttle answering the read by number, when `project`
   runs, then the issue is under `created, not read back` with
   `no read ran`, the stand-in records no request after the throttled read,
   and the run exits 3. Closed by:
   `ReadBack.test_a_throttled_read_by_number_stops_the_reads` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Add the reads by number to `settle` in `crates/meow/src/github/project.rs`,
as SPC-1080's section "Projecting the record onto a tracker" states. The
stand-in's `omit` leaves an issue out of the listing and still answers a read
of it by number, and `alter` and `retitle` change what the listing shows;
give the stand-in a way to change what a read by number shows too.
`Partial.test_an_issue_the_listing_omits_is_not_read_back` changes with this
task, because an issue the listing omits and that reads back by number is now
projected; change it in the commit that holds the new checks, and say so in
its message.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:` and the two pages under `docs/`
that name it. The README says an issue the listing leaves out is read by its
number.

## Depends on

- TSK-4020 (not blocking): both change `settle` and raise `meow-github`'s
  version, so whichever lands second takes the next version above the first.
- TSK-4030 (not blocking): it changes the refusal lines a read by number can
  print, and raises the same version.

## Evidence

`settle` in `crates/meow/src/github/project.rs` sends the read-back listing
as before, then reads by number, through `get_mapped`, each created issue the
listing left out. An issue that reads back as written is projected, one that
reads differently goes under `created, not read back`, and a throttle during
the reads stops them and leaves each remaining issue under
`created, not read back` with `no read ran`.

Each criterion is closed by the check it names, in
`plugins/meow-github/tests/test_github.py`:

1. `ReadBack.test_an_issue_the_listing_leaves_out_is_read_by_number`
2. `Partial.test_an_issue_the_listing_omits_is_not_read_back`
3. `Partial.test_created_issues_are_read_back_in_one_listing`
4. `ReadBack.test_a_throttled_read_by_number_stops_the_reads`

No criterion rests on judgement. The checks for criteria 1, 2 and 4 failed
first, in the commit that holds them alone, where the `test` verb exited 1.
That commit changes the `omit` case of criterion 2's check to read the issue
by number with another body, because an issue the listing omits and that
reads back is now projected. Criterion 3's check passed before the change,
as the task expects, because no issue was left out. `format`, `lint`,
`check`, `test` and `build` each pass on the change's tree, as the pull
request cites.

I made one choice the task leaves open. A read by number that fails other
than by a throttle, a ceiling or a 401 puts the issue under
`created, not read back` with `couldn't be read`, prints the failure, and the
reads go on to the next issue, as a failed read of a mapped issue does. A 401
stops the reads as a throttle does, as SPC-1080 states; review found the
first version didn't, and criterion 4's check now sends one.

`meow-github` goes to 0.10.0, and its README says an issue the listing leaves
out is read by its number.

## Left alone

`history`, which reads no issue by number.
