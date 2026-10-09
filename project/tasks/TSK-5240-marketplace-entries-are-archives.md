---
id: TSK-5240
artifact: task
status: draft
revised: 2026-10-09
bug: BUG-1520
closes: [REQ-1485]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Publish a marketplace file whose every entry is an archive

The release workflow publishes a `marketplace.json` in which every unit's
`source` is an archive, whichever unit's tag started the run, and a check
fails the run before it publishes a file that holds a relative `source`.
Without that, the served file keeps the relative entries BUG-1520 records and
the platform refuses each of them.

## Acceptance criteria

1. Given a `<unit>-v<version>` tag run for one unit whose version has no
   release, when the workflow builds `dist/marketplace.json`, then every entry
   of the file has a `source` object with `source: archive`, a `url` and a
   `sha256`. Closed by: a unit test in `tools/test_marketplace.py` that runs
   the packing logic over a fixture of three units and one tag.
2. Given a `marketplace.json` with one entry whose `source` is a string, when
   the check runs on it, then it exits 1 and names that entry. Closed by: a
   test in `tools/test_marketplace.py` that passes a fixture with one relative
   entry and asserts the exit status and the unit's name.
3. Given the workflow run without a tag and without `publish`, when it packs,
   then the file it leaves as a workflow artifact passes the same check.
   Closed by: the workflow run's job summary on the pull request, which names
   the check's result.
4. Given the first publishing run after this change, when the address
   `https://meow.retran.me/meowpaw/marketplace.json` has been deployed, then
   `curl` of it lists no `source` that is a string. Closed by: the command in
   BUG-1520's reproduction, run once and its output recorded under Evidence.

## What to do

Write every entry of the published file from the archive of its unit's
current version, and not only the entry of the unit the run packs. A unit
whose version already has a release keeps its archive, as SPC-1080 says, so
for the units the run skips, take the `url` and `sha256` from that release and
never from `.claude-plugin/marketplace.json`. Make the same check run in the
workflow before `Publish`, so that a file with a relative entry never
replaces the release asset.

First confirm whether a run without a tag publishes a complete file, because
BUG-1520 records that as unchecked, and keep that run's behaviour if it does.

The file of the repository, `.claude-plugin/marketplace.json`, keeps its
relative paths for development (SPC-1080), so the check applies to the
released file only.

Criterion 4 is the evidence that closes REQ-1485: once the served file lists
only archives, `claude plugin marketplace update meowpaw` has something to
fetch for every unit.

## Depends on

Nothing.

## Evidence

Not yet. Criterion 4 rests on a publishing run, which only the owner starts,
because publishing is a public act; the task isn't done until that run has
happened and its output is recorded here.

## Left alone

The install text in `README.md`, `docs/` and each unit's README, because it
already follows ADR-1120 and the defect is in what the address serves. The
`MARKETPLACE_DISPATCH_TOKEN` step and the Pages site of `retran/meow.retran.me`
stay as they are, because the file they deploy is the only thing wrong.
