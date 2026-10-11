---
id: TSK-5490
artifact: task
status: approved
revised: 2026-10-11
bug: BUG-1630
closes: []
issue:
---

# Carry the style into Pi's bundled copy, and hold the copy to the source

`packages/meow-core/prompts/reply-shape.md` carries the style
`plugins/meow-core/output-styles/meow.md` ships, held equal by a check that
allows only the platform's path phrasing. One task, one branch, one pull
request, one review: the tests first, then the change, its documentation and
its marks.

## Acceptance criteria

1. Given the bundled copy and the style, when
   `tools/test_pi_extensions.py` compares them, then they are equal where the
   copy's R10 names the package's own file in place of
   `${CLAUDE_PLUGIN_ROOT}/output-styles/meow.md`, and equal nowhere else.
   Closed by: `tools/test_pi_extensions.py`, seen failing first (BUG-1630).
2. Given this change's tree, when `meow-checks run format lint check test
   build` runs, then each passes. Closed by: each verb's outcome in the task's
   pull request.

## What to do

Copy the style over the bundled copy, adapting only the R10 path phrase, and
let the check normalise that phrase before it compares. Every later change to
the style fails the check until the copy moves with it.

## Depends on

Nothing.

## Left alone

The kernel extension's injection itself, which REQ-4108's task closed and
this defect doesn't touch.

## Evidence

Not yet.