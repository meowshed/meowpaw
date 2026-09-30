---
id: TSK-2950
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1720
closes: [REQ-2568, REQ-2582]
issue: 706
projected: 4bac05d3ef46
---

# Keep the four budgets, space the writes, and name the credential's form

The request layer counts primary requests, secondary points and content
creation, sends writes a second apart, and stops a run before a request that
would pass a ceiling. Every run names the form of authentication `gh` used and
prints its budgets. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given 501 unmapped tasks and a stand-in `gh` that creates every issue, when
   `project` runs with an injected clock, then the stand-in records 500
   creates, the run stops before the 501st naming content creation at 500 of
   500 this hour, and exits 3. Closed by:
   `Budgets.test_content_creation_stops_the_run_at_500_an_hour` in
   `plugins/meow-github/tests/test_github.py`.
2. Given the same run, when the stand-in's timestamps are read, then every
   write is at least one second after the previous one. Closed by:
   `Budgets.test_writes_are_a_second_apart` in
   `plugins/meow-github/tests/test_github.py`.
3. Given `x-ratelimit-limit: 1000` and `GITHUB_ACTIONS=true`, when `project`
   finishes, then the last lines of its report name primary requests with
   1,000 as the limit, secondary points, content creation and spacing. Closed
   by: `Budgets.test_the_budget_lines_name_the_four_counts` in
   `plugins/meow-github/tests/test_github.py`.
4. Given `GH_TOKEN` set, then only `GITHUB_TOKEN` set, then neither, when
   `project` runs, then its first line names `GH_TOKEN from the environment`,
   `GITHUB_TOKEN from the environment` and `gh's stored credential` in turn,
   and `GITHUB_ACTIONS=true` adds `, inside a GitHub Actions workflow`. Closed
   by: `Credential.test_the_first_line_names_the_form` in
   `plugins/meow-github/tests/test_github.py`.
5. Given a sentinel token value in `GH_TOKEN` or `GITHUB_TOKEN`, when
   `project` or `history` runs, then the value appears nowhere in standard
   output or standard error. Closed by:
   `Credential.test_the_token_value_is_never_printed` in
   `plugins/meow-github/tests/test_github.py`.
6. Given a run of `history`, when its document is parsed, then it carries
   `credential` with the form and `budget` with the budget lines, and every
   field onboarding reads is unchanged. Closed by:
   `History.test_the_document_names_the_credential_and_the_budget` in
   `plugins/meow-github/tests/test_github.py`.

## What to do

Add the four counts to the layer TSK-2940 added, as SPC-1080's section "The
GitHub request layer" states: primary requests, and per
`x-ratelimit-resource` the limit, remaining and reset the last fresh response
stated; secondary points, 1 for a `GET` and 5 for any other method over the
last minute against 900; content creation, every `POST`, over the last minute
against 80 and over the last hour against 500; and spacing, one write at a
time, each at least a second after the previous one. Check the counts before
each request, and stop at a ceiling as at a throttle, naming the count and
when it frees. Read the limit from `x-ratelimit-limit` and never assume it
from the credential's form.

Name the credential's form from whether `GH_TOKEN` and `GITHUB_TOKEN` are set,
in that order, and from `GITHUB_ACTIONS`, reading no variable's value, because
the value is secret material. Add `credential` and `budget` to `history`'s
document.

Raise `meow-github`'s minor version above the one `main` carries when this
lands, and match its README's `describes:`. The README names the credential
line and the budget lines.

## Depends on

- TSK-2940 (blocking): the counts and the credential's form sit in the layer
  it adds.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The read-back listing and `partial:`, which TSK-2960 adds, and the refusal
reports, which TSK-2970 adds. Budgets another run or a person spends on the
same account, which ADR-1810 leaves to GitHub's throttle. The hand path's
spacing in the README, which the document step writes.
