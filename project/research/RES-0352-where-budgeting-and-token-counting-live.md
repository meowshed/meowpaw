---
id: RES-0352
artifact: research
status: approved
revised: 2026-10-11
elaborates: RES-0213
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Budgeting and token counting, and where they live in both trees

## Summary

The harness carries two measuring mechanisms nobody asked to keep: a character
budget per unit, stated in a `budget.toml` per unit in both the Claude Code
plugins and the Pi packages, and a token count in the measurement suite's
tables. This document maps every place both live, so a decision to remove them
can name what it deletes and what it keeps. It covers this repository's trees
only, and reads no other project's practice.

## The question

The owner asked to remove all budgeting and token counting and to reject the
requirements that state them. What constrains it: the run bounds (an iteration
ceiling, a time limit, a request budget on the code host) are a different
mechanism the request doesn't name, and the platform's own cap of 1,536
characters on a description is the platform's rule, not the harness's. The
assumption behind the question, challenged: that a budget earns its check. It
doesn't — the budget's one effect in the tree was to be raised (3,945 to 4,500
in `plugins/meow-core/budget.toml` in a month), so the number records history
rather than bounds anything.

## Method

Searched both trees with `grep` for `budget`, `permanent_characters`,
`ceiling`, `tokens` and `cost`, over `plugins/`, `packages/`, `crates/meow/`,
`tools/`, `mise.toml`, `.meowpaw/profile.toml`, `docs/` and `project/`, and
searched the record with `paw find budget`, `paw find token` and `paw find
cost`, each exhaustive over 2,144 artifacts. Read the hits that carry
behaviour: `crates/meow/src/author.rs`, `tools/check_docs.py`,
`tools/loop.py`, `tools/test_secrets_rule.py`, `mise.toml`,
`.meowpaw/profile.toml`.

## Findings

- **The character budget is stated per unit and checked by one command.** All
  16 Claude plugins and all 16 Pi packages carry a `budget.toml` with
  `permanent_characters`, which two requirements state. `meow author cost`
  (`crates/meow/src/author.rs`, the `cost` subcommand) counts the characters of
  each description, skill, agent and output style a unit loads on every turn,
  compares with the budget, and fails the gate's `budget` task on an overrun,
  which two requirements make a defect and a standing check. `mise.toml`
  composes the task into `all`, and `.meowpaw/profile.toml` binds it into the
  `lint` stage.
- **The budget also drags two obligations with it.** The documentation check
  (`tools/check_docs.py`) requires every `plugin.json` description to name its
  unit's ceiling from `budget.toml`, and 23 unit READMEs state a character
  count for the same reason. The authoring skill
  (`plugins/meow-author/skills/write/SKILL.md`) tells the author to run
  `meow-author cost` before cutting or keeping material, which a requirement
  states.
- **The platform cap shares the subcommand.** The `cost` subcommand is also
  where the platform's cap of 1,536 characters on a description is checked,
  which stays in force when the budget goes. Removing the subcommand whole
  would leave that cap named by no check.
- **Token counting lives in the measurement suite alone.** `tools/loop.py`
  measures each run's input tokens against an empty probe (`input_tokens`,
  `token_cost`) and prints `Tokens` and a money `cost` column, both derived
  from the same usage counts; the landing rule "a candidate lands when the
  difference holds or rises on both models and the token cost falls" and the
  stated "cost in tokens" sit in `SPC-1020` (lines 110 and 154). No requirement
  states token counting: a search over `project/requirements/` for `token cost`
  and `cost in tokens` matches nothing. The published results under
  `plugins/meow-core/evals/results/` keep their tables as history.
- **The run bounds are a different mechanism.** A set of requirements naming
  an iteration ceiling, a time limit and a request budget on the code host, and
  ADR-2910, bound a run's iterations and time. None counts characters or
  tokens; none is touched.

## Conclusions

1. The harness states no size budget for a unit, and no check reads a
   `budget.toml`.
2. The harness runs no command that reports a unit's context cost, and the
   gate holds no budget task.
3. A description's fit under the platform's cap of 1,536 characters keeps a
   standing check, carried by the check the authoring capability already runs.
4. The measurement suite states no token count and no money cost, and a
   candidate's landing depends on the score difference alone.
5. Material still loads only when the work needs it, and the writing standard
   still holds, because neither rests on the budget.

## Sources

- `crates/meow/src/author.rs` at `4f32e7ce`, 2026-10-11 - the `cost` subcommand, the cap and the ceiling read.
- `mise.toml` at `4f32e7ce`, 2026-10-11 - the `budget` task and its place in `all`.
- `.meowpaw/profile.toml` at `4f32e7ce`, 2026-10-11 - the `lint` stage binding.
- `tools/check_docs.py` at `4f32e7ce`, 2026-10-11 - the ceiling-naming check.
- `tools/loop.py` at `4f32e7ce`, 2026-10-11 - the token and cost columns.
- `project/specs/SPC-1020-measuring-the-harness.md` at `4f32e7ce`, 2026-10-11 - the stated cost in tokens and the landing rule.
- `project/specs/SPC-1030-how-the-harness-writes-a-prompt.md` at `4f32e7ce`, 2026-10-11 - the budget rules and the `meow-author cost` table row.
- `project/specs/SPC-1300-the-pi-packages.md` at `4f32e7ce`, 2026-10-11 - the Pi packages' `budget.toml`.
- `paw find budget`, `paw find token`, `paw find cost`, 2026-10-11, exhaustive - the requirements named above.
