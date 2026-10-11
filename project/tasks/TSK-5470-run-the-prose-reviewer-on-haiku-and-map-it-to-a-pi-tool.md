---
id: TSK-5470
artifact: task
status: approved
revised: 2026-10-11
realises: ADR-2950
closes: [REQ-4618]
issue:
---

# Run the prose reviewer on haiku and map it to a Pi tool

`plugins/meow-prose/agents/prose.md` runs on haiku, and `packages/meow-prose/`
registers the `meow-prose-review` tool, whose nested call carries the reply
shape and prefers glm 5.3 flash. One task, one branch, one pull request, one
review: the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given `plugins/meow-prose/agents/prose.md`, when its front matter is read,
   then `model:` names the haiku tier. Closed by:
   `tools/test_pi_extensions.py`, seen failing first.
2. Given `packages/meow-prose/extensions/prose.ts`, when the test reads it,
   then it registers `meow-prose-review`, reads the reply shape and the
   writing skill and its patterns file from the package, and prefers the model
   `MEOW_NESTED_MODEL` names, glm 5.3 flash where it names nothing. Closed
   by: the same test.
3. Given `packages/meow-prose/lib/models.mjs`, when node drives it with a
   stand-in registry, then a failing model is skipped, a string or block-list
   answer yields its text, and a catalogue where every model fails names the
   last failure with its provider and model. Closed by: the same test.
4. Given this change's tree, when `meow-checks run format lint check test
   build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

## What to do

Copy the nested-call module into each package that nests, generalised to the
preference the environment names: `packages/meow-prose/lib/models.mjs` beside
`meow-flow`'s, because REQ-4130 bundles every file an extension loads inside
its own package. The extension reads `skills/writing/SKILL.md` and
`skills/writing/patterns/en.md` and builds the review prompt from the agent's
role and the standard, because the nested call reads nothing. Raise
`@meowshed/meow-prose` and the `meow-prose` plugin to 0.7.0 together
(REQ-4614), and carry the README and the budget to both sides.

## Depends on

Nothing.

## Left alone

The prose gate's judge, which the gate binary spawns and the extension never
re-implements; the review the session performs from the writing skill, which
stays for a text the person reviews inline.

## Evidence

Not yet.