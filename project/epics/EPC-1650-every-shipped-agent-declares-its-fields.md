---
id: EPC-1650
artifact: epic
status: approved
revised: 2026-09-30
realises: ADR-1700
---

# Every shipped agent declares its turns, tools, model, effort, instructions and skills, and meow-author check fails one that doesn't

Realises exactly one authorising record, ADR-1700. The epic is complete when
`meow-author check` fails an agent that leaves out any of the six fields,
both agents the harness ships declare them and hold no delegation tool, and
the write skill and the method skill carry the rules no program can check.

**Amended by ADR-2300.** ADR-2300 removed `record-reviewer` and its evaluation cases, so criterion 3's hand-run case, criterion 4's ceiling case, which dispatched it, and the `record-reviewer` half of criterion 6 no longer apply, and criterion 7 is checked by `paw check coverage` in each task's gate.

## Acceptance criteria

Taken from ADR-1700, from its list of how I will know it was realised, before
the tasks below were written:

1. Crate tests over fixture agents show the check failing, naming the file
   and the field, on an agent with no `maxTurns`, one with `maxTurns: 0`, one
   with no `tools`, one with `tools: "*"`, one listing `Agent`, one listing
   `Task`, one listing `Agent(worker)`, one naming `Agent` in a
   comma-separated `tools` string, one with no `model`, one with
   `model: inherit`, one with `model: opsu`, one with no `effort`, one with
   `effort: extreme`, one with no `omitClaudeMd`, one with no `skills`, and
   one of each wrong type TSK-2700 lists. They show it failing with
   that reason on a front matter block that doesn't parse, and passing on one
   declaring all six with `skills: []`, on a shipped agent with `tools: []`,
   on one naming a full model identifier, on a repository's own agent listing
   `Agent` and on a repository's own agent with `tools: "*"`. The passing
   fixture's declarations are added only after the failing ones are seen
   failing against the current check.
2. `mise run prompts` exits 0 at the merge revision with both shipped agents
   declaring the fields in ADR-1700's table.
3. A hand-run evaluation case under `plugins/meow-flow/evals/`, run by a
   person and never in CI, asks `record-reviewer` to hand part of its review
   to another agent, and its transcript shows no Agent call and the review
   done by the reviewer itself.
4. A hand-run case dispatches an agent defined with `maxTurns: 2` on work
   that needs more, and its output comes back marked as stopped at its
   ceiling.
5. A hand-run `meow-author` evaluation case asks for an agent that carries a
   language's idioms, and the write skill produces a skill.
6. `meow-prose:prose` and `meow-flow:record-reviewer`, each dispatched with a
   path alone, read the updated SPC-1030, SPC-1090 and write skill and report
   no sentence treating a delegated agent as a boundary, and the task's
   evidence names both as the judge for REQ-2976. A person reads both reports
   before the task closes.
7. Every requirement ADR-1700 addresses, REQ-2972, REQ-2974, REQ-2976,
   REQ-2982, REQ-2984, REQ-2988 and REQ-3270, lands in exactly one closed
   task, and REQ-3271 reads as postponed.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 [P] TSK-2700 make `meow-author check` in `crates/meow/src/author.rs`
      require the six fields and declare them in each shipped agent
      closes: REQ-2974, REQ-2982, REQ-2984, REQ-2988, REQ-3270
      evidence: the 26 `AgentFields` checks and `ShippedAgents` pass after
      failing first, and `meow-author check` passes every shipped agent,
      `router` included, in #667. TSK-2700 carries the runs. Criterion 3's
      hand-run case is dropped with `record-reviewer`.
      depends: nothing

- [>] T-002 [P] TSK-2701 give `meow-author:write` the rules a program can't
  check, and add the hand-run case for knowledge shipped as a skill
  closes: REQ-2972, REQ-2976
  evidence: the `WriteSkill` checks pass after failing first, in #686.
  TSK-2701 carries the rest. Criteria 4 and 5 wait for a person to run the
  hand-run case and to read what `prose` reports.
  depends: nothing

TSK-2700 and TSK-2701 touch different files except `meow-flow`'s and
`meow-author`'s versions and their READMEs' `describes`, so whichever lands
second takes the next version above the first. TSK-2701's rules for the six
fields describe the check TSK-2700 adds, and they read correctly whichever
lands first, because each rule states its reason and not the check's output.

## Coverage

ADR-1700 addresses seven requirements, and each lands in one task. REQ-2974,
REQ-2982, REQ-2984, REQ-2988 and REQ-3270 land in TSK-2700, because each is a
field `meow-author check` reads, and the check and the two agents change in
one change so the gate stays green. REQ-2972 and REQ-2976 land in TSK-2701,
because no field shows either, so they are rules in the write skill that
review holds.

Criteria 1, 2 and 3 close in TSK-2700, and criteria 4, 5 and 6 in TSK-2701. Criterion 7 is checked at the verify step by
`paw check coverage` and by REQ-3271's postponement in ADR-1700.

The smallest set that tests the decision is TSK-2700: with it, every shipped
agent carries a turn ceiling, a model, an effort and no delegation tool, and
the gate fails an agent that drops one. Before any task is finished, one
thing can be measured: the number of shipped agents declaring all six
fields, which is 0 today, because `record-reviewer` declares only `tools`
and `prose` only `tools` and `skills`, and must be 2.

Criteria 3 and 4 rest on the platform's behaviour, which a third party
controls. The project ships the agents' `tools` lists and `maxTurns` values
and the two evaluation cases. Whether the platform marks an output as
stopped at its ceiling is what criterion 4 observes, and until a run shows
the marking, a dispatcher treats any output of a run that reached its ceiling
as unfinished, as ADR-1700 says.

## Not covered

- REQ-3271, the session's nesting depth, which ADR-1700 postpones until a
  plugin's `settings.json` can set it.
- Running the check over this repository's own `.claude/` agents, which
  ADR-1700 names under what still doesn't work: the `prompts` task runs
  `meow-author check` with no path.
- `permissionMode`, `hooks` and `mcpServers`, and a skill forked with
  `context: fork`, which ADR-1700 leaves unsettled.
- The user-facing pages beyond each unit's README `describes`, which the
  document step updates from ADR-1700's consequences once both tasks are
  done.
