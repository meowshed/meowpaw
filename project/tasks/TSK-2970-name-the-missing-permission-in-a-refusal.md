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

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

A refusal's place in the `partial:` line, which TSK-2960 owns. A refusal of a
write off the allow list, which the layer makes before `gh` starts and
TSK-2980 adds.
