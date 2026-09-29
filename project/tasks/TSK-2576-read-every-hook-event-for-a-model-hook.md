---
id: TSK-2576
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1266
closes: []
issue: 715
---

# Refuse a model hook under any event of the prose gate's hooks

Make the check that the prose gate runs no model read the type of every hook
under every event in `plugins/meow-prose-gate/hooks/hooks.json`, so a `prompt`
or `agent` hook fails the check wherever it is added. One task, one branch,
one pull request, one review.

## Acceptance criteria

1. Given a `hooks.json` holding the shipped hooks and a `prompt` hook under
   `Stop`, when the check reads it, then it names that hook's type as one
   other than `command`. Closed by:
   `TheHook.test_a_prompt_hook_under_any_event_is_refused` in
   `plugins/meow-prose-gate/tests/test_gate.py`.
2. Given a `hooks.json` holding the shipped hooks and an `agent` hook under
   `PostToolUse`, when the check reads it, then it names that hook's type.
   Closed by: `TheHook.test_an_agent_hook_under_any_event_is_refused`.
3. Given the shipped `hooks.json`, when the check reads it, then every type it
   collects is `command`. Closed by: `TheHook.test_no_hook_is_a_prompt`.

## What to do

Give `TheHook` one function that collects the type of each hook under each
event in a loaded `hooks.json`, and have the three tests use it. Write the two
refusing tests first, in a commit of their own, against the reading the check
has now, and keep their run as the failing run. Change no file the unit ships,
so `meow-prose-gate` keeps its version.

## Depends on

Nothing. BUG-1266 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet.

## Left alone

Whether a `command` hook itself calls a model: no program can read that from
`hooks.json`, and the hook's command names the unit's own launcher, which the
other fixtures run.
