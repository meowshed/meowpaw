---
id: ADR-3070
artifact: adr
status: superseded
revised: 2026-10-30
addresses: [REQ-5200]
supersedes: [ADR-3060]
concerns: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3070. The probe reads the caller's own `bin/` directory for any target at all

## Decision

This supersedes ADR-3060, whose probe was backwards: it fired only where
`bin/` carried at least one other target but not this machine's, which is
the archive-backed install's own unsupported-machine case, already covered
by today's message. `BUG-1690`'s reproduction shows the opposite: a
`github`-source install's `bin/` carries no target at all, every
`<cpu>-<system>/` subdirectory gitignored out of the tree it clones.

The launcher template probes, before it names `claude plugin install
meow-core@meowpaw`, whether its own `bin/` directory (`$here`, where the
launcher script itself lives) holds no `<cpu>-<system>/` subdirectory for
any platform. Where none exists, the message names that cause — this
install carries no binary the archive would have shipped — and the
archive-backed marketplace's address, `meow.retran.me`. Where at least one
target directory exists, even one that isn't this machine's, the message
stays exactly as it runs on the trunk today.

Once this is accepted, a `github`-source install denies naming the actual
cause and the working address on its first guarded call. What still
doesn't work: a machine whose target the archive-backed release doesn't
build still reads the generic message, because REQ-5200 asks only that the
message tell the two causes apart, and ADR-2710 already names that case as
unreversed.

## Why

`$here` is the directory the launcher script's own copy sits in, and every
unit's release archive packs that unit's own `bin/<target>/paw` directly
beside it (`claude-release.yml`'s `zip`, built from the targets `rust-tool`
produced). A `github`-source install clones the tree with
`plugins/*/bin/*-*-*/` excluded by `.gitignore`, so `$here` holds the
launcher script and nothing else: no target directory for any platform, not
even one. A local build beside the checkout (`SPC-1080`) writes exactly one
target under `bin/`, so it is never mistaken for the `github`-source case
either. Reading `$here` needs no new state and no new file: every launcher
already resolves from `$here` first, before it falls back to the shared
binary `CLAUDE_FIND` locates.

## Alternatives

| Option                                                                   | Better at                                           | Why it lost                                                                                                                                                               |
| ------------------------------------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Probe `$here` for any `<cpu>-<system>/` directory                        | Matches the actual symptom, no new state            | Chosen                                                                                                                                                                    |
| ADR-3060's probe: require `bin/` to name another target but not this one | None; it never matches the `github`-source install  | Superseded: `bin/` is absent, not partially populated, so the condition is never true                                                                                     |
| Read `known_marketplaces.json` for the installed source                  | Names the declared source exactly, not an inference | Its path and schema aren't documented for a launcher to read (REQ-4510); a future platform release can move or rename it with no notice                                   |
| Probe meow-core's shared `bin/` (via its `meow-root` pointer) instead    | Checks the binary provider other units borrow from  | A unit whose own archive carries its own `bin/<target>/paw` (every unit does) never reaches that fallback, so the probe would read the wrong directory for most launchers |

## What it costs

The same as ADR-3060 costed: one more directory read on the already-slow
denial path, and a probe that can't tell a `github`-source install from a
local checkout with no build run yet, which reads the same on disk — both
get the new message, and both are in fact missing every binary the archive
would have shipped, so the message is accurate for either.

## What would reverse it

- The platform itself reports, on an install, that the chosen source ships
  no binary for a unit that needs one, as ADR-3060 already named.

## Consequences

`tools/launchers.toml` and `tools/generate_launchers.py` carry this probe in
place of ADR-3060's, and `tools/test_generate_launchers.py` carries a
fixture with an empty `bin/` beside the launcher, alongside one with another
target present and none for this machine.

## How I will know it was realised

1. A launcher run from `$here` with no `<cpu>-<system>/` subdirectory at all
   denies naming the cause and `meow.retran.me` (REQ-5200).
2. A launcher run from `$here` with another target's directory present and
   none for this machine denies naming `claude plugin install
meow-core@meowpaw`, unchanged from the trunk today.

## What this does not settle

- Everything ADR-3060 already left unsettled.
