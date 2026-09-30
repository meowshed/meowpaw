---
id: TSK-2701
artifact: task
status: approved
revised: 2026-09-30
epic: EPC-1650
closes: [REQ-2972, REQ-2976]
issue: 660
projected: c46ec446735d
---

# Write the delegation rules into the write skill, and the partial-output rule into the method skill

`meow-author:write` says knowledge ships as a skill and never as an agent,
says a delegated agent is no isolation boundary, and gives each of the six
agent fields its rule and reason. One task, one
branch, one pull request, one review.

**Amended by ADR-2300.** Criterion 5 names `prose` alone, since ADR-2300 removed `record-reviewer`. Criteria 2 and 3 are dropped: the method skill reviews no record, so it has no rule for a review that stopped at its ceiling, and the case that exercised one is removed. Its verbs criterion is closed by the pull request's gate, since no run output is kept, and it names the checks unit `meow-checks`.

## Acceptance criteria

1. Given `plugins/meow-author/skills/write/SKILL.md`, when it is read, then
   it holds a rule that knowledge ships as a skill and never as an agent, a
   rule that no text treats a delegated agent as an isolation boundary, one
   rule for each of `maxTurns`, `tools`, `model`, `effort`, `omitClaudeMd`
   and `skills` with its reason, and a rule that a dispatcher reads an output
   marked partial as unfinished. Closed by: a fixture in
   `plugins/meow-author/tests/test_author.py`, class `WriteSkill`, that finds
   each rule, and the `prompts` check in the gate, which holds its tags.
2. Dropped by ADR-2300: the method skill dispatches no reviewer of a record,
   so it holds no rule for one that stopped at its ceiling.
3. Dropped by ADR-2300: the hand-run case for the ceiling dispatched the
   record reviewer, and both are removed.
4. Given a hand-run `meow-author` case under `plugins/meow-author/evals/`
   that asks for an agent carrying a language's idioms, when a person runs
   it, then the write skill produces a skill and no agent. Closed by:
   judgement, because a model's output is read by a person; the task's
   Evidence names who read the run.
5. Given the updated SPC-1030, SPC-1090 and write skill, when
   `meow-prose:prose` is dispatched
   with a path alone, then it doesn't report a sentence treating a delegated
   agent as a boundary. Closed by: judgement, because REQ-2976 names an agent
   as its verifier; the task's evidence names `prose` as the judge, and a
   person reads its report before the task closes, because the agent
   may share the author's model family.
6. Given this change's tree, when `meow-checks run format lint test` runs,
   then each passes. Closed by: each verb's outcome in the task's pull request.

## What to do

Add to `meow-author:write` the rules ADR-1700 lists under what the write
skill gains, each with the reason the decision gives, following the skill's
own form. The rules for the six fields state why each is written out, and
match the table in SPC-1030 under "What an agent declares".

Add the hand-run case for knowledge under `plugins/meow-author/evals/`, with
a `prompt.md`, graders and a line in the unit's `thresholds.toml`. A person
runs it; it never runs in CI.

Raise `meow-author`'s and `meow-flow`'s patch versions, because both skills
gain rules and no capability, and match each README's `describes:`. If
TSK-2700 lands first, take the next version above the one it set.

## Depends on

Nothing. ADR-1700 and EPC-1650 are approved, and the rules state reasons
that hold whether or not TSK-2700's check has landed.

## Evidence

`meow-author:write` gains the rules D1 to D9 under `<rules name="agents and
delegation">`. D1 ships knowledge, such as a language's idioms, as a skill and
never as an agent (REQ-2972). D2 forbids describing a delegated agent as a
boundary, because it runs under the parent's sandbox configuration
(REQ-2976). D3 to D8 give each of the six fields its rule and reason, matching
SPC-1030's table, and D9 reads an output marked partial as unfinished. The
method skill gains M23 beside M22, and its core stays within `budget.toml`.
The hand-run cases are `plugins/meow-flow/evals/stopped-at-the-ceiling/` and
`plugins/meow-author/evals/knowledge-as-a-skill/`, each with its line in
`thresholds.toml`. `meow-author` goes to 0.4.1 and `meow-flow` to 0.39.3,
one patch above the versions TSK-2700 set.

Criteria 1, 2 and 6 are met. The checks in `Cover` failed first and pass now,
`timeout 500 mise run all` exits 0, and `meow-verbs evidence --keep format
lint check test build` keeps a passing run of each verb at this change's
tree, as the pull request cites.

Criteria 3, 4 and 5 are open. Nobody has run either hand-run case, and
neither `meow-prose:prose` nor `meow-flow:record-reviewer` has read the
updated SPC-1030, SPC-1090 and write skill, so no transcript and no report is
kept and no person has read one. The fixtures read the rules' wording and not
whether a model follows them, so they stand in for none of the three. The
task stays open until a person runs the two cases and the two judges and
keeps what they print.

## Left alone

`crates/meow/src/author.rs` and the two shipped agents, which TSK-2700
changes. The session's nesting depth, REQ-3271, which ADR-1700 postpones.
The user-facing pages beyond each README's `describes`, which the implement step updates in the same pull request.
