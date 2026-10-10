---
id: ADR-2870
artifact: adr
status: done
revised: 2026-10-10
addresses: [REQ-4500, REQ-4502, REQ-4504, REQ-4506, REQ-4508]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2870. The core unit ships the one build of the tool, and the units depend on it

## Decision

`meow-core` ships the one build of the native tool, for every platform the
harness supports, with every unit's program in it (REQ-4500). A unit that runs
a program of the tool declares `meow-core` under `dependencies` in its
manifest, and depends on no other unit (REQ-4502), so the platform installs the
core unit with it. The units ship no binary of their own.

A unit's launcher finds the binary through the core unit's data directory. The
core unit's session start writes the path of its own installed root there, and
the launcher reads it from `~/.claude/plugins/data/<id>/`, a path the platform
documents, and not from the cache layout (REQ-4504). Where it finds no binary
the launcher reports each of the unit's checks as unresolved and names the core
unit as what would supply it (REQ-4506).

I choose the core unit over a new one because it is the kernel the other units
already assume, so the dependency points down. The work is two epics: the core
unit ships the build and the units find it, then the units drop their own
builds and the standalone check follows.

Once this is accepted, the records say a unit may depend on the core unit and
nothing in the tree has changed. Once EPC-2780 lands, units find the shared
binary and still carry their own. What still doesn't work: a hook that runs
before the core unit's first session start finds no data path and reports
unresolved, which it does until the first session of an install has begun.

## Why

RES-0347 found that the platform installs a dependency with the plugin and
documents the data path a launcher can read, and that 13 archives sum to 41 MB
where the one build is about 7 MB. The cache layout would work today, as the
`meow-scm` lookup does, and RES-0347 finds that the documentation doesn't
promise it.

## Alternatives

| Option                                 | Better at                           | Why it lost                                                          |
| -------------------------------------- | ----------------------------------- | -------------------------------------------------------------------- |
| Do nothing                             | Each unit works alone               | 13 builds and 41 MB, and 12 feature builds on every release          |
| A new unit that holds the binary       | `meow-core` stays free of a program | A 17th unit for the same cost, and the owner asked for the core unit |
| Look the binary up in the cache layout | No session start hook               | Undocumented, and several versions of the core unit sit in it        |
| Download the binary at first use       | Small archives                      | A network call at run time, which the records refuse                 |

## What it costs

A unit is no longer a harness on its own: installing one installs the core
unit, and removing the core unit disables the others. REQ-0074 and REQ-0076 are
withdrawn for that, and `tools/check_standalone.py` needs a rule that lets a
unit name the core unit and no other. The core unit gains a program and a hook,
so its character budget on every turn has to hold the hook.

## What would reverse it

- The platform changes `dependencies` so that a dependency's directory has a
  documented variable, in which case the data directory file is dropped. Or a
  release of the core unit breaks a dependent's load check twice in a row.

## Consequences

REQ-0074 and REQ-0076 are withdrawn and replaced by REQ-4502 and REQ-4508. ADR-1110 is amended in what
it says of a binary for each unit, ADR-1270 in what it says of a unit standing
alone, and ADR-2810, which listed this switch under what it does not settle,
is settled by it. EPC-2780 and EPC-2790 carry four tasks.

## How I will know it was realised

1. `plugins/meow-core` carries the binary for each platform, and no other unit
   carries one (REQ-4500).
2. Each unit that runs a program names `meow-core` and nothing else under
   `dependencies` (REQ-4502).
3. A unit's launcher run with the data file absent exits 3 and names `meow-core`
   (REQ-4506).

## What this does not settle

- Where `claude plugin install` fails because the core unit's version doesn't
  satisfy a unit's range, which depends on the marketplace's archive sources.
- The Pi packages, which already share one binary (REQ-4136).
