---
id: TSK-5480
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2950
closes: [REQ-3526]
issue:
---

# Run the research step as a cheap subagent

The research step dispatches a researcher on the cheap tier — haiku on Claude
Code, glm on Pi — and the session writes the artifact and runs the checks. One
task, one branch, one pull request, one review: the tests first, then the
change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-flow/agents/researcher.md`, when its front matter is
   read, then `model:` names the haiku tier and its tools name no write tool.
   Closed by: `tools/test_pi_extensions.py`, seen failing first.
2. Given `plugins/meow-flow/skills/method/steps/research.md`, when the test
   reads it, then it states the dispatch and the write-back: the session
   allocates the identifier, dispatches the researcher with the question and
   the sources, writes the artifact from `paw template research` and runs
   `paw check`. Closed by: the same test.
3. Given `packages/meow-flow/extensions/flow.ts`, when the test reads it, then
   it registers `meow-research`, whose nested call prefers the model
   `MEOW_NESTED_MODEL` names, glm 5.3 flash where it names nothing, and carries
   the record template the session passes. Closed by: the same test.
4. Given this change's tree, when `meow-checks run format lint check test
   build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

## What to do

The researcher agent reads the primary sources with Read, Grep, Glob and
WebFetch and returns the draft; the session writes the file, fills the front
matter from `paw new research` and the template, and runs `paw check`. On Pi
the session gathers the material — the template, the `paw find` results and
the sources' text — into the call, because a nested call reads nothing. State
both in the step, and name the cheap tier in the agent's front matter.

## Depends on

Nothing.

## Left alone

The requirements step and every later step, which run in the session until a
decision says otherwise (ADR-2950, "What this does not settle"), and the
research record's gate, which stays the person's.

## Evidence

Not yet.