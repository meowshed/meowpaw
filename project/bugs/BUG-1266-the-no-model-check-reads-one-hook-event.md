---
id: BUG-1266
artifact: bug
status: approved
severity: minor
violates: REQ-2076
enters: cover
found: 2026-09-29
revised: 2026-09-29
issue: 715
---

# The prose gate's no-model check reads the `PreToolUse` hooks only

`TheHook.test_no_hook_is_a_prompt` in
`plugins/meow-prose-gate/tests/test_gate.py` collects the hook types from
`hooks["hooks"]["PreToolUse"]` alone. So a `prompt` hook added under `Stop`,
or under any other event, passes the check, and a model could judge the
unit's texts again with every check green. EPC-1590's verification says the
check fails on a file holding one `prompt` hook, which holds only for that one
event.

## Reproduction

`main` after #713, with `meow-prose-gate` 0.2.0, on macOS on arm64.

1. Load `plugins/meow-prose-gate/hooks/hooks.json` and add
   `"Stop": [{"hooks": [{"type": "prompt", "prompt": "Check the prose."}]}]`
   under `hooks`.
2. Evaluate the check's expression on it:
   `set(hook["type"] for group in hooks["hooks"]["PreToolUse"] for hook in group["hooks"]) == {"command"}`.

## What the system does

The expression prints `True`, so the test would pass on a `hooks.json` that
runs a model on every stop.

## What it should do, and why

The check should collect the type of every hook under every event in
`hooks.json` and fail on any type other than `command`. REQ-2076 forbids
checking by evaluation what a program can check, and ADR-1600 chose a program
for that reason. A check that reads one event keeps that choice for one event.

## Triage

It enters at cover, because REQ-2076 and ADR-1600 are right and the program
holds them today: the check misses what they ask. Minor, because
`hooks.json` holds no model hook now, and only the guard against one coming
back is missing.

## Closed by

The reproduction as fixtures in the class `TheHook` in
`plugins/meow-prose-gate/tests/test_gate.py`: the check's reading applied to a
`hooks.json` with a `prompt` hook under `Stop` and one with an `agent` hook
under `PostToolUse`, each refused, and the shipped `hooks.json` accepted.

## Tasks

- [x] T-001 TSK-2576 read the type of every hook under every event, in
      `plugins/meow-prose-gate/tests/test_gate.py`
      evidence: 2 checks seen failing first, 33 `meow-prose-gate` fixtures
      passing, in #717.
