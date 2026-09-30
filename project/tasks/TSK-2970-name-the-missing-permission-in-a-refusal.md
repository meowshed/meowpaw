---
id: TSK-2970
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1720
closes: [REQ-2574]
issue: 708
projected: 53ab6e7b4959
---

# Name the endpoint and the missing permission in a refusal

A 401, a 403 that isn't a throttle, and a 404 on an object the record maps are
each reported with the method, the endpoint and the permission GitHub named,
or GitHub's own message where it named none. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a stand-in `gh` answering a create with 403 and
   `X-Accepted-GitHub-Permissions: issues=write`, when `project` runs, then
   it prints `refused: POST repos/o/r/issues needs issues=write` and exits 3.
   Closed by: `Refusal.test_a_403_names_the_github_permission` in
   `plugins/meow-github/tests/test_github.py`.
2. Given a 403 carrying only `X-Accepted-OAuth-Scopes` and `X-OAuth-Scopes`,
   when `project` runs, then the report names the accepted scopes and the
   credential's own. Closed by:
   `Refusal.test_a_403_names_the_oauth_scopes` in
   `plugins/meow-github/tests/test_github.py`.
3. Given a 403 carrying neither header, when `project` runs, then the report
   says `GitHub named no permission` and quotes GitHub's message. Closed by:
   `Refusal.test_a_403_naming_nothing_quotes_github` in
   `plugins/meow-github/tests/test_github.py`.
4. Given a 404 on a task's mapped issue, when `project` runs, then the report
   adds `, or it is hidden from this credential`. Closed by:
   `Refusal.test_a_404_on_a_mapped_issue_may_be_hidden` in
   `plugins/meow-github/tests/test_github.py`.
5. Given a 401, when `project` runs, then it prints
   `unauthenticated: <method> <endpoint>` and exits 3. Closed by:
   `Refusal.test_a_401_is_unauthenticated` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Report a refusal in the layer, as SPC-1080's section "The GitHub request
layer" states, from the status and headers `gh api --include` prints on
standard output for a refused call. Take the permission from
`X-Accepted-GitHub-Permissions`, and otherwise from `X-Accepted-OAuth-Scopes`
beside `X-OAuth-Scopes`. A 403 the layer reads as a throttle stays a
throttle. `history` reports a refusal as unread, naming the listing, as
ADR-1290 states, with the same permission text.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:`. The README's section "When it
can't read" shows the three refusal lines.

## Depends on

- TSK-2940 (blocking): the layer is what reads a refused call's headers.

## Evidence

`exchange` in `crates/meow/src/github/request.rs` returns the new
`Failure::Refused` for a 401, for a 403 that isn't a throttle and for a 404
on an object the record maps. `permission` takes the permission from
`X-Accepted-GitHub-Permissions`, or else from `X-Accepted-OAuth-Scopes`
beside `X-OAuth-Scopes`, or else quotes GitHub's message. `get_mapped` and a
`PATCH` mark the object as one the record maps. `project` prints the line on
a line of its own, above the line naming the task it concerns. `history`
prints it after `unread:`, and after the listing's name where a listing was
refused.

Each criterion is closed by the check it names, in
`plugins/meow-github/tests/test_github.py`:

1. `Refusal.test_a_403_names_the_github_permission`
2. `Refusal.test_a_403_names_the_oauth_scopes`
3. `Refusal.test_a_403_naming_nothing_quotes_github`
4. `Refusal.test_a_404_on_a_mapped_issue_may_be_hidden`
5. `Refusal.test_a_401_is_unauthenticated`

`Refusal.test_history_reports_a_refusal_as_unread` covers the sentence of
What to do that no criterion names. No criterion rests on judgement. The six
checks failed first, in the commit that holds them alone, where the `test`
verb exited 1. A commit of its own then changes
`History.test_a_refused_listing_leaves_the_history_unread`, which named
`HTTP 403` after the endpoint, the form this task replaces. Review added
`Refusal.test_a_404_on_an_unmapped_object_is_no_refusal`, which guards the
arm that reports a 404 as a refusal only on an object the record maps, and
passes on the commit that holds the six checks, and strengthened the others to
read whole lines. `format`, `lint`,
`check`, `test` and `build` each pass on the change's tree, as the pull
request cites.

I made three choices the task leaves open. The scopes read
`one of the scopes <accepted>; the credential holds <own>`, and `none` where
the credential states no scope. With neither header the line reads
`needs a permission: GitHub named no permission and said "<message>"`, so
every refusal keeps the one shape. A `PATCH` to a mapped issue counts as a
call on an object the record maps, as the read of it does.

Review asked for GitHub's message on every refusal line, since a header can
name a scope the credential already holds while the real reason, such as an
archived repository, is in the message. I left it out, because criterion 1
and SPC-1080 fix the line as `refused: <method> <endpoint> needs <permission>`
and quote the message only where no header names a permission. Review also
asked whether a 401 should stop the run, since no later call can pass it.
After a 401 on the read or the update of a mapped issue, `project` goes on
to the remaining tasks. After a 401 on a create it creates nothing more, and
still reads back the issues it created. Both are as they were before this
task, and both questions need a change to the specification.

No run against GitHub was refused, so the three header names are as SPC-1080
states them and the stand-in sends them. `meow-github` goes to 0.9.0, and its
README shows the three lines under "When it can't read".

## Left alone

A refusal's place in the `partial:` line, which TSK-2960 owns. A refusal of a
write off the allow list, which the layer makes before `gh` starts and
TSK-2980 adds.
