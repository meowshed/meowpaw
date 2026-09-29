---
id: TSK-3510
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-2000
closes: [REQ-0330, REQ-0332, REQ-0336, REQ-0340]
issue: 649
projected: efa38f29d8c2
---

# Add the route skill that routes a request before work starts and reports the route before any edit

`meow-flow` ships `skills/route/SKILL.md`, which dispatches the router before
any work on a request to change the repository, reports the route and its
reason before any tool that writes runs, proceeds or stops as the route says,
takes the four override words, and reports each of the seven states SPC-1090
lists as itself. The method skill and `CLAUDE.md` name it. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/route/SKILL.md`, when it is read, then it
   names `route none`, `route reduced`, `route full` and `route one`, and
   names `meow-flow:router` as the agent it dispatches. Closed by:
   `RouteSkill.test_the_skill_names_four_override_words` and
   `RouteSkill.test_the_skill_dispatches_the_router` in
   `plugins/meow-flow/tests/test_route.py`.
2. Given the method skill's first step and `CLAUDE.md`'s `own_method_first`,
   where it names trivial work, when each is read, then it names the `route`
   skill. Closed by:
   `RouteSkill.test_the_method_and_constitution_name_the_route`.
3. Given `meow-flow`, when the `budget` check runs, then it passes with the
   skill's and the agent's descriptions, within 1,000 characters. Closed by:
   `mise run budget` in the gate's output.
4. Given a request to fix a typo, when the session runs, then it routes
   `none`, reports the route and its reason before any tool that writes, and
   the router is the first agent it dispatches. Closed by: the case
   `route-a-typo` under `plugins/meow-flow/evals/`, scoring at least its
   threshold on Sonnet 5 and Opus 5.5 in a run by hand.
5. Given a request whose evidence points both ways, when the session runs,
   then its report says `ambiguous` and names the evidence on each side.
   Closed by: the case `route-reported-ambiguous`.
6. Given a request carrying `route none`, then no router is dispatched and the
   route is reported as given; given `route none` after a `full` route, and
   `route full` after a `none`, then each changes the route with no further
   question; given `route reduced` for new work no approved record
   authorises, then the report says `full`, the `reduced` given, and that no
   approved record authorises the work; given `route full` after a
   several-changes route, then the list stays with every entry `full`, and
   given `route one` after it, one change at the largest size among the
   entries. Closed by: the cases `route-given`, `route-overridden`,
   `route-reduced-unauthorised` and `route-list-overridden`.
7. Given every route case, when its stream is read, then no Write, Edit,
   NotebookEdit or Bash call comes before the route is reported, and each run
   starts in a scratch repository where `git status --porcelain` prints
   nothing. Closed by: a grader shared by every route case, including
   TSK-3500's.
8. Given a question in chat that changes nothing, when the session runs, then
   no router is dispatched. Closed by: the case `route-a-question`.
9. Given the skill's description, when the case `route-a-typo` runs, then the
   skill loads before what it says is measured (REQ-3032), beside near misses
   such as a question in chat. Closed by: the load measure the platform's eval
   runner reports for `route-a-typo` and `route-a-question`.

## What to do

Write `plugins/meow-flow/skills/route/SKILL.md` following `meow-author:write`,
with its description stating the obligation in the third person, as RES-0272
measured. It dispatches `meow-flow:router`, reads the reply fields the
router's definition states and nothing its brief adds, and behaves as
SPC-1090 "The route" and its failure paths give: the report comes first, the
skill proceeds with no question for `none`, `reduced` and `full`, hands a
defect to the method skill's defect path, and stops only on several changes.
An override applies to the request it answers, skips the dispatch when given
with the request, and a route in a subagent's brief counts as given.

Name the route as what comes before the chain's first step in
`plugins/meow-flow/skills/method/SKILL.md`, and name the skill where this
repository's `CLAUDE.md` names trivial work, in `own_method_first`.

Add `RouteSkill` to `plugins/meow-flow/tests/test_route.py`, and see its
tests fail before the skill exists. Add the cases `route-a-typo`,
`route-reported-ambiguous`, `route-given`, `route-overridden`,
`route-reduced-unauthorised`, `route-list-overridden` and `route-a-question`
under `plugins/meow-flow/evals/`, and the grader for criterion 7 shared by
every route case. Add each case to `evals/thresholds.toml` before its first
run (REQ-0159). Every case runs with `meow-core` enabled.

Raise `permanent_characters` in `budget.toml` to what the budget check
measures, at most 1,000, and `meow-flow`'s minor version in `plugin.json`,
with its README's `describes` to match.

## Depends on

- TSK-3500 (blocking): the skill dispatches the router and reads the reply
  fields its definition states, and every case here runs the router.

## Cover

- Checks: plugins/meow-flow/tests/test_route.py
- Failing run: project/evidence/ed1d8795487d.txt
- Landed in: not yet
- Judgement: 3: the existing budget check closes it, and it passes before the skill exists, so no failing run can be kept for it; 4: the case runs a model session, by hand on Sonnet 5 and Opus 5.5 and never in the gate; 5: the case runs a model session, by hand on Sonnet 5 and Opus 5.5 and never in the gate; 6: the cases run a model session, by hand on Sonnet 5 and Opus 5.5 and never in the gate; 8: the case runs a model session, by hand on Sonnet 5 and Opus 5.5 and never in the gate; 7: whether a stream shows a write before the route is reported is read from a model's run, by hand; 9: the load measure comes from the platform's eval runner on a model, by hand

The checks are the classes `RouteSkill` and `RouteCases`, each naming its
criterion and requirement in its docstring. Criterion 1 is checked by
`RouteSkill.test_the_skill_names_four_override_words` and
`RouteSkill.test_the_skill_dispatches_the_router`, and criterion 2 by
`RouteSkill.test_the_method_and_constitution_name_the_route`. The static half
of criteria 4, 5, 6 and 8 is `RouteCases.test_each_skill_case_has_a_threshold`:
each case exists, names itself and carries its threshold before its first run
(REQ-0159). The static half of criterion 7 is
`RouteCases.test_every_route_case_shares_the_write_grader`, one grader naming
Write, Edit, NotebookEdit and Bash, the same in every route case including
TSK-3500's, and `RouteCases.test_every_route_case_starts_in_a_clean_repository`,
which runs each case's scaffold in an empty directory and expects a git
repository where `git status --porcelain` prints nothing. The kept run fails 34
subtests, all of them these: the skill and the seven cases don't exist, the
method skill and `CLAUDE.md` don't name the route skill, no route case carries
the grader, and TSK-3500's four scaffolds extract a tree with no repository.

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

`plugins/meow-flow/templates/constitution.md`, which names no trivial work, so
it has no place to name the skill (ADR-2100). The router agent and its cases,
which TSK-3500 adds. The body of `plugins/meow-flow/README.md`, the root
`README.md` and `llms.txt`, which the document step updates once both tasks
are done. A hook refusing a write before
the route is reported, which ADR-2100 rejects until a hook reads the
conversation as it stands. Recording the route in the record, which ADR-2100
leaves unsettled.
