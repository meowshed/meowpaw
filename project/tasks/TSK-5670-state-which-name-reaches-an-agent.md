---
id: TSK-5670
artifact: task
status: done
revised: 2026-10-24
realises: ADR-3020
closes: [REQ-3273]
issue: 1118
projected: 13d85825d01e
tracked: 0b04ccedbeff
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# State which name reaches an agent

The pages for `meow-flow` and `meow-prose` say which name reaches the unit's
agent and which reaches a repository's own agent of the same name, and a test
holds them to it. This work shipped with TSK-4955 in pull request 1072, and
the task records it against the requirement that replaced REQ-2986.

## Acceptance criteria

1. Given a page that ships an agent, when `tools/test_shipped_agents.py` runs,
   then the page states how to define a repository's own agent and which name
   reaches which definition, and a page that doesn't fails (REQ-3273). Closed
   by: `ReplacingAnAgent` in `tools/test_shipped_agents.py`.

## What to do

Nothing is left to build. The sections "Replace the researcher" in
`plugins/meow-flow/README.md` and "Replace the reviewer" in
`plugins/meow-prose/README.md` and the test exist on the trunk.

## Depends on

Nothing.

## Evidence

Criterion 1 is closed by `ReplacingAnAgent` in `tools/test_shipped_agents.py`,
which names REQ-3273 and holds each page that ships an agent to naming
`.claude/agents/<agent>.md`, `<unit>:<agent>` and the bare name. `python3 -m unittest
tools/test_shipped_agents.py` ran 7 tests and passed all 7. The pages and the
test shipped with TSK-4955 in pull request 1072, before REQ-3273 existed, so
this task records them against the requirement that replaced REQ-2986.

Every stage passed in pull request #1072.

## Left alone

Every claim that the repository's definition wins, which RES-0368 found false.
