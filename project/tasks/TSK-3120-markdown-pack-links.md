---
id: TSK-3120
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1800
closes: [REQ-2438, REQ-2454]
issue: 636
projected: ce04cba83ec0
---

# Classify a link check with `links`, and check its declared settings

`meow-markdown links` runs lychee, classifies each result from its JSON as a
finding, unreachable, skipped, unresolved, absent or broken, and exits on
that, and `check` reports a link check that leaves `offline`, `max_retries` or
`cache` undeclared, as SPC-1195 states. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a stand-in lychee printing RES-0294's JSON with a timeout and a
   failed connection, and another with a 403 and a 503, when `links` runs,
   then each result prints as `unreachable` and `links` exits 3. Closed by:
   fixtures naming REQ-2438, seen failing first.
2. Given a stand-in printing a 404, and another printing a missing relative
   file, when `links` runs, then each prints as `finding` and `links` exits 1;
   given a mix of a 404 and a timeout, then it exits 1 with the unreachable
   address listed under its own heading. Closed by: fixtures naming REQ-2438.
3. Given a stand-in printing only excluded addresses, when `links` runs, then
   they print as `skipped`, with their count, and `links` exits 0. Closed by: a
   fixture.
4. Given no lychee on `PATH`, a stand-in exiting 3, one printing text that
   isn't JSON, and one printing RES-0294's JSON with `timeout_map` renamed,
   when `links` runs, then the first prints `tool absent` and the others
   `tool broken`, each exiting 3; given a stand-in whose JSON holds a rejected
   3xx response, then it prints `unresolved` and exits 3. Closed by: fixtures
   naming REQ-2438.
5. Given the real lychee and a fixture with a relative link to a missing file,
   when `links` runs, then it exits 1 with the finding. Closed by: a fixture
   that reports itself as skipped where lychee isn't installed, and a kept
   run of it with lychee 0.24.2 installed.
6. Given a `test` verb running `meow-markdown links` and a `lychee.toml`
   without `max_retries`, when `check` runs, then it exits 1 naming
   `max_retries`; given one declaring `offline`, `max_retries` and `cache`,
   then it exits 0; given a verb running `lychee --offline --max-retries 0
--cache=false` and no `lychee.toml`, then it exits 0. Closed by: fixtures
   naming REQ-2454, seen failing first.
7. Given a `lychee.toml` that doesn't parse as TOML, when `check` runs, then
   it exits 1 naming the file; given `cache = true` and no ignore file in the
   repository covering `.lycheecache`, then it exits 1 with that finding, and
   0 once `.gitignore` names it. Closed by: fixtures.

## What to do

Add `links` to the `markdown` feature and the link check's settings to
`check`. `links` runs `lychee --format json --no-progress` from the root,
passes inputs and no flag, and classifies from the JSON alone, never from
lychee's exit status. The stand-in fixtures carry RES-0294's recorded JSON.
Raise `meow-markdown`'s minor version, above the one TSK-3110 took where it
landed first.

## Depends on

TSK-3100, because the program and its detection come from it. It runs in
parallel with TSK-3110, and whichever merges second rebases onto the first,
since both add to `check`.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

Binding this repository's own link check, `tools/check_links.py`, to `links`,
because that check reaches no network and ADR-1900 changes nothing about it.
How `meow-verbs` reports a `test` verb whose command exits 3, which ADR-1900
leaves unsettled.
