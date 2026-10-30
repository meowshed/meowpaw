---
id: ADR-3080
artifact: adr
status: draft
revised: 2026-10-30
addresses: [REQ-5200]
supersedes: [ADR-3070]
concerns: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3080. The probe reads `meow-core`'s own `bin/` directory, not the caller's

## Decision

This supersedes ADR-3070, whose probe read the wrong directory. ADR-3070
checked the guarded unit's own `bin/` (`$here`) for any target at all, on
the premise that an archive-backed install ships every unit's own
`bin/<target>/paw` directly. It doesn't: downloading `meow-git-0.6.1.zip`
and `meow-flow-0.53.1.zip` and listing their contents shows each carries
only its own launcher script, `bin/meow-git` and `bin/paw`, with no target
directory at all — exactly what a `github`-source install also looks like.
Only `meow-core`'s own archive (`meow-core-0.10.2.zip`, also checked)
carries all six platform binaries. `$here` can't tell the two cases apart
for any unit except `meow-core` itself, because it looks the same either
way.

The launcher template probes, instead, the same directory `CLAUDE_FIND`
already resolves: `meow-core`'s own install, found through its `meow-root`
pointer under `$CLAUDE_PLUGIN_DATA`'s sibling data directory. Once that
block has run, if it found a `meow-root` (`$root` is non-empty) and that
directory's `bin/` carries no `<cpu>-<system>/` subdirectory for any
platform, the message names that cause and `meow.retran.me` in place of
`claude plugin install meow-core@meowpaw`. Where no `meow-root` was found
at all, `meow-core` simply isn't installed, and the existing message
already names the right remedy. Where `bin/` carries at least one platform
directory, even one that isn't this machine's, the message is unchanged.

Verified directly: a scratch `meow-git` launcher copied beside a scratch
`meow-core` whose `bin/` is a bare, empty directory, with a `meow-root`
pointer between them, denies with today's message as things stand; the
probe this decision adds is what changes that outcome, proven in
`tools/test_generate_launchers.py`'s `Denial` fixtures.

Once this is accepted, every guarded unit (`meow-git`, `meow-github`,
`meow-loop`, `meow-prose-gate`) and every advisory launcher reads the
`github`-source cause correctly, because all of them resolve through the
same `meow-core` install. What still doesn't work: a machine for which the
archive genuinely ships no binary (none exists today, but a future release
could drop a target) reads the generic message too, since its `bin/` would
carry other targets and not this one — the same case ADR-2710 already
left unreversed.

## Why

Every unit's own `bin/<target>/paw` check in the launcher (`binary="$here/
$cpu-$system/paw$exe"`) is there for a build placed directly beside a
checkout (`SPC-1080`'s local build), not for the archive-backed install;
the archive doesn't populate it for any unit but `meow-core`
(`EPC-2730`'s own acceptance criterion 3, confirmed again here by
downloading the archives). `meow-core`'s own directory is therefore the
one place an absent `bin/` and a `github`-source install are the same
fact, and it is already the directory every other unit's launcher reads
to find its binary in the first place.

## Alternatives

| Option                                                                        | Better at                                                           | Why it lost                                                                                                                                                                    |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Probe `meow-core`'s own `bin/`, via the `root` `CLAUDE_FIND` already resolves | Matches what every unit actually ships; verified directly           | Chosen                                                                                                                                                                         |
| ADR-3070's probe: the caller's own `bin/`                                     | None; every non-`meow-core` unit's `bin/` looks the same either way | Superseded: downloading `meow-git`'s and `meow-flow`'s own archives shows neither ships `bin/<target>/` at all                                                                 |
| Read `known_marketplaces.json` for the installed source                       | Names the declared source exactly, not an inference                 | Still undocumented for a launcher to read (ADR-3070 already weighed this)                                                                                                      |
| Have the person declare a flag or an environment variable at install time     | No probe at all, no risk of misreading the directory                | Nothing writes it; the `github` source and the archive-backed one both run `claude plugin install`, which can't be told apart after the fact without reading something on disk |

## What it costs

The same probe cost ADR-3070 already named, now spent reading the right
directory: one glob over `meow-core`'s own `bin/` once the resolution path
has already walked there for the binary itself, so no new file is opened
that `CLAUDE_FIND` hadn't already opened. `meow-core` not being installed
at all, and `meow-core` being a `github`-source install with no release
binaries yet, read identically (no `meow-root`'s target at all is treated
the same under either probe reading, if the `meow-root` file itself exists
but points at a directory later removed) — a rare case this decision
leaves exactly as unreversed as ADR-2710 does.

## What would reverse it

- The platform itself reports, on an install, that the chosen source ships
  no binary for a unit that needs one, as ADR-3060 and ADR-3070 both
  already named.

## Consequences

`tools/launchers.toml` and `tools/generate_launchers.py` carry this probe,
reading `$root` after `CLAUDE_FIND`, in place of ADR-3070's. Every
`claude`-host launcher that denies with the install command (`meow-git`,
`meow-github`, `meow-loop`, `meow-prose-gate`, `meow-flow`'s
`SessionStart` print, and `meow-checks revision`) is rewritten to read the
branch-appropriate command from a `fix` variable the same probe sets,
because a fixed `claude plugin install meow-core@meowpaw` string hardcoded
beside the message would read wrong on the new branch. `meow-author`,
`meow-checks status`, `meow-licence`, `meow-scm` and the twelve
`STANDARD_TAIL` units need no further change beyond the shared `reason`
text, since none of them appends a command of its own.

## How I will know it was realised

1. A launcher denies naming the `github`-source cause and `meow.retran.me`
   where `meow-core`'s own resolved `bin/` carries no platform directory at
   all (REQ-5200), proven by `tools/test_generate_launchers.py`'s
   `Denial.test_meow_core_with_no_target_at_all_names_the_github_cause_and_the_address`.
2. The same launcher denies naming `claude plugin install
meow-core@meowpaw`, unchanged, where `meow-core`'s `bin/` carries
   another platform's directory and none of this machine's, or where no
   `meow-core` install is found at all, proven by the same file's other two
   `Denial` cases.

## What this does not settle

- Everything ADR-3060 and ADR-3070 already left unsettled.
