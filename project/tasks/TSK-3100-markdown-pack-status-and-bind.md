---
id: TSK-3100
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-1800
closes: [REQ-2352]
issue:
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

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

`check`, which TSK-3110 and TSK-3120 take; `links`, which TSK-3120 takes; the
skill's body and `reviewing.md`, which TSK-3130 takes; this repository's
profile, which TSK-3110 changes. REQ-2424 and REQ-2484, which ADR-1900
postpones.
