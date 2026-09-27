---
id: TSK-2040
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-3160, REQ-3162, REQ-3164]
issue: 415
projected: eee63b13e83d
---

# Every served catalogue entry carries the fields a reader sees before an install

Each unit's `plugin.json` carries the five catalogue fields, its homepage
points at the unit's own page and its description names what the unit costs,
and the release copies the fields into each served entry. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given the tree, when `python3 tools/check_docs.py` runs, then it exits 0.
   Given a copy where one `plugin.json` lacks `license`, where one `homepage`
   points at `docs/`, or where one description doesn't name the unit's ceiling
   from `budget.toml`, then it exits 1 and names the unit. Closed by: fixtures
   naming REQ-3160, REQ-3162 and REQ-3164, seen failing first.
2. Given the committed `.claude-plugin/marketplace.json`, when the release
   workflow's step that completes the entries runs over it, then every entry
   carries `description`, `homepage`, `repository`, `license` and `keywords`,
   equal to its unit's `plugin.json`. Closed by: running that step locally and
   the `jq` output.

## What to do

Complete each unit's `plugin.json`, point its `homepage` at
`plugins/<unit>/README.md` on the default branch, and end each description
with the unit's ceiling from `budget.toml`, in characters of context on every
turn. Point the committed catalogue's `homepage` fields at the same pages.
Make the release workflow copy `description`, `repository`, `license` and
`keywords` from `plugin.json` into each served entry, where it already
replaces the source. Extend `tools/check_docs.py` with the catalogue checks
SPC-1110 lists.

Each description changes, so each unit's version moves by a patch, and its
pages are restamped under TSK-2030's check.

## Depends on

TSK-2030, because the homepage points at the page it moves and the check it
extends is the one it writes.

## Evidence

Every unit's `plugin.json` carried the five catalogue fields already, and each
description now names the unit's ceiling from `budget.toml`: up to 4,200
characters for `meow-core`, 700 for `meow-prose`, 500 for `meow-method`, 450
for `meow-verbs` and 380 for `meow-scm`, and nothing in context for
`meow-git`, `meow-github` and `meow-prose-gate`. Each unit moved by a patch
for its new description, and every page describing it is restamped.

`tools/check_docs.py` checks the catalogue fields, and three new fixtures,
naming REQ-3160, REQ-3162 and REQ-3164, failed against the check as TSK-2030
left it and pass against this one:

```text
$ CHECK_DOCS=check_docs_before.py python3 -m unittest tools/test_check_docs.py
FAIL: test_a_description_without_the_ceiling_fails
FAIL: test_a_homepage_outside_the_unit_fails
FAIL: test_a_manifest_without_its_licence_fails
FAILED (failures=3)
$ python3 -m unittest tools/test_check_docs.py
Ran 12 tests
OK
```

The release workflow copies `description`, `repository`, `license` and
`keywords` from each unit's `plugin.json` into its served entry. Its `jq`
step, run locally over the committed catalogue, left every entry with all five
fields and a homepage at `plugins/<unit>/README.md`. The workflow parses as
YAML; `actionlint` isn't installed here, so it wasn't linted.

## Left alone

The descriptions' wording beyond the cost they now state.
