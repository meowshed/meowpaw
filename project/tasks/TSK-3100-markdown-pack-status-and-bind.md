---
id: TSK-3100
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1800
closes: [REQ-2352]
issue: 634
projected: da3a251668d2
---

# Ship the Markdown pack with detection, `status` and `bind`

`meow-markdown` ships as a unit, detects a Markdown corpus from what git
tracks, lists what the repository configured with `status`, and prints a
`[verbs]` table with `bind`, as SPC-1195 states. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a fixture repository with two tracked `*.md` files, one with a lone
   `README.md`, and one with a lone `README.md` and a `.markdownlint.yaml`,
   when `status` runs in each, then the first and third are detected and the
   second prints `unresolved: not a Markdown repository` and exits 3. Closed
   by: fixtures naming REQ-2352, seen failing first.
2. Given fixtures holding a `.markdownlint-cli2.yaml`, no linter
   configuration, a `.prettierrc`, a `lychee.toml`, a `mkdocs.yml`, and a
   profile that already declares `test`, when `bind` runs, then it prints
   `lint` bound to markdownlint-cli2 with `meow-markdown check` in a comment
   under it, `lint` as `meow-markdown check`, `format` bound to prettier,
   `check` as unresolved with its reason, `test` as `meow-markdown links`,
   `build` as unbound naming `mkdocs.yml`, and nothing for the declared
   `test`. Closed by: fixtures naming REQ-2352, seen failing first.
3. Given a fixture holding a `mise.toml`, when `bind` runs, then it names the
   file and points at the mise pack. Closed by: a fixture.
4. Given this repository, when `status` runs, then it lists
   `.markdownlint-cli2.yaml` as read by markdownlint-cli2 alone. Closed by: a
   fixture running `status` on a copy of that file.
5. Given any fixture above, when `status` and `bind` run, then `git status
--porcelain --ignored` reads the same before and after. Closed by: a
   fixture.

## What to do

Add a `markdown` feature to `crates/meow` and the unit under
`plugins/meow-markdown`, with its launcher, a skill file naming the program,
its README, budget, `requires.toml`, `plugin.json` at 0.1.0 and a
marketplace entry, built by `build-units` and tested by the `test` verb. The
program runs git alone, as `git ls-files` and `git check-ignore`, and writes
nothing. `check` and `links` may print a usage line until TSK-3110 and
TSK-3120 land. Add the unit to the documentation index.

## Depends on

Nothing. ADR-1900 is approved.

## Evidence

`crates/meow/src/markdown.rs` is the `markdown` feature: `status` and `bind`,
reading the tracked file list from `git ls-files` and the profile, and nothing
else. `build-units` builds it into `plugins/meow-markdown/bin/`, and the unit
ships its launcher, a skill naming the program, its README, budget,
`requires.toml` and `plugin.json` at 0.1.0, with a marketplace entry and a row
in the documentation index. `check` and `links` print the usage line and exit
2 until TSK-3110 and TSK-3120 land.

The 13 checks failed first: `meow-verbs run test` exited 1 with 19 failures
counting the subtests, kept as `project/evidence/389ccd22365c.txt`, in the
cover commit 593222a, which held the checks alone. They pass now, unchanged,
since `git diff 593222a -- plugins/meow-markdown/tests/test_markdown.py`
prints nothing:

```text
$ python3 -m unittest discover -s plugins/meow-markdown/tests
Ran 13 tests
OK                                               # exit 0
$ plugins/meow-markdown/bin/meow-markdown status  # in this repository
markdown files: 1874 tracked
markdownlint configuration, by directory:
  .markdownlint-cli2.yaml: read by markdownlint-cli2 alone
  plugins/.markdownlint.yaml: read by markdownlint-cli2 and markdownlint-cli
                                                 # exit 0
```

SPC-1195 didn't say whether `bind` exits 0 or 3 with its `# check:
unresolved` line. It exits 0, because ADR-1900 counts a verb printed with its
reason as settled, and SPC-1195 now says so. A missing profile is unresolved,
exit 3, for `status` and `bind` alike, as SPC-1195's failure paths state.
`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

`check`, which TSK-3110 and TSK-3120 take; `links`, which TSK-3120 takes; the
skill's body and `reviewing.md`, which TSK-3130 takes; this repository's
profile, which TSK-3110 changes. REQ-2424 and REQ-2484, which ADR-1900
postpones.
