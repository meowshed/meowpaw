---
id: ADR-3040
artifact: adr
status: done
revised: 2026-10-24
addresses:
  [
    REQ-2798,
    REQ-2800,
    REQ-3074,
    REQ-3196,
    REQ-4510,
    REQ-4610,
    REQ-4612,
    REQ-4614,
    REQ-4624,
    REQ-4622,
  ]
postpones: []
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3040. Ten requirements that no task names get one epic

## Decision

I plan the ten requirements that ADR-2920 and ADR-2990 addressed and no task
names, REQ-2798, REQ-2800, REQ-3074, REQ-3196, REQ-4510, REQ-4610, REQ-4612,
REQ-4614, REQ-4624 and REQ-4622, in one epic of five tasks. Two tasks name
behaviour that already holds and give it a test that cites the requirement: the
shared executable's name, its distribution and the equal versions of a plugin
and its package, and the trunk's passing gate (TSK-5680); and the judge hook's
matchers, which already name only publishing commands (TSK-5681). Three tasks
build: `paw` answers within a second on a tree it has read (TSK-5682), a unit's
launcher and Pi extension are generated from one template and the copies of a
unit's description and page are held to each other (TSK-5683), and a launcher
resolves its binary once per machine (TSK-5684).

This is the direction the owner chose on 2026-10-13 for the Pi tree: generate it
from the Claude tree in place of keeping both by hand. REQ-4624 and REQ-4622 state it, and no earlier plan carried them out. REQ-4624
narrows REQ-4620, which asked for every Pi extension to be generated: seven
extensions carry a host's hook and command adapters that no template
expresses, so they stay hand-written.

Once this is accepted, every requirement in force is named by a task or
postponed, except REQ-1666's postponement by ADR-3030. What still doesn't work:
a Pi package's page mirrors its unit's page only where the unit marks a section
as host-specific, so a host difference not marked will fail the check until
someone marks it.

## Why

ADR-2920 and ADR-2990 addressed these requirements and closed with tasks that
covered other requirements, which `paw status` shows as ten requirements named
by no task. A requirement in force with no task is a promise nobody is working
on. Measured on 2026-10-24, `paw check` took 3.5 seconds on this repository's
record and `paw status --brief` 1.2 seconds, against the second REQ-2800 asks.

## Alternatives

| Option                        | Better at      | Why it lost                                                                                      |
| ----------------------------- | -------------- | ------------------------------------------------------------------------------------------------ |
| Do nothing                    | Costs no work  | Leaves ten requirements in force that nobody works on, and the status line never reaches zero    |
| Postpone the three that build | Smaller change | REQ-4624 and REQ-4622 are what the owner chose for the Pi tree, and REQ-2800 is a failing number |
| One task for all ten          | One record     | A task that closes ten requirements across five areas can't be reviewed or reverted in parts     |

## What it costs

A generator for launchers and extensions, a check that holds a package's page to
its unit's, and a cache for the record. Each is code the harness keeps, and each
can fail a gate.

## What would reverse it

- The owner decides Pi isn't needed, which makes REQ-4624 and REQ-4622 moot, or
  the generator takes longer to keep than the hand-written copies it replaces.

## Consequences

An epic, five tasks and one pull request. REQ-2800 may add a cache under a
state directory, which ADR-2970's rule against counting tokens doesn't touch.

## How I will know it was realised

1. Every requirement named above is named by a task that is done.
2. `paw check` on this repository's record completes in under one second when
   nothing changed since the last call.
3. A unit's committed launcher and Pi extension equal what the generator
   writes, and a check fails naming a copy that differs.

## What this does not settle

- How the generator is invoked, which TSK-5683 decides within the constraints it
  states.
