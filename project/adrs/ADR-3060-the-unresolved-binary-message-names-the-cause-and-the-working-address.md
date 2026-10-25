---
id: ADR-3060
artifact: adr
status: approved
revised: 2026-10-25
addresses: [REQ-5200]
supersedes: []
concerns: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3060. The unresolved-binary message names the install's own cause before it names a remedy

## Decision

The launcher template probes, before it prints the unresolved-binary line,
whether its own directory sits under a marketplace installed with source
`github`: a sibling `.claude-plugin/` with no `bin/<target>/` beside it,
where `bin/` names at least one other target the release ships. Where that
holds, the message states that cause, the archive-backed marketplace carries
the binary this source doesn't, and that marketplace's address
(`meow.retran.me`), in place of the install command that already ran.
Elsewhere, the message keeps naming `claude plugin install
meow-core@meowpaw` as it does today, because that remedy still fixes a
stale or missing install from the archive-backed marketplace.

Once this is accepted, a person on the `github` source reads, on the first
unresolved call, why the remedy they already ran changed nothing and which
address does. What still doesn't work: the message still can't tell a
`github`-source install with no release binaries yet built for this machine
from one with none ever shipped, because both look the same on disk; REQ-5200
asks only that the message name the cause and the address, not diagnose which
of the two applies.

## Why

BUG-1690 found the install reported success and the message kept returning
unchanged, because `claude plugin install meow-core@meowpaw` is a no-op
against a source already on that package. The message's own text is the only
thing the person sees once denied, so the fix has to live in the text the
launcher already prints, not in a install step nobody runs again.

## Alternatives

| Option                                                                            | Better at                                            | Why it lost                                                                                                                                                                             |
| --------------------------------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name the cause and the address in the message, probed from disk                   | One line fixes it for every launcher, no new state   | Chosen                                                                                                                                                                                  |
| Do nothing                                                                        | No launcher text changes                             | REQ-5200 stands unmet, and the next `github`-source install repeats BUG-1690 with no record to find                                                                                     |
| Have `claude plugin install` refuse a source that ships no binary                 | Catches the mismatch at install, not at first denial | The harness doesn't own that command; a launcher's own text is the only surface it can change                                                                                           |
| Detect the source from `known_marketplaces.json` instead of the sibling directory | Reads the actual declared source, not an inference   | `CLAUDE_PLUGIN_DATA`'s layout documents the sibling directory; the marketplace file's path and schema aren't (REQ-4510), so reading it risks a silent miss on a future platform release |

## What it costs

Every launcher's unresolved-binary branch gains one directory probe (a
sibling `.claude-plugin/` and a `bin/` listing) before it prints, so the
denial path does one more stat call under a case already slow enough that
the person is reading a message. The probe can misread a release that
genuinely ships a `github`-source install with a `bin/` directory partially
populated by a local build (SPC-1080's local-build path); where that happens,
the message names the wrong cause once, and the person still has the address
and the generic remedy both in front of them.

## What would reverse it

- The platform itself reports, on an install, that the chosen source ships no
  binary for a unit that needs one, which would make the launcher's own
  probe a second report of a fact the platform already gave.

## Consequences

`tools/launchers.toml` carries the probe and the two message branches,
`tools/generate_launchers.py` renders both into every unit's `bin/<name>`
launcher and `plugins/meow-flow/bin/paw`. Each launcher's fixture with no
binary gains a case for the `github`-source sibling layout, alongside the
existing no-binary case.

## How I will know it was realised

1. A launcher run from a `plugins/<name>` git subdirectory, with no `bin/`
   beside it, denies naming the cause and `meow.retran.me` (REQ-5200).
2. A launcher run from the archive-backed install, with no binary for the
   machine, denies naming `claude plugin install meow-core@meowpaw` as it
   does on the trunk today, unchanged.

## What this does not settle

- Whether the platform should refuse the `github` source for a unit that
  ships a binary, which is the platform's decision and not this
  repository's.
- Diagnosing a `github`-source install whose binary is merely stale rather
  than absent, which REQ-5200 doesn't ask for.
