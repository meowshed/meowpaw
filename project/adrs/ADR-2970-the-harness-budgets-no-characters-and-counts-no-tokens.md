---
id: ADR-2970
artifact: adr
status: done
revised: 2026-10-11
addresses: [REQ-1060, REQ-2748, REQ-3194, REQ-5000]
withdraws:
  [
    REQ-1056,
    REQ-1057,
    REQ-1058,
    REQ-1072,
    REQ-1074,
    REQ-1676,
    REQ-3164,
    REQ-4120,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2970. The harness budgets no characters and counts no tokens

## Decision

The character budget and the token count go, and the two obligations they
carried by accident stay with checks of their own.

The harness deletes the size-budget mechanism whole: every unit's
`budget.toml`, in the 16 Claude plugins and the 16 Pi packages, the `budget`
gate task, its binding into the `lint` stage, and `meow author cost`, the
subcommand that counted each unit's characters against it (REQ-1056, REQ-1057,
REQ-1058, REQ-1072, REQ-1074, REQ-4120). The documentation check stops
requiring a `plugin.json` description to name its unit's ceiling, and the
descriptions drop the phrase. The authoring skill stops telling the model to
run `meow-author cost` before cutting or keeping material.

Two things the budget carried must not fall with it:

- the platform's cap of 1,536 characters on a description (REQ-1060) is the
  platform's rule, so its check moves from the `cost` subcommand into `meow
author check`, which already reads every description;
- the authoring capability's enforcement of the writing standard (the half of
  REQ-1676 that isn't budgets) is restated as REQ-5000, and keeps its check.

The measurement suite stops counting tokens: `tools/loop.py` drops its token
probe and the `Tokens` and money `cost` columns, and SPC-1020 drops the stated
cost in tokens and the landing clause "and the token cost falls", so a
candidate lands on the difference holding or rising alone. The published
results under `plugins/meow-core/evals/results/` keep their tables, because
they are the history of runs already made, and a frozen record keeps the rules
it was approved under (ADR-1140).

The catalogue description stops stating what keeping a unit installed costs
(REQ-3164 withdrawn): it states what the unit does for the reader (REQ-3194).

This amends ADR-1460: its first half, material loads only when needed, stands
with every rule it placed; its second half, `meow-author` reporting each
unit's cost and use, is withdrawn here.

Left in force, because they bound a run or a request and not a character
count: the run bounds of ADR-2910 (an iteration ceiling, a time limit,
REQ-0870, REQ-0874, REQ-0876, REQ-2658, REQ-3724, REQ-3730, REQ-3732) and the
code host's request budget (REQ-2568). The owner's instruction said budgeting;
these are a different mechanism, and this decision takes none of them.

After this decision a unit states no budget, the gate holds no budget task,
and no number but a score comes out of a measurement. What still doesn't work:
nothing that worked before stops working, because the budget's one effect in
the tree in a month was to be raised, from 3,945 to 4,500 characters in
`meow-core`, which is a number recording history rather than bounding anything
(RES-0352).

## Why

The budget was introduced to hold the harness's permanent floor to a stated
size, and it never held anything: the one unit that reached its ceiling had
the ceiling raised in the same change, with the reason written beside the new
number. A check whose only possible outcomes are pass and raise-the-ceiling
checks nothing, and the character count a unit loads is already held by the
rules that keep material out of always-loaded context (REQ-1050, REQ-1052,
REQ-1054), which stand. The token count in the measurement suite answered a
question nobody acted on: no candidate decision cites a tokens figure, and the
landing rule it fed made a scoring gain refusable on a number the decision
never read. Removing both costs nothing the record cites and deletes two
mechanisms, 34 files and two columns, that maintenance carries without
return (RES-0352).

## Alternatives

| Option                                      | Better at                        | Why it lost                                                                                             |
| ------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Keep the budget, stop enforcing it          | A number a person can still read | A budget nobody enforces is a second stale number, which is the drift this removes                      |
| Keep the token columns, stop gating on them | No change to the suite           | The columns exist to gate the landing, and printed without a use they are the noise this removes        |
| Replace the budget with a softer warning    | Slack instead of a hard stop     | REQ-2780's slack applies to run bounds; a warning on characters is the same count with a softer failure |

## What it costs

Thirty-four `budget.toml` files, one subcommand, one gate task, one stage
binding and two table columns go. The ceiling check moves into `meow author
check`, so the authoring unit's test grows by a case there and loses its
budget cases.

## What would reverse it

I would bring the budget back if a unit's always-loaded material grew
unnoticed past what a reader would accept, shown by a review finding a
description or a style grown by hundreds of characters with nothing cut, on
both models' sessions. I would bring the token count back once a decision
needed a tokens figure to decide something, and named it.

## Consequences

- REQ-1056, REQ-1057, REQ-1058, REQ-1072, REQ-1074, REQ-1676, REQ-3164 and
  REQ-4120 are withdrawn, REQ-1676 replaced by REQ-5000 and REQ-3164 by
  REQ-3194.
- SPC-1030, SPC-1020, SPC-1080, SPC-1010, SPC-1110, SPC-1130, SPC-1201 and
  SPC-1300 lose their budget and token statements; CLAUDE.md loses the gate's
  `budget` row.
- `meow author check` gains the platform-cap check.

## How I will know it was realised

1. No `budget.toml` exists in either tree, and `grep` over `plugins/`,
   `packages/` and `crates/meow/` for `permanent_characters` matches nothing.
2. The gate holds no `budget` task, and `.meowpaw/profile.toml`'s `lint` stage
   names none.
3. `meow author check` fails a fixture description over the cap of 1,536
   characters (REQ-1060).
4. `tools/loop.py` prints no `Tokens` column and no money cost, and its
   landing rule cites the difference alone.
5. The eight requirements carry `status: withdrawn`, each naming this
   decision, and REQ-5000 and REQ-3194 carry what survives them.
6. Every requirement this decision addresses lands in exactly one closed task.

## What this does not settle

Whether a repository using the harness wants a budget of its own, which its
own profile may state; the harness ships no mechanism for it, and a repository
that asks for one gets a new decision.
