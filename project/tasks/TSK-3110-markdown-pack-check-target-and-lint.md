---
id: TSK-3110
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1800
closes: [REQ-2434, REQ-2452]
issue: 635
projected: e106e2645c17
---

# Check the render target and the markdownlint settings, and adopt the check here

`meow-markdown check` reports a missing render target and each markdownlint
configuration the `lint` verb ignores, lacks or overrides in silence, as
SPC-1195 states, and this repository declares `[markdown] target = "github"`
and runs the check in its `lint` verb. One task, one branch, one pull request,
one review.

## Acceptance criteria

1. Given a profile with no `[markdown] target`, when `check` runs, then it
   exits 1 naming the missing target; given one declaring `github`, and one
   declaring `forgejo`, then it exits 0. Closed by: fixtures naming REQ-2452,
   seen failing first.
2. Given a `lint` verb running markdownlint-cli2 with no configuration file,
   when `check` runs, then it exits 1 with the defaults finding. Closed by: a
   fixture naming REQ-2434, seen failing first.
3. Given a `lint` verb running `markdownlint` beside a tracked
   `.markdownlint-cli2.jsonc`, when `check` runs, then it exits 1 naming that
   file. Closed by: a fixture naming REQ-2434, seen failing first.
4. Given one directory holding a `.markdownlint.jsonc` and a
   `.markdownlint-cli2.yaml` whose `config` sets a rule, when `check` runs,
   whatever the `lint` verb runs, then it exits 1 naming both files and that
   markdownlint-cli2 applies the `.markdownlint.jsonc`. Closed by: a fixture
   naming REQ-2434, seen failing first.
5. Given a missing profile, or one that doesn't parse, when `check` runs, then
   it prints unresolved and exits 3. Closed by: fixtures.
6. Given any fixture above, when `check` runs, then `git status --porcelain
--ignored` reads the same before and after. Closed by: a fixture.
7. Given this repository after the change, when the `lint` verb runs, then it
   runs `meow-markdown check` and passes. Closed by: `meow-verbs run lint`,
   exit status 0, kept as evidence.

## What to do

Add `check` to the `markdown` feature. It reads the profile's `[verbs]` and
`[markdown]`, the tracked markdownlint files and, for the `config` key of a
`.markdownlint-cli2.*` file, that file's contents; it runs git alone and
writes nothing. In this repository, add `[markdown] target = "github"` to
`.meowpaw/profile.toml` and append `meow-markdown check` to the `lint` verb,
naming the program by its path so a job without the unit's `bin/` on `PATH`
still runs it. Raise `meow-markdown`'s minor version.

## Depends on

TSK-3100, because the program, its detection and its profile reading come
from it.

## Cover

- Checks: `plugins/meow-markdown/tests/test_markdown.py`, classes
  `RenderTarget` (criterion 1), `MarkdownlintSettings` (criteria 2 to 4),
  `CheckUnresolved` (criterion 5), `CheckTree` (criterion 6) and `Adopted`
  (criterion 7), each test named `test_criterion_N_...`
- Failing run: `project/evidence/d8c083022377.txt`
- Landed in: not yet
- Judgement: none. Criterion 7's `lint` run is shown by the kept `lint`
  evidence at implementation, because a check inside `test` that ran the whole
  `lint` verb would run the gate within the gate

## Evidence

Not yet.

## Left alone

The link check's settings, which TSK-3120 adds to `check`. A tool run through
a runner's task, which `check` doesn't read, so here `check` holds the render
target and the markdownlint files alone, as ADR-1900 says.
