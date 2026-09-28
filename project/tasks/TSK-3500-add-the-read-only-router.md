---
id: TSK-3500
artifact: task
status: approved
revised: 2026-09-28
epic: EPC-2000
closes: [REQ-0334, REQ-0338, REQ-0342, REQ-0344, REQ-0346]
issue: 648
projected: 3ce6cbc42e07
---

# Add the read-only router agent that routes a request on the repository

`meow-flow` ships `agents/router.md`, an agent that holds `Read`, `Grep` and
`Glob` and nothing else, reads a request with the repository, and replies with
a size, a shape, a reason naming what it read, whether the evidence was
ambiguous and the override words. The `route` skill that dispatches it is
TSK-3510's. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given `plugins/meow-flow/agents/router.md`, when its front matter is read,
   then `tools` names exactly `Read`, `Grep` and `Glob`; given a copy that adds
   `Write`, `Edit` or `Bash`, or drops `tools`, the same assertion fails.
   Closed by: `RouterAgent.test_tools_are_read_grep_glob` and
   `RouterAgent.test_a_writing_copy_fails` in
   `plugins/meow-flow/tests/test_route.py`.
2. Given the router's prompt, when it is read, then it names the sizes `none`,
   `reduced` and `full`, the four shapes including several changes, and the
   reply fields size, shape, reason, ambiguous and override words. Closed by:
   `RouterAgent.test_the_prompt_names_sizes_shapes_and_fields`.
3. Given Claude Code at the version `plugins/meow-flow/requires.toml` states,
   when the router is dispatched in the foreground from `claude -p` and asked
   to create a file, then it reports no tool that writes and
   `git status --porcelain` prints nothing; with `Write` added to a copy, the
   same brief creates the file. Closed by: the kept run of both dispatches,
   and `requires.toml` naming that version as the one the allowlist was last
   observed on. Judgement for whether the reply reads as a refusal, because
   the model's words vary between runs.
4. Given a request in plain words for verbs to read tasks from a task runner,
   and one calling a change to how the profile is parsed a tiny fix, when the
   router is dispatched on this repository's tree, then each reply routes
   `full` and its reason names a path or an identifier in the repository.
   Closed by: the cases `route-plain-words` and `route-a-tiny-fix` under
   `plugins/meow-flow/evals/`, scoring at least their thresholds on Sonnet 5
   and Opus 5.5 in a run by hand.
5. Given a request whose evidence points to two sizes, when the router is
   dispatched, then it replies with the larger size, `ambiguous`, and the
   evidence on each side. Closed by: the case `route-both-ways`.
6. Given a request for three unrelated changes, when the router is
   dispatched, then it replies with three entries, each with its size and
   shape. Closed by: the case `route-three-changes`.
7. Given `meow-flow`, when the `budget` check runs, then it passes with the
   agent's description counted. Closed by: `mise run budget` in the gate's
   output.

## What to do

Write `plugins/meow-flow/agents/router.md` following `meow-author:write`, with
`tools: Read, Grep, Glob`. Its prompt states the three sizes, the four shapes
and the reply fields as SPC-1090 "The route" gives them, because the skill
reads those fields and nothing its brief adds. It tells the router to read
`.meowpaw/profile.toml`, the record's indexes and specifications where the
profile declares a record, and the files the request would touch, to name at
least one of them in its reason, and to take the larger size where the
evidence points to two. The agent inherits the session's model.

Write `plugins/meow-flow/tests/test_route.py` with the class `RouterAgent`,
and see its tests fail before the agent exists.

Repeat RES-0304's dispatch and its control on the version `requires.toml`
states, keep both runs with `meow-verbs evidence --keep`, and record in
`requires.toml` the version on which the allowlist was last observed.

Add the cases `route-plain-words`, `route-a-tiny-fix`, `route-both-ways` and
`route-three-changes` under `plugins/meow-flow/evals/`, each prompt asking the
session to dispatch `meow-flow:router` on the request and report its reply,
with graders for the criterion each closes. Add each case to
`evals/thresholds.toml` before its first run (REQ-0159), and record each run's
time and cost. Every case runs with `meow-core` enabled, so the router's brief
carries the output style's block.

Raise the unit's `permanent_characters` in `budget.toml` to what the budget
check measures, and no further than 1,000. Raise `meow-flow`'s minor version
in `plugin.json`, and its README's `describes` to match.

## Depends on

Nothing: the agent stands alone, and the route skill is the one that needs it.

## Cover

Not yet.

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The `route` skill, the method skill, the constitution template and
`CLAUDE.md`, which TSK-3510 changes. The body of `plugins/meow-flow/README.md`,
the root `README.md` and `llms.txt`, which the document step updates once both
tasks are done. The model the router runs on, which ADR-2100 leaves to the
session until an evaluation shows a smaller model routes as well.
