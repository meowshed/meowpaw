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

## Evidence

`crates/meow/src/markdown.rs` gains `check`: it reads `[markdown] target`, the
`lint` verb's command and the tracked markdownlint files, and for each
`.markdownlint-cli2.*` beside a `.markdownlint.*` the file's `config` key. It
runs git alone and writes nothing. The `markdown` feature now takes
`yaml-rust2` to read a `.markdownlint-cli2.yaml`. `.meowpaw/profile.toml`
declares `[markdown] target = "github"`, and its `lint` verb runs
`plugins/meow-markdown/bin/meow-markdown check` second to last. It goes before
`mise run crate-lint`, not after it, because the checks for REQ-1186 in
`tools/test_verb_bindings.py` and `tools/test_shell_verbs.py` hold the crate's
lint as the verb's last command.
`meow-markdown` is 0.2.0, and its README and SPC-1195 say how `check` reads a
command and a `config` key.

The 14 checks failed first: `meow-verbs run test` exited 1, kept as
the run in #665, no longer kept, in the cover commit b9acb6f, which held
the checks alone. They pass now, unchanged, since
`git diff b9acb6f -- plugins/meow-markdown/tests/test_markdown.py` prints
nothing:

```text
$ python3 -m unittest discover -s plugins/meow-markdown/tests
Ran 27 tests
OK                                               # exit 0
$ plugins/meow-markdown/bin/meow-markdown check   # in this repository
meow-markdown check
no findings                                      # exit 0
```

Criterion 7's `lint` run is `meow-verbs run lint`, which now runs
`meow-markdown check`. `meow-verbs evidence --keep format lint check test
build` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites.

## Left alone

The link check's settings, which TSK-3120 adds to `check`. A tool run through
a runner's task, which `check` doesn't read, so here `check` holds the render
target and the markdownlint files alone, as ADR-1900 says.
