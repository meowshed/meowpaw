---
id: TSK-2701
artifact: task
status: approved
revised: 2026-09-29
epic: EPC-1650
closes: [REQ-2972, REQ-2976]
issue: 660
projected: c46ec446735d
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

- Checks: plugins/meow-author/tests/test_author.py plugins/meow-flow/tests/test_record.py
- Failing run: project/evidence/7e8fcf9d28fb.txt project/evidence/0470c7ed88ab.txt project/evidence/27b2d5b8f16b.txt
- Landed in: #686
- Judgement: 3: the platform writes the partial marking, and only a hand-run transcript shows it; 4: a person reads the model's output in the kept transcript; 5: REQ-2976 names an agent as its verifier, and a person reads both reports; 6: the kept run of `format lint test` at implement closes it

Criterion 1 is covered by the class `WriteSkill` in `test_author.py`:
`test_knowledge_ships_as_a_skill_and_never_as_an_agent`,
`test_a_delegated_agent_is_no_isolation_boundary`,
`test_each_of_the_six_fields_has_its_rule` and
`test_a_partial_output_is_unfinished`. The `prompts` check in the gate holds
the tags. Criterion 2 is covered by
`MethodSkill.test_a_partial_review_is_unreviewed` in `test_record.py`.

The two runs are kept because the `test` verb stops at the first unit that
fails. In `7e8fcf9d28fb.txt`, criterion 2's check fails and the verb stops
before `meow-author`'s tests. `0470c7ed88ab.txt` comes from a tree holding
criterion 1's checks alone, where its four checks report nine failures.

A skeptic found that the fixtures for REQ-2972 and REQ-2976 matched words, so
a rule saying the opposite passed them. `WriteSkill` now requires "as a
skill" before "never as an agent", and a negation before "boundary", and
`test_the_knowledge_rule_refuses_its_inversion` and
`test_the_boundary_rule_refuses_its_inversion` feed each pattern two inverted
rules and require a refusal. `27b2d5b8f16b.txt` is the `test` verb exiting 1
with four failures, one for each inverted rule, against the patterns that
matched words, in commit f429d11, which holds the two fixtures alone.

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
The user-facing pages beyond each README's `describes`, which the document
step updates.
