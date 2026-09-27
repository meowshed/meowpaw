---
id: ADR-1460
artifact: adr
status: approved
revised: 2026-09-27
addresses:
  [
    REQ-1052,
    REQ-1054,
    REQ-1068,
    REQ-1070,
    REQ-1072,
    REQ-1074,
    REQ-1076,
    REQ-1078,
    REQ-2696,
    REQ-2698,
    REQ-2700,
    REQ-2702,
    REQ-2704,
  ]
supersedes: []
---

# 1460. Material loads only when it is needed, and `meow-author` reports each unit's cost and use

## Decision

`meow-author` gains a second command, `meow-author cost`, and its `write` skill
gains the rules on when material loads.

`meow-author cost` reports, for each unit under `plugins/`, the characters it
keeps in context on every turn against the budget its `budget.toml` states. It
counts the description and `when_to_use` of each skill and agent the model can
load, and the whole of each output style (REQ-1072). It fails on a unit over
its budget, a unit with no `budget.toml` and a description and its
`when_to_use` together over the platform's cap of 1,536 characters, as
`tools/check_budget.py` does today. This
repository's `budget` task runs it in place of that script, which goes, so the
report is part of every verification (REQ-1074).

How often each skill is used comes from the platform's own `/skill-doctor`,
which reports each skill's token cost and how often it is invoked (RES-0005).
`meow-author cost` ends by naming it, and the `write` skill has the model run
it before cutting or keeping a unit, so the harness reports its cost and its
use together without reading the platform's private files (REQ-1072).

The `write` skill's new rules:

- material needed only once a capability is chosen loads at that point, and
  material for an unusual case loads only in that case, never carried by
  material that is always loaded (REQ-1052, REQ-1054);
- one capability is one skill, and one skill belongs to one discipline, split
  where it spans two (REQ-1068, REQ-1070);
- a rule carries its reason beside it where the rule is counter-intuitive or
  the model's default is wrong, and otherwise the reason lives in material
  loaded on demand (REQ-1076);
- moving explanation out of always-loaded material is shown not to change
  behaviour by the loop SPC-1020 states, not by assertion (REQ-1078);
- instruction that applies only to certain files is a path-scoped rule, and
  splitting always-loaded material into imported files counts as no saving,
  because the platform expands imports at launch (REQ-2696, REQ-2698);
- nothing loads because it might be relevant, no obligation sits in a file
  read at the model's discretion, and mutually exclusive branches sit in
  separate files (REQ-2700, REQ-2702, REQ-2704).

After this decision a repository sees what each unit costs on every turn and
how often it earned that cost, and the rules on loading are in front of the
model when it writes material. What still doesn't work: whether a unit loads
only when needed is judged from its wording, so review holds it.
`/skill-doctor` counts skills, so a unit's agents and output styles show no use
there, and the kernel, which ships only an output style, can't be judged by its
count.

## Why

RES-0005 found that the descriptions of what is installed are the harness's
permanent floor, and that a skill's cost and how often it is invoked together
answer whether it earns that cost, measured by `/skill-doctor`. Today the cost
is checked by a script in `tools/`, which no other repository gets;
`meow-author` already ships the rest of the authoring capability (ADR-1450), so
the cost joins it.

The usage comes from `/skill-doctor` because the platform measures it already,
and because RES-0262 found that parsing the platform's own transcripts, whose
format is internal and changes between versions, is the failure a harness
must not repeat. RES-0202 found that loading a nearly relevant skill adds a
distractor with a measured cost, which is why "might be relevant" is no reason
to load one.

The strongest objection: a usage figure a person has to fetch with a slash
command is one a program can't gate on. It is a figure for a person deciding
what to cut, which no gate should decide, and the cost, which a gate can
hold, stays in `meow-author cost`.

## Alternatives

| Option                                      | Better at                         | Why it lost                                                                                                             |
| ------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                  | No change                         | The cost check stays in `tools/`, and nothing reports how often a unit is used                                          |
| Keep the budget script, add usage beside it | Nothing to port                   | Only this repository gets either, against REQ-1672, which ADR-1450 answered for the rest                                |
| Count loads from the session transcripts    | A usage figure in the same report | RES-0262 found parsing the platform's transcripts is the failure: their format is internal and changes between versions |
| Telemetry of the harness's own              | Usage across machines             | A service a person installs and operates separately, against REQ-3178                                                   |
| Loading rules in SPC-1030 only              | No change to the skill            | A specification isn't in front of the model when it writes material                                                     |

## What it costs

The `write` skill grows by eleven rules, loaded only when material is written.
`meow-author` gains a command, and the `budget` task moves to it.

## What would reverse it

I would reverse the use of `/skill-doctor` if the platform removed it or
stopped reporting invocations, because the harness would then report cost
alone.

## Consequences

- `meow-author cost` replaces `tools/check_budget.py` in the `budget` task.
- `meow-author:write` carries the loading rules.
- SPC-1030 states the report and the rules.

## How I will know it was realised

1. `meow-author cost` reports this repository's units against their budgets
   and passes, and fixtures show it failing on a unit over its budget, a unit
   with no budget, and a description over the cap.
2. `meow-author cost` names `/skill-doctor` as where each skill's use is
   reported, and the `write` skill has the model consult it before cutting or
   keeping a unit.
3. The skill's rules carry REQ-1052, REQ-1054, REQ-1068, REQ-1070, REQ-1076,
   REQ-1078 and REQ-2696 to REQ-2704, traced in the task's evidence.
4. Every requirement ADR-1460 addresses lands in exactly one closed task.

## What this does not settle

- Usage across machines, which would need a service.
- Which units to cut on the evidence of the report, which is the owner's call.
