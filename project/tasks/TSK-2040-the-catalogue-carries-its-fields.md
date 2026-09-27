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

Not yet.

## Left alone

The descriptions' wording beyond the cost they now state.
