---
id: TSK-2700
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1650
closes: [REQ-2974, REQ-2982, REQ-2984, REQ-2988, REQ-3270]
issue: 659
projected: 6cc5c14f469e
---

# Make `meow-author check` require an agent's six fields, and declare them in both shipped agents

`meow-author check` fails an agent that leaves out `maxTurns`, `tools`,
`model`, `effort`, `omitClaudeMd` or `skills`, or holds a value SPC-1030's
table doesn't accept, and fails a shipped agent whose `tools` can delegate.
`record-reviewer` and `prose` declare all six in the same change, so the gate
stays green. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given a fixture unit whose agent leaves out one field, when
   `meow-author check` runs on it, then it exits 1 naming the file and that
   field, for each of: no `maxTurns`, no `tools`, no `model`, no `effort`, no
   `omitClaudeMd` and no `skills`. Closed by: `AgentFields.test_a_missing_<field>_fails`
   for each of the six, in `plugins/meow-author/tests/test_author.py`.
2. Given a fixture unit's agent with `maxTurns: 0`, `model: inherit`,
   `model: opsu` or `effort: extreme`, or with a wrong type, `maxTurns: -1`,
   `maxTurns: 2.5`, `effort: 3`, `omitClaudeMd: yes` or `skills` written as a
   string, then the check exits 1 naming the file and the field. Closed by:
   `AgentFields.test_a_zero_ceiling_fails`,
   `AgentFields.test_inherit_fails`,
   `AgentFields.test_an_unknown_model_alias_fails`,
   `AgentFields.test_an_unknown_effort_fails` and
   `AgentFields.test_a_wrong_type_fails` for each of the five wrong types.
3. Given a unit's agent with `tools: "*"`, one listing `Agent`, one listing
   `Task`, one listing `Agent(worker)` and one naming `Agent` in a
   comma-separated `tools` string, then the check exits 1 naming the file and
   `tools` for each. Closed by: `AgentFields.test_a_shipped_agent_with_every_tool_fails`,
   `AgentFields.test_a_shipped_agent_listing_agent_fails`,
   `AgentFields.test_a_shipped_agent_listing_task_fails`,
   `AgentFields.test_a_restricted_agent_entry_fails` and
   `AgentFields.test_agent_in_a_comma_separated_list_fails`.
4. Given an agent whose front matter doesn't parse, then the check exits 1
   with that reason and reports no field. Closed by:
   `AgentFields.test_front_matter_that_does_not_parse_fails_alone`.
5. Given a unit's agent declaring all six with `skills: []`, one with
   `tools: []`, one naming a full identifier such as `model: claude-opus-5-5`,
   and a
   repository's own agent under a path such as `.claude/agents/` listing
   `Agent` or with `tools: "*"`, then the check exits 0 on each. Closed by:
   `AgentFields.test_an_agent_declaring_all_six_passes`,
   `AgentFields.test_a_shipped_agent_with_no_tools_passes`,
   `AgentFields.test_a_full_model_identifier_passes`,
   `AgentFields.test_a_repositorys_own_agent_may_list_agent` and
   `AgentFields.test_a_repositorys_own_agent_may_list_every_tool`. Each first
   asserts a refusal with one field removed, because the check passes an
   agent with only a `description` today and a check asserting only the 0
   couldn't fail before the change.
6. Given this change's tree, when `mise run prompts` runs, then it exits 0,
   and `plugins/meow-flow/agents/record-reviewer.md` and
   `plugins/meow-prose/agents/prose.md` declare the values in SPC-1030's
   table under "What an agent declares". Closed by: the kept evidence of the
   gate's run at the merging revision.
7. Given `plugins/meow-flow/evals/review-without-delegating/`, when a person
   runs it by hand, then the transcript shows `record-reviewer` making no
   Agent call and doing the review itself. Closed by: judgement, because a
   hand-run evaluation is a model's run read by a person and never runs in
   CI; the kept transcript is the evidence.

## What to do

In `crates/meow/src/author.rs`, the agent branch that checks `description`
gains the six field rules SPC-1030 states under "What an agent declares" and
"The check": each field present, each value one the table accepts, and in a
unit's `agents/` directory a `tools` list with no `*`, no `Agent` and no
`Task`, alone or with a restriction. `tools` is read as a YAML list or as a
comma-separated string. A front matter block that doesn't parse fails with
that reason and runs no field rule. A repository's own agent, reached through
a path the check is given, passes the `tools` rule once it writes a list.

The ADR's first criterion names crate tests; I chose the Python fixtures in
`plugins/meow-author/tests/test_author.py`, class `AgentFields`, because
they drive the built binary as the existing `Check` fixtures do. Write the
failing fixtures first, in a commit of their own, and see them fail against
the current check before the passing fixture gains its declarations.

Give `plugins/meow-flow/agents/record-reviewer.md` and
`plugins/meow-prose/agents/prose.md` the values in SPC-1030's table. Add the
hand-run case `plugins/meow-flow/evals/review-without-delegating/`, with a
`prompt.md` and graders in the shape of the unit's other cases, and its line
in `plugins/meow-flow/evals/thresholds.toml`; it never runs in CI.

Raise `meow-author`'s minor version, because the check fails agents it
passed before, and name the six fields and the reason for each in its README
and release notes. Raise `meow-flow`'s and `meow-prose`'s patch versions. Each
README's `describes:` matches its version.

## Depends on

Nothing. ADR-1700 and EPC-1650 are approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

The write skill and the method skill, which TSK-2701 changes. This
repository's `prompts` task, which still runs `meow-author check` with no
path, so this repository's own `.claude/` agents stay unchecked, as ADR-1700
says under what still doesn't work. `permissionMode`, `hooks` and
`mcpServers`, which no requirement asks the check to read.
