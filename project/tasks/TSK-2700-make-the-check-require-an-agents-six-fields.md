---
id: TSK-2700
artifact: task
status: approved
revised: 2026-09-30
epic: EPC-1650
closes: [REQ-2974, REQ-2982, REQ-2984, REQ-2988, REQ-3270]
issue: 659
projected: 6cc5c14f469e
---

# Make `meow-author check` require an agent's six fields, and declare them in both shipped agents

`meow-author check` fails an agent that leaves out `maxTurns`, `tools`,
`model`, `effort`, `omitClaudeMd` or `skills`, or holds a value SPC-1030's
table doesn't accept, and fails a shipped agent whose `tools` can delegate.
Each shipped agent declares all six in the same change, so the gate
stays green. One task, one branch, one pull request, one review.

**Amended by ADR-2300.** It names no `record-reviewer`, which ADR-2300 removed with its evaluation case, its gate criterion is closed by the pull request's gate, and What to do no longer adds that case.

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
   and each shipped agent declares the values in SPC-1030's table under
   "What an agent declares". Closed by: the gate's outcome in the task's
   pull request.
7. Dropped by ADR-2300: the case `review-without-delegating` exercised
   `record-reviewer`, and both are removed.

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

Give each shipped agent the values in SPC-1030's table.

Raise `meow-author`'s minor version, because the check fails agents it
passed before, and name the six fields and the reason for each in its README
and release notes. Raise `meow-flow`'s and `meow-prose`'s patch versions. Each
README's `describes:` matches its version.

## Depends on

Nothing. ADR-1700 and EPC-1650 are approved.

## Evidence

`agent_fields` in `crates/meow/src/author.rs` reads an agent's front matter
as YAML and fails, naming the file and the field, on each of the six fields
SPC-1030 states when it is missing or holds a value the table doesn't accept.
In a unit's `agents/` directory it also fails a `tools` list holding `*`,
`Agent` or `Task`, alone or with a restriction, read as a list or as a
comma-separated string. A unit counts as shipped when it sits in a `plugins/`
directory or carries a plugin manifest, so `.claude/` passes the `tools` rule
once it writes a list. Front matter that doesn't parse fails with the parser's
reason and runs no field rule. The `author` feature now builds with
`yaml-rust2`, which the `gotask` feature already uses.

`record-reviewer`, `router` and `prose` declare the values in SPC-1030's
table, and
`plugins/meow-flow/evals/review-without-delegating/` is the hand-run case for
criterion 7, with its threshold in `thresholds.toml`. Nobody has run it yet,
so criterion 7 is open until a person runs it and keeps the transcript.

The 26 checks in `AgentFields` failed first: the `test` verb exited 1, seen
in the run under #667, whose output is no longer kept, in the commit that held the checks
alone. They pass now, and `git diff 4aad79e -- plugins/meow-author/tests/test_author.py`
prints nothing:

```text
$ python3 -m unittest plugins/meow-author/tests/test_author.py
Ran 40 tests in 1.740s
OK                                   # exit 0
$ plugins/meow-author/bin/meow-author check
51 files, 0 authoring failures       # exit 0
```

`router` joined the harness in #669 after this task was written, so it gains
the six fields and a row in SPC-1030's table in this change; without them the
check fails it and the gate goes red. `ShippedAgents` passes once it has
both.

`meow-author` goes to 0.4.0, because the check fails agents it passed before,
and `meow-flow` to 0.39.2 and `meow-prose` to 0.4.1 for their agents'
declarations. `meow-verbs evidence --keep format lint check test build` exits
0 on this change's own tree, each result kept in `project/evidence/`, as the
pull request cites.

## Left alone

The write skill and the method skill, which TSK-2701 changes. This
repository's `prompts` task, which still runs `meow-author check` with no
path, so this repository's own `.claude/` agents stay unchecked, as ADR-1700
says under what still doesn't work. `permissionMode`, `hooks` and
`mcpServers`, which no requirement asks the check to read.
