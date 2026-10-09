---
id: BUG-1520
artifact: bug
status: approved
severity: critical
violates: REQ-1485
enters: implement
found: 2026-10-09
revised: 2026-10-09
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The served marketplace keeps relative sources for every unit but one

The file at `https://meow.retran.me/meowpaw/marketplace.json` lists 15 of its
16 units with a relative `source` such as `./plugins/meow-flow`. Claude Code
reads the address as a `url` marketplace, whose cache holds that one file and
no `plugins/` directory, so it refuses each relative entry and no unit
installs or updates from the documented address.

## Reproduction

Seen with Claude Code 2.1.284 on macOS (arm64), against the file served on
2026-10-09, which is the `marketplace` release's asset uploaded on
2026-10-04T18:55:19Z by the run for the tag `meow-markdown-v0.6.1`.

1. Read the served entries:

   ```bash
   curl -fsS https://meow.retran.me/meowpaw/marketplace.json |
     jq -r '.plugins[] | [.name, (.source | if type == "string" then . else .source end)] | @tsv'
   ```

   Fifteen lines end in `./plugins/<name>`, and `meow-markdown` ends in
   `archive`.

2. Add the address as the documentation says, then update a unit:

   ```bash
   claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
   claude plugin update meow-flow@meowpaw
   ```

## What the system does

`claude plugin update meow-flow@meowpaw` exits non-zero with `Plugin source
path refused: ./plugins/meow-flow does not stay inside its marketplace
directory`. `claude plugin list` shows every installed unit but
`meow-markdown` as `failed to load` with the same message, and
`claude plugin marketplace update meowpaw` reports success while changing
nothing.

The cause is in `.github/workflows/claude-release.yml`. The packing step
starts from a copy of `.claude-plugin/marketplace.json` (line 74), whose
`source` values are all relative, and rewrites an entry to an archive only for
a unit it packs. A run started by a `<unit>-v<version>` tag sets `unit` and
skips every other name (line 78), so it rewrites one entry. The publish step
then replaces the release's `marketplace.json` with `--clobber` (line 123),
which discards the archive entries an earlier run had written. The last run
was for `meow-markdown`, so only that entry is an archive.

## What it should do, and why

REQ-1485 says one address serves every release, so that the platform's own
update brings a later release with nothing downloaded by hand. SPC-1080 states
that the released file's entries point at every unit's archive by `url` and
`sha256`. A file with a relative entry breaks both: the update has nothing to
fetch for that unit, and the person is left to download an archive by hand.

The form `claude plugin marketplace add meowshed/meowpaw` is no way round it.
It clones the repository, which carries no binaries, and BUG-1120 closed that
form as a defect against REQ-3178.

## Triage

Enters at `implement`, because REQ-1485 and SPC-1080 already say what the file
holds and the workflow doesn't produce it. Severity is critical: the only
documented install path fails for 15 of 16 units, existing installs can't
update, and the one working source is a form the project has already ruled a
defect.

Every single-unit tag run publishes a file like this one, so the fault
returns with each unit release until the workflow writes every entry from its
unit's release, whatever `unit` names. I haven't checked whether a run
without a tag publishes a complete file; that is the first thing the task
confirms.

This record doesn't touch ADR-1120, whose decision holds. It reopens REQ-1485,
which EPC-1090 closed.

## Closed by

Not yet. The fix is a task under this record, `bug: BUG-1520`. It lands with a
check that fails when a served `marketplace.json` carries a `source` that is a
string, so a single-unit run can't publish one again, and the reproduction's
first step then prints `archive` on every line.

## Tasks

- [ ] T-001 TSK-5240 publish a `marketplace.json` whose every entry is an archive, and check it before `Publish` in `.github/workflows/claude-release.yml`
