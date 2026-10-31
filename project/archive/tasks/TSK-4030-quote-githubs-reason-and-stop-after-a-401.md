---
id: TSK-4030
artifact: task
status: done
revised: 2026-09-30
realises: ADR-2330
closes: [REQ-3324, REQ-3326]
issue: 784
projected: 924721f27769
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Quote GitHub's reason on every refusal line, and send nothing after a 401

Every `refused:` and `unauthenticated:` line ends with GitHub's own message,
and after a 401 the request layer sends no further request in the run. One
task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a create answered 403 with `X-Accepted-GitHub-Permissions: issues=write`
   and the message `Resource not accessible by personal access token`, when
   `project` runs, then it prints
   `refused: POST repos/o/r/issues needs issues=write; GitHub said "Resource not accessible by personal access token"`
   and exits 3. Closed by:
   `Refusal.test_a_403_names_the_github_permission` in
   `plugins/meow-github/tests/test_github.py`.
2. Given a create answered 401 with the message `Bad credentials`, when
   `project` runs, then it prints
   `unauthenticated: POST repos/o/r/issues; GitHub said "Bad credentials"`
   and exits 3. Closed by: `Refusal.test_a_401_is_unauthenticated` in
   `plugins/meow-github/tests/test_github.py`.
3. Given two mapped tasks whose first issue's read is answered 401, when
   `project` runs, then the stand-in records no request after that read, the
   run prints the `partial:` line and exits 3. Closed by:
   `Refusal.test_a_401_ends_the_run` in
   `plugins/meow-github/tests/test_github.py`.
4. Given a 403 carrying neither permission header, when `project` runs, then
   the line quotes GitHub's message once and adds no second quotation.
   Closed by: `Refusal.test_a_403_naming_nothing_quotes_github` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Change the refusal lines and the layer's handling of a 401 as SPC-1080's
section "The GitHub request layer" states. The checks named above that
TSK-2970 wrote change with this task, because the lines they compare change;
change each in the commit that holds the new checks, and say so in its
message.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:` and the two pages under `docs/`
that name it. The README shows the lines with GitHub's reason and says a run
sends nothing after a 401.

## Depends on

- TSK-4020 (not blocking): both raise `meow-github`'s version and change
  `crates/meow/src/github/project.rs`, so whichever lands second takes the
  next version above the first.

## Evidence

`exchange` in `crates/meow/src/github/request.rs` ends each refusal line
with `; GitHub said "<message>"` where GitHub's answer carries a message the
line doesn't already quote, and answers a 401 with the new
`Failure::Rejected`. After a 401 the layer returns `Failure::Rejected` for
every later call without starting `gh`. `project` stops at a rejected
credential as it does at a throttle, through `halt`, which names what it
stopped at, and `history` reports the listing unread.

Each criterion is closed by the check it names, in
`plugins/meow-github/tests/test_github.py`:

1. `Refusal.test_a_403_names_the_github_permission`
2. `Refusal.test_a_401_is_unauthenticated`
3. `Refusal.test_a_401_ends_the_run`
4. `Refusal.test_a_403_naming_nothing_quotes_github`

No criterion rests on judgement. The checks for criteria 1 to 3 failed first,
in the commit that holds them alone, where the `test` verb exited 1. That
commit also changes `Refusal.test_a_403_names_the_oauth_scopes` and
`Refusal.test_history_reports_a_refusal_as_unread`, whose lines now end with
GitHub's reason. Criterion 4's check passed before the change, as it should,
because the line with neither header already quoted the message once.
`format`, `lint`, `check`, `test` and `build` each pass on the change's
tree, as the pull request cites.

I made two choices the task leaves open. A read-back listing answered 401
leaves each created issue under `created, not read back` with
`the listing's credential was rejected`. A call made after a 401, which the
layer doesn't send, reads
`unauthenticated: <method> <endpoint> not sent, because GitHub rejected this run's credential`,
so a caller that asks is told why nothing went out.

Review added one more choice. A quoted message has any control character or
line separator printed as a space and any backslash or double quote escaped,
and the `HTTP <status>:` line gets the same flattening, so GitHub's text
can't split a report's line or end its quotation; `a_quoted_message_stays_on_its_line`
in `request.rs` checks it. Two records now say less than the code, and this
step may not edit them: SPC-1080 doesn't state the escaping, and this task's
opening says every line ends with GitHub's message, where a line with no
permission header quotes it earlier in the line.

`meow-github` goes to 0.11.0, and its README shows the lines with GitHub's
reason and says a run sends nothing after a 401.

## Left alone

The `X-GitHub-SSO` authorisation URL, which ADR-2330 leaves unsettled.
