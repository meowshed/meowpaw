---
id: TSK-2701
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1650
closes: [REQ-2972, REQ-2976]
issue:
---

# Write the delegation rules into the write skill, and the partial-output rule into the method skill

`meow-author:write` says knowledge ships as a skill and never as an agent,
says a delegated agent is no isolation boundary, and gives each of the six
agent fields its rule and reason. The method skill reports a record whose
review stopped at its turn ceiling as unreviewed by an agent. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-author/skills/write/SKILL.md`, when it is read, then
   it holds a rule that knowledge ships as a skill and never as an agent, a
   rule that no text treats a delegated agent as an isolation boundary, one
   rule for each of `maxTurns`, `tools`, `model`, `effort`, `omitClaudeMd`
   and `skills` with its reason, and a rule that a dispatcher reads an output
   marked partial as unfinished. Closed by: a fixture in
   `plugins/meow-author/tests/test_author.py`, class `WriteSkill`, that finds
   each rule, and the `prompts` check in the gate, which holds its tags.
2. Given `plugins/meow-flow/skills/method/SKILL.md`, then a rule beside M22
   says a review whose output is marked as stopped at its ceiling leaves the
   record unreviewed by an agent. Closed by:
   `MethodSkill.test_a_partial_review_is_unreviewed` in
   `plugins/meow-flow/tests/test_record.py`.
3. Given a hand-run case that dispatches an agent defined with `maxTurns: 2`
   on work that needs more, when a person runs it, then its output comes back
   marked as stopped at its ceiling. Closed by: judgement, because the
   marking is the platform's behaviour, observed in a hand-run transcript that
   never runs in CI.
4. Given a hand-run `meow-author` case under `plugins/meow-author/evals/`
   that asks for an agent carrying a language's idioms, when a person runs
   it, then the write skill produces a skill and no agent. Closed by:
   judgement, because a model's output is read by a person, and the kept
   transcript is the evidence.
5. Given the updated SPC-1030, SPC-1090 and write skill, when
   `meow-prose:prose` and `meow-flow:record-reviewer` are each dispatched
   with a path alone, then neither reports a sentence treating a delegated
   agent as a boundary. Closed by: judgement, because REQ-2976 names an agent
   as its verifier; the task's evidence names both agents as the judge, and a
   person reads both reports before the task closes, because the two agents
   may share the author's model family.
6. Given this change's tree, when `meow-verbs run format lint test` runs,
   then each passes. Closed by: the kept evidence of that run.

## What to do

Add to `meow-author:write` the rules ADR-1700 lists under what the write
skill gains, each with the reason the decision gives, following the skill's
own form. The rules for the six fields state why each is written out, and
match the table in SPC-1030 under "What an agent declares".

Add to the method skill a rule beside M22 that a review whose output comes
back marked as stopped at the agent's ceiling is reported as unreviewed by an
agent, as SPC-1090 states under "The review before a gate". Keep the method
skill's core within `budget.toml`.

Add the hand-run case for the ceiling under `plugins/meow-flow/evals/`, with
a fixture agent defined with `maxTurns: 2`, and the case for knowledge under
`plugins/meow-author/evals/`, each with a `prompt.md`, graders and a line in
its unit's `thresholds.toml`. A person runs them; neither runs in CI.

Raise `meow-author`'s and `meow-flow`'s patch versions, because both skills
gain rules and no capability, and match each README's `describes:`. If
TSK-2700 lands first, take the next version above the one it set.

## Depends on

Nothing. ADR-1700 and EPC-1650 are approved, and the rules state reasons
that hold whether or not TSK-2700's check has landed.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

`crates/meow/src/author.rs` and the two shipped agents, which TSK-2700
changes. The session's nesting depth, REQ-3271, which ADR-1700 postpones.
The user-facing pages beyond each README's `describes`, which the document
step updates.
