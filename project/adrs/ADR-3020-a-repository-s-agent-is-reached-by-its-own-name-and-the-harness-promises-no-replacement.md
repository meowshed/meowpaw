---
id: ADR-3020
artifact: adr
status: done
revised: 2026-10-24
addresses: [REQ-3273]
postpones: []
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3020. A repository's agent is reached by its own name, and the harness promises no replacement

## Decision

I withdraw REQ-2986, which asked that a repository be able to replace any agent
the harness ships, and replace it with REQ-3273: a page that ships an agent
states which name reaches the unit's definition and which reaches a
repository's own agent of the same name. TSK-4955 is withdrawn, and TSK-5670
closes REQ-3273 with the pages and the test that already shipped with it.
ADR-2560 says a repository's definition of the same name is loaded in place of
the plugin's, and this decision amends that sentence and leaves the rest of
ADR-2560 as it is.

RES-0368 found that the platform keeps both definitions: a dispatch of
`meow-flow:researcher` reached the unit's, and a dispatch of `researcher` the
repository's. A promise of replacement would rest on a behaviour the harness
doesn't control.

Once this is accepted, no document promises replacement, and the pages for
`meow-flow` and `meow-prose` say which name reaches which definition. What
still doesn't work: a repository can't swap the researcher or the prose
reviewer that a step dispatches. It can run its own agent by its own name.

## Why

RES-0368 is the only evidence, and it is one run on one model. I withdraw the
requirement on it because the opposite claim has no evidence at all, and a
requirement is a promise.

## Alternatives

| Option                     | Better at                           | Why it lost                                                                                               |
| -------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Do nothing                 | Keeps ADR-2560 whole                | Keeps a promise the run contradicts, so a repository that defines a same-name agent still gets the unit's |
| Steps dispatch a bare name | A repository's definition would win | Nobody has run what a bare name reaches where the repository defines none, and it rewrites every step     |

## What it costs

A repository that wants a different reviewer changes the step that dispatches
it, or runs its own agent itself.

## What would reverse it

- The platform is shown to answer a same-name dispatch with the repository's
  definition, or a step that dispatches a bare name is shown to reach the
  unit's agent where the repository defines none.

## Consequences

REQ-2986 is withdrawn and REQ-3273 is in force. TSK-4955 is withdrawn, and
EPC-2530 closes with two tasks done.

## How I will know it was realised

1. `tools/test_shipped_agents.py` fails a page that ships an agent and doesn't
   say which name reaches which definition.
2. `paw check` reports no requirement in force that promises replacement.

## What this does not settle

- What the platform documents about resolving a name, which I didn't read.
- Pi, which ships no agents.
