---
id: TSK-4400
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2340
closes: [REQ-2996, REQ-3002]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Refuse a changed unit at a released version, and a version with no written notes

The release exits 1 before it packs anything where a unit's tracked files
changed since its last release tag while its version still equals that
tag's, or where a new version has no section in the unit's `CHANGELOG.md`,
and it publishes each unit's notes from that section, as SPC-1080 states. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository where `plugins/x/` changed after the tag
   `x-v0.1.0` and `x`'s version is still `0.1.0`, when
   `python3 tools/check_release.py` runs on it, then it exits 1 naming `x`
   (REQ-2996). Closed by: a test in `tools/test_check_release.py` naming
   REQ-2996, seen failing first.
2. Given the same fixture with `x` unchanged since its tag, when the check
   runs, then it exits 0. Closed by: a test naming REQ-2996.
3. Given a unit at a version with no release yet and no `## 0.2.0` section in
   its `CHANGELOG.md`, when the check runs, then it exits 1 naming the unit
   and the version (REQ-3002). Closed by: a test naming REQ-3002.
4. Given `.github/workflows/release.yml`, when a test reads it, then each
   unit's release takes its notes from its changelog section and the
   workflow passes no option that generates notes from commits (REQ-3002).
   Closed by: a test naming REQ-3002.

## What to do

Extend `tools/check_release.py`, which the release already runs before
packing, with both refusals. A commit belongs to a unit as the check already
decides under ADR-1570. Add a `CHANGELOG.md` to each unit with a section for
its current version, written for the person whose repository changes and
held to the writing standard's `changelog` type, and make the workflow read
each new version's section. I chose the per-unit changelog as where the
written notes live, because ADR-2480 asks for written notes and names no
file.

Keep the archive table the workflow writes today, below the written notes,
because it carries the sizes and SHA-256 a person checks.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

The rule on breaking changes the check already holds (REQ-3192), and the
marketplace release's notes, which name the address and no unit's changes.
