---
id: RES-0354
artifact: research
status: approved
revised: 2026-10-11
elaborates: RES-0001
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Where the harness spends time and duplicates itself, measured on its own trunk

## Summary

The harness's gate is seconds-scale and fast enough; the session is where the
time goes, and the trees carry hand-maintained duplication the record never
checks. This document measures both, from the trunk at `6536d751`, and records
three defects the measurement surfaced: the trunk's own record check is red,
a unit's test suite fails on the trunk, and the record's readiness and status
answers disagree.

## The question

The owner asked for a critical review of the harness, both distributions,
asking what can be improved and whether it can be faster. What constrains
it: the budget and the measurement suite went in the two changes before this
one, so what is slow or duplicated now is not what those removed, and every
finding below names where it was measured.

## Method

Timed each task of `mise.toml` and its underlying command on this machine,
an Apple-silicon laptop, from the trunk at `6536d751`, cold where caching
would hide the cost. Counted the hooks every unit ships and read their
matchers from `hooks/hooks.json`. Compared each unit's plugin page with its
package page, and each launcher and Pi extension with its siblings, by line
counts and by `diff`. Ran `plugins/meow-flow`'s test suite in an
`origin/main` worktree to tell a defect from a local change.

## Findings

- **The gate is seconds-scale.** `mise run all` completes in under four
  seconds where it fails on the pre-existing finding; prettier over 2,334
  files takes 6.8 seconds, markdownlint 2.8, the test stage 5 to 25 depending
  on cache state, the crate's release build 3.4 cold, and every other task
  under a second.
- **The session is where the time goes, and one hook dominates.** The prose
  gate asks a judge model twice on every command matched, 14 matchers in
  `plugins/meow-prose-gate/hooks/hooks.json`, with a 120-second hook timeout.
  Two matchers are over-broad: `git -C *` and `gh -R *` fire on reads, so a
  command publishing no text, such as `git -C /tmp/x log`, pays for two
  model calls.
- **`paw` rereads the whole record on every call.** `paw status` takes 1.0
  second and `paw check` 2.9 over 2,155 artifacts, and `paw status
--waiting` runs on every session start. The record already keeps generated
  indexes; a parsed cache keyed by the tree would make a warm call cheap and
  does not exist.
- **Every guarded tool call re-probes the machine.** Each launcher probes
  `uname` twice and walks the core unit's data directory on every
  invocation, and Claude Code runs three native guards on every Bash, Edit
  or Write call. Each costs tens of milliseconds; the work is the same on
  every call and its result is never stored.
- **Nothing holds a unit's four descriptions together.** Each unit's
  description exists in `plugins/<unit>/README.md`,
  `plugins/<unit>/.claude-plugin/plugin.json`, `packages/<unit>/README.md`
  and `packages/<unit>/package.json`, all hand-edited, and no check compares
  them. Two changes in this session edited the same paragraph in all four
  places, by hand, twice.
- **Fifteen launchers and fifteen Pi extensions are one script each.** The
  launchers differ by name and the extensions by command list; 974 lines of
  extension code and a like number of launcher lines are fifteen copies of
  one template, and `build-units` already generates what they dispatch to.
- **The package pages mirror their plugin pages by hand.** Sixteen package
  pages share about ten lines with the unit page they mirror, and nothing
  checks the mirror.
- **Three defects.** The trunk's `paw check` exits 1, because the Pi
  packages' specification rests on a requirement a later decision withdrew
  through an approved defect's citation, so `mise run test-record` fails on
  `main` and every verification records stale. `plugins/meow-flow`'s suite
  carries a failing test on `origin/main`,
  `test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported`,
  asserting status wording the program no longer prints. And `paw ready
implement` answers "approved and complete" from a task's Evidence while
  `paw status` derives in-progress from its epic's marks, two answers to one
  question, which REQ-0585 says must agree.

## Conclusions

1. The trunk's record check passes, so a verification run binds its results
   to the tree it ran on.
2. A judged rule is asked only where the command publishes text.
3. A warm `paw` invocation completes within a second, from a parsed cache
   keyed by the tree.
4. A unit's launcher resolves its binary once and reuses the resolution.
5. A unit's description agrees across its plugin manifest, its plugin page,
   its package manifest and its package page, held by a check.
6. A unit's launcher and Pi extension are generated from one template by the
   unit's program, not hand-written per unit.
7. A package's page mirrors its unit's page, held by the same check as the
   description.
8. The three defects are recorded, each as its own defect record, and the
   readiness answer derives from what `paw status` derives from.

## Sources

- `mise.toml` at `6536d751`, timed 2026-10-11 - the gate's cost, task by task.
- `plugins/meow-prose-gate/hooks/hooks.json` at `6536d751`, read 2026-10-11 - the 14 matchers and the over-broad two.
- `plugins/meow-flow/bin/paw`, `crates/meow/src/record.rs` at `6536d751`, read 2026-10-11 - the record reread per call.
- `plugins/*/bin/*` and `packages/*/extensions/*.ts` at `6536d751`, compared 2026-10-11 - the fifteen near-identical launchers and extensions.
- `plugins/*/README.md` against `packages/*/README.md` at `6536d751`, compared 2026-10-11 - the hand-maintained mirrors.
- `mise run test-record` on `main`, `plugins/meow-flow`'s suite in an `origin/main` worktree, 2026-10-11 - the three defects.
