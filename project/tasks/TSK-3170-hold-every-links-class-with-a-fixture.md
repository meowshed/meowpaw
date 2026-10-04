---
id: TSK-3170
artifact: task
status: done
revised: 2026-09-29
bug: BUG-1323
closes: []
issue: 690
---

# Hold every class `links` reports with a fixture, and run the real lychee in the `test` verb

The `links` fixtures fail when `links` passes lychee the wrong arguments or
misclassifies a 429, a 408, a 401, a 410, an exit status of 1 or a map, and
the fixture that runs the real lychee runs under this repository's `test`
verb. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a stand-in lychee that records its arguments, when `links` runs with
   no input and then with `README.md`, then the stand-in got
   `--format json --no-progress -- **/*.md` and then
   `--format json --no-progress -- README.md`. Closed by:
   `Links.test_criterion_2_links_passes_lychee_its_arguments`.
2. Given a stand-in printing a 429, a 408 and a 401, when `links` runs, then
   each prints as `unreachable` and it exits 3; given a 410, it prints as a
   finding and exits 1. Closed by:
   `Links.test_criterion_1_throttled_and_refused_responses_are_unreachable` and
   `Links.test_criterion_2_a_410_is_a_finding`.
3. Given a stand-in printing a clean report and exiting 1, one whose JSON
   carries an unknown map beside the
   six it knows, and one whose JSON lacks `timeout_map`, when `links` runs,
   then each prints `tool broken` and exits 3. Closed by:
   `Links.test_criterion_4_a_lychee_that_fails_or_prints_no_json_is_tool_broken`.
4. Given no lychee that runs, when the real-lychee fixture runs, then it fails
   naming lychee, and given the `test` verb, it runs against lychee 0.24.2 and
   passes. Closed by:
   `Links.test_criterion_5_the_real_lychee_reports_a_missing_file`, and the
   `test` verb's output with no test skipped in the Markdown suite.

## What to do

In `plugins/meow-markdown/tests/test_markdown.py`, have the stand-in lychee
write each argument it gets to a file, one to a line, and assert them. Add the
responses RES-0294 observed and the fixtures lack, and split the renamed-map
case into an unknown map and a missing map, each alone. Make the real-lychee
fixture fail, and not skip, where lychee doesn't run.

Run the Markdown suite in the `test` verb in `.meowpaw/profile.toml` under
`mise exec lychee@0.24.2 --`, because the fixture runs `links` in a scratch
repository, where a mise shim finds no version of lychee to run, and
`mise exec` puts the installed lychee itself on `PATH`. Write the checks
first, in a commit of their own, and see them fail.

## Depends on

BUG-1324, added while this task ran and fixed first in #724: until then
`check` read `lychee@0.24.2` in the `test` verb as a link check, and
`Adopted.test_criterion_7_check_passes_on_this_repository` failed. BUG-1323
is approved.

## Evidence

The stand-in lychee in `Links.links` writes each argument it gets to
`bin/lychee.args`, and
`Links.test_criterion_2_links_passes_lychee_its_arguments` asserts them. New
fixtures give a 429, a 408 and a 401 as `unreachable` and a 410 as a finding.
The `tool broken` fixture now has lychee exit 1 after printing a clean report,
so only its status can break the run, and puts an unknown map and a missing
`timeout_map` in separate cases. The real-lychee fixture fails where no lychee
runs, and the `test` verb runs the Markdown suite under
`mise exec lychee@0.24.2 --`.

I built one binary with four changed copies of `links`: 429 moved to
`finding` and 410 to `unreachable`, `--no-progress` dropped, exit 1 accepted,
and unknown maps allowed. The fixtures caught each one, and the unchanged
binary passes:

```text
$ mise exec lychee@0.24.2 -- python3 -m unittest test_markdown.Links   # four changes built in
Ran 12 tests
FAILED (failures=6)                     # exit 1; 429, 410, arguments x2, exit 1, unknown map
$ mise exec lychee@0.24.2 -- python3 -m unittest test_markdown         # unchanged binary
Ran 57 tests
OK                                      # exit 0
$ python3 -m unittest test_markdown.Links                              # no lychee on PATH
FAILED (failures=1)                     # exit 1; the real-lychee fixture
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`crates/meow/src/markdown.rs`, because `links` classifies each case right
today and only its checks were short. `mise.toml`, because a tool declared
there reaches a scratch repository only through a shim, which resolves no
version outside this repository, and the owner's checkout carries an
uncommitted change to that file. `meow-markdown`'s version, because its
shipped behaviour doesn't change.
