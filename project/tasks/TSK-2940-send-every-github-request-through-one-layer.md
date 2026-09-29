---
id: TSK-2940
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1720
closes: [REQ-2566, REQ-2578]
issue: 705
projected: 830811b8caac
---

# Send every GitHub request through one layer that reads its limits and stops at a stated wait

`meow-github` sends every call to GitHub through one request layer, which
reads the limit headers on every response, tells a cached replay from a fresh
response, turns a header into a wait through one table, and stops the run at
a throttle unless `--wait` asks it to sleep. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a stand-in `gh` answering a create with 403 and `retry-after: 30`,
   when `project` runs, then it prints `throttled`, the method and endpoint,
   and the UTC time 30 seconds after the response, exits 3 and sends no
   further call. Closed by: `Throttle.test_a_stated_wait_stops_the_run` in
   `plugins/meow-github/tests/test_github.py`.
2. Given the same stand-in and an injected clock, when `project --wait` runs,
   then the stand-in records the resent call no earlier than 30 seconds after
   the refused one. Closed by:
   `Throttle.test_wait_resends_no_earlier_than_the_stated_time` in
   `plugins/meow-github/tests/test_github.py`.
3. Given a first throttle of 3,540 seconds and a second of 120 seconds, when
   `project --wait` runs, then it sleeps the first, starts no second sleep,
   prints `throttled` and exits 3. Closed by:
   `Throttle.test_wait_stops_once_the_waits_would_pass_an_hour` in
   `plugins/meow-github/tests/test_github.py`.
4. Given `x-ratelimit-reset: 1790695444` and a `Date` of 1790692237, when the
   layer derives the wait, then it is 3,207 seconds, and reading the value as
   milliseconds would give about 3.2 seconds or a date in 1970. Closed by: the
   unit test `reset_is_read_in_epoch_seconds` in
   `crates/meow/src/github/request.rs`.
5. Given a throttle whose `retry-after` isn't a number of seconds, when the
   run meets it, then it reports the wait as unknown, sends no further call
   and exits 3. Closed by:
   `Throttle.test_an_unparsed_wait_is_unknown_and_stops_the_run` in
   `plugins/meow-github/tests/test_github.py`.
6. Given a response carrying no rate-limit header, when the run reads it, then
   it records the response as carrying none and goes on. Closed by:
   `Limits.test_a_response_with_no_limit_header_lets_the_run_go_on` in
   `plugins/meow-github/tests/test_github.py`.
7. Given a cached response whose `Date` is ten minutes old, when the run reads
   it, then it isn't counted as a request and its `remaining` isn't reported
   as current. Given the injected local clock two minutes ahead of the
   stand-in's `Date`, a fresh cached response is counted and its `remaining`
   reported as current, and the run's first call carries no `--cache`. Closed
   by: `Limits.test_a_stale_replay_is_not_read_as_current` and
   `Limits.test_a_skewed_clock_leaves_a_fresh_response_current` in
   `plugins/meow-github/tests/test_github.py`.
8. Given the crate, when a test reads its source, then only
   `crates/meow/src/github/request.rs` starts `gh` in the `github` feature.
   Closed by: the unit test `only_the_layer_starts_gh` in
   `crates/meow/src/github/request.rs`.

## What to do

Add `crates/meow/src/github/request.rs`, remove `gh()` from
`crates/meow/src/github.rs`, and move `history`, `project` and naming the
repository onto the layer, as SPC-1080's section "The GitHub request layer"
states. The layer runs `gh api --include` and parses the status line, the
headers and the body. `history` follows each listing's `Link` header one page
a call, keeping `--cache 1h` on every call but the run's first, because
`--include` with `--slurp` prints text that isn't JSON (RES-0290). Naming the
repository reads `repos/{owner}/{repo}` where it ran `gh repo view`.

Keep the replay test, the wait table and the throttle rules exactly as
ADR-1810 states them: the 60-second test measured on GitHub's clock through
the offset, one table keyed by service, 60 seconds doubled for each further
secondary throttle, exit 3 at a stop, and a total of an hour of waits. Every
conversion from a header to a duration goes through the table.

Make the stand-in `gh` in `plugins/meow-github/tests/test_github.py` print a
header block under `--include`, and let the fixtures inject the clock and the
sleep, so no test waits in real time. A shipped run uses the system clock.
The existing `History` and `Project` fixtures keep passing against the new
stand-in.

Add `--wait` to `history` and `project`, raise `meow-github`'s minor version
in `plugins/meow-github/.claude-plugin/plugin.json`, and match its README's
`describes:`. The README's section "When it can't read" names the `throttled`
line and `--wait`.

## Depends on

Nothing.

## Cover

- Checks: plugins/meow-github/tests/test_github.py, crates/meow/src/github/request.rs
- Failing run: project/evidence/5c33f71ed1dc.txt project/evidence/97bd1ebb8bc1.txt
- Landed in: not yet
- Judgement: 7: whether a replay is counted as a request is printed only once TSK-2950 adds the budget lines, so until then the checks read the replay test through whether a `remaining` of 0 holds the next call

The checks, each naming its criterion and requirement in its docstring or
doc comment: `Throttle.test_a_stated_wait_stops_the_run` for criterion 1,
`Throttle.test_wait_resends_no_earlier_than_the_stated_time` for criterion 2,
`Throttle.test_wait_stops_once_the_waits_would_pass_an_hour` for criterion 3,
`Throttle.test_an_unparsed_wait_is_unknown_and_stops_the_run` for criterion
5, `Limits.test_a_response_with_no_limit_header_lets_the_run_go_on` for
criterion 6, and `Limits.test_a_stale_replay_is_not_read_as_current` and
`Limits.test_a_skewed_clock_leaves_a_fresh_response_current` for criterion 7,
in `plugins/meow-github/tests/test_github.py`; `reset_is_read_in_epoch_seconds`
for criterion 4 and `only_the_layer_starts_gh` for criterion 8, in
`crates/meow/src/github/request.rs`.

The test verb stops at the crate's first failure, so two kept runs cover the
checks. `5c33f71ed1dc` fails both crate tests at this tree. `97bd1ebb8bc1`
fails all seven fixtures, eight failures counting both of criterion 5's
subtests, on a tree that differs from this one only by the line in
`crates/meow/src/github.rs` declaring the `request` module.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The budgets, the credential's form, the read-back listing, the refusal
reports and the allow list, which TSK-2950, TSK-2960, TSK-2970 and TSK-2980
add on top of the layer. `project` still reads each created issue back one at
a time until TSK-2960 replaces that with one listing. The rest of the README
and `docs/` wait for the document step.
