---
id: ADR-2680
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-3080, REQ-3084, REQ-3086, REQ-3090]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2680. The diagnostic answers whether the repository can be worked on, and writes nothing

## Decision

`meow-checks doctor` answers one question: can this repository be worked on
here. `paw status` answers the other, where the work stands, and neither
command answers both (REQ-3080). The diagnostic reports the profile's state,
each verb's resolution and each pack's detection, naming which pack matched
which marker file, so a wrong detection shows before a wrong command runs
(REQ-3090).

A finding that depends on this machine, a missing tool or an old platform,
is marked `machine`, so "this machine can't build this" isn't read as "this
repository is broken" (REQ-3084). The diagnostic repairs nothing and writes
nothing, a cache included (REQ-3086).

Once this is accepted, a person new to a repository runs one command to learn
whether they can start. What still doesn't work: the diagnostic reads the
installed packs only, so a pack that isn't installed can't report its
marker.

## Why

RES-0160 read a `/meow:doctor` command and found it mixed "can I work here"
with "what's next", so neither answer was easy to find, and that a doctor
which fixes what it finds changes a repository nobody asked it to.
RES-0215 found that a surface answers one question well and two badly.
`meow-checks` already resolves the verbs, so it holds the diagnostic.

## Alternatives

| Option                     | Better at               | Why it lost                                         |
| -------------------------- | ----------------------- | --------------------------------------------------- |
| Do nothing                 | No new command          | A person learns a tool is missing when a verb fails |
| Put it in `paw status`     | One command to remember | It mixes the two questions REQ-3080 separates       |
| A doctor that fixes things | Saves a step            | It writes into a repository, against REQ-3086       |

## What it costs

One more command, and each pack has to report its markers to it.

## What would reverse it

- People run `paw status` and the diagnostic together every time, which would
  show the two questions are one in practice.

## Consequences

`meow-checks` gains `doctor`. Each pack's `status` reports the markers it
matched.

## How I will know it was realised

1. `meow-checks doctor` on a fixture repository names each pack and the
   marker it matched (REQ-3090).
2. A missing tool's finding is marked `machine` (REQ-3084).
3. The tree is byte-identical before and after a run (REQ-3086).

## What this does not settle

- What `paw status` reports, which ADR-1170 and ADR-1210 decided.
