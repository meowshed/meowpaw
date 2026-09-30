---
id: TSK-3510
artifact: task
status: approved
revised: 2026-09-29
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

## Evidence

Closes REQ-0330, REQ-0332, REQ-0336 and REQ-0340 as far as the skill states
them. Criteria 1 to 3 pass. Criteria 4, 8 and 9 pass on both models.
Criteria 5 and 6 pass on Sonnet 5 and not on Opus 5.5, and criterion 7 passes
on neither, so BUG-1360 records what they still lack.

Criteria 1 and 2. The cover commit added the checks, and
the run under #722, whose output is no longer kept, was their failing run: the `test` verb
exited 1 with `FAILED (failures=34)`, every failure in `RouteSkill` and
`RouteCases`. With the skill, the cases and the two names in place,
`python3 -m unittest plugins/meow-flow/tests/test_route.py -v` exits 0:

```text
Ran 9 tests in 63.010s

OK
```

`python3 -m unittest discover -s plugins/meow-flow/tests` exits 0 with
`Ran 227 tests` and `OK`.
`git diff 5107b5c9fc85bef01f5512b38a5e051cdaa437ec -- plugins/meow-flow/tests/test_route.py`
prints nothing, so the checks are the ones the cover commit wrote.

Criterion 3. `mise run budget` prints
`meow-flow: 958 of 960 characters on every turn`: the method skill's, the
route skill's and the router's descriptions. `budget.toml` states 960, under
the 1,000 ADR-2100 allows. The skill's description names the four override
words, because a resumed session that saw `route none` alone loaded no skill
and went to work.

Criteria 4 to 9. Each case is a `case.yaml` with a `scaffold.sh` that copies
the committed tree and commits it to a fresh repository, so each run starts
where `git status --porcelain` prints nothing. The cases for an override
after a route resume a `history.jsonl` in which the skill was loaded, the
router ran and its route was reported. The thresholds of 0.66 were committed
before the first run (REQ-0159). The report's checks are regular expressions
over the trace, because an `llm` grader with `focus: trace` reads only the
first 12 and last 12 events, which leaves out the report in a longer run.
`no-write-before-route` is the one grader every route case carries: it fails
where a Write, Edit, NotebookEdit or Bash call comes before the first
assistant text or tool result holding `size:` and a size.

I ran them by hand on 2026-09-29 with
`claude plugin eval plugins/meow-flow --case 'route-*' -j 4 --scaffold --ablation none --model <model> --judge-model claude-opus-5-5 --allow-tools Edit Write Bash`,
3 runs a case, Claude Code 2.1.283. Opus 5.5 judged both models, so the Opus
figures are a smoke check (REQ-3028). The runner loads only plugins under the
unit's directory from a case, so `meow-core` wasn't enabled, which the task
asked for. The final runs, at the revision this change lands:

| Case                         | Sonnet 5  | Opus 5.5  |
| ---------------------------- | --------- | --------- |
| `route-a-typo`               | 1.00      | 0.92      |
| `route-reported-ambiguous`   | 1.00      | 0.33      |
| `route-given`                | 0.79      | 0.58      |
| `route-overridden`           | 0.73      | 0.20      |
| `route-overridden-up`        | 0.73      | 1.00      |
| `route-reduced-unauthorised` | 0.73      | 0.00      |
| `route-list-overridden`      | 1.00      | 1.00      |
| `route-list-one`             | 1.00      | 0.17      |
| `route-a-question`           | 0.67      | 0.67      |
| `route-plain-words`          | 1.00      | 1.00      |
| `route-a-tiny-fix`           | 1.00      | 0.60      |
| `route-both-ways`            | 1.00      | 1.00      |
| `route-three-changes`        | 0.60      | 1.00      |
| Cost                         | USD 10.77 | USD 12.53 |

Sonnet 5's `route-three-changes` lost two runs to the runner's 300 s timeout,
and 0.60 is the one score under 0.66 on that model. Opus 5.5's
`route-a-tiny-fix` routed `reduced` twice, as TSK-3500's case does on a
request whose premise the code already meets.

Criterion 4: in every typo run on both models the router was the first
agent, the report came before the edit, and the typo was fixed. Criterion 8:
`route-a-question` dispatched no router and loaded no route skill in 3 of 3
runs on each model; its score is 0.67 because each run read files with Bash,
which the shared grader counts. Criterion 9: the route skill loaded in 3 of 3
`route-a-typo` runs and in 0 of 3 `route-a-question` runs on each model.
Criterion 7: `no-write-before-route` passed 30 of 36 runs on Sonnet 5 and 27
of 36 on Opus 5.5, `route-a-question` left out. Opus 5.5 went from the
router's reply, or the skill's load, to Bash or the method skill with no
report written, and two rewordings, a step saying to call no tool until the
report is written and a failing example of a route never shown, didn't move
it. BUG-1360 records it.

Two cases were added beyond the seven the task names, because a case resumes
one conversation and criterion 6 asks for two directions twice:
`route-overridden-up` gives `route full` after `none`, and `route-list-one`
gives `route one` after a list.

## Left alone

`plugins/meow-flow/templates/constitution.md`, which names no trivial work, so
it has no place to name the skill (ADR-2100). The router agent and its cases,
which TSK-3500 adds. The body of `plugins/meow-flow/README.md`, the root
`README.md` and `llms.txt`, which the document step updates once both tasks
are done. A hook refusing a write before
the route is reported, which ADR-2100 rejects until a hook reads the
conversation as it stands. Recording the route in the record, which ADR-2100
leaves unsettled.
