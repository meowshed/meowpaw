---
id: BUG-1323
artifact: bug
status: approved
severity: major
violates: REQ-2438
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 690
---

# The `links` fixtures pass against a `links` that breaks REQ-2438

The fixtures for `meow-markdown links` would go on passing if the program
reported a throttled link check as a finding, dropped `--format json`, or
misread lychee exiting 1, and the one fixture that runs the real lychee skips
under this repository's `test` verb. So nothing in the gate holds what
REQ-2438 asks of `links`, although EPC-1800 records the requirement as
verified.

## Reproduction

`main` after #713, with `meow-markdown` 0.4.3 built by `crates/meow/build-units`.

1. Run `grep -nE '429|408|401|410' plugins/meow-markdown/tests/test_markdown.py`.
2. Read `Links.links` in the same file: the stand-in lychee is
   `cat <file>; exit <status>`, whatever arguments it gets.
3. Run `plugins/meow-verbs/bin/meow-verbs run test` and read the Markdown
   suite's summary.

## What the system does

The `grep` matches nothing, so no fixture has a 429, a 408, a 401 or a 410,
and moving 429 from `unreachable` to `finding` in `error_class` in
`crates/meow/src/markdown.rs` passes every fixture. The stand-in ignores its
arguments, so `links` could drop `--format json` or `--no-progress` and pass.
No fixture has lychee exit 1, which ADR-1900 names as `tool broken`, and the
renamed-map case puts an unknown map and a missing map in one output, so
neither rule is shown alone. The `test` verb prints `OK (skipped=1)` for the
suite: `Links.test_criterion_5_the_real_lychee_reports_a_missing_file` skips,
because `lychee --version` fails with
`mise ERROR No version is set for shim: lychee` and nothing in the repository
declares lychee. I built four changed copies of `links` in one binary: 429
moved to `finding` and 410 to `unreachable`, `--no-progress` dropped, exit 1
accepted, and unknown maps allowed. The suite passed all but the fixture that
skips or fails for want of lychee, so it caught none of the four.

## What it should do, and why

Each class SPC-1195 states for `links` should have a fixture that fails when
`links` misclassifies it, and the real-lychee fixture should run under the
`test` verb, failing where lychee can't run, because a check that skips on
the machine that runs the gate holds nothing there. REQ-2438 is the
obligation, and its checks are what the record cites as its verification.

## Triage

It enters at cover, because REQ-2438, ADR-1900 and `links` are right, and the
checks TSK-3120 wrote miss cases the requirement asks for. Major, because the
record reports REQ-2438 as verified by checks that would pass the defect it
forbids, and nothing after them would notice.

## Closed by

Fixtures in the class `Links` in `plugins/meow-markdown/tests/test_markdown.py`:
the stand-in's arguments asserted, a 429, a 408 and a 401 as `unreachable` and
a 410 as a finding, lychee exiting 1 as `tool broken`, an unknown map and a
missing map each alone as `tool broken`, and the real-lychee fixture failing
where lychee can't run. The `test` verb runs the Markdown suite with lychee
0.24.2 on `PATH`.

## Tasks

- [ ] T-001 TSK-3170 hold every class `links` reports with a fixture, and run
      the real lychee in the `test` verb, in
      `plugins/meow-markdown/tests/test_markdown.py` and `.meowpaw/profile.toml`
