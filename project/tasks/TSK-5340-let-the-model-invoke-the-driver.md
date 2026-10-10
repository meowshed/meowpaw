---
id: TSK-5340
artifact: task
status: done
revised: 2026-10-10
bug: BUG-1540
closes: [REQ-4900, REQ-4902]
issue: 918
projected: 83d3932122b3
tracked: e2cb23623f62
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Let the model invoke the driver, and count its description in the budget

The `run` skill of `meow-flow` carries no `disable-model-invocation`, and the
unit's budget states what its description now loads.

## Acceptance criteria

1. Given `plugins/meow-flow/skills/run/SKILL.md`, when its front matter is
   read, then it has no `disable-model-invocation` field. Closed by: a
   `grep` for the field in the file exiting 1.
2. Given the unit's `budget.toml`, when `mise run budget` runs, then it exits
   0 with the driver's description counted. Closed by: the command's output.
3. Given `packages/meow-flow/skills/run/SKILL.md`, when it is compared with
   the plugin's copy, then the two match. Closed by: `diff` exiting 0.

## What to do

Remove the field from the skill and from its mirror, raise
`permanent_characters` to the figure `mise run budget` measures and update the
comment above it, and cite REQ-4900 in SPC-1030 in place of REQ-2680. Keep the
skill's attended rule as it stands.

## Depends on

Nothing.

## Evidence

1. `grep -q disable-model-invocation plugins/meow-flow/skills/run/SKILL.md`
   exits 1, so the field is absent.
2. `mise run budget` exits 0 and reports `meow-flow: 903 of 910 characters on
every turn`.
3. The two skill files differ only in the launcher path the mirror leaves out
   (`${CLAUDE_SKILL_DIR}/../../bin/paw` against `paw`), as before the change.
   A `diff` with that prefix removed exits 0.

`paw check` reports no finding. The gate's other failures, `test-author` (2),
`test-flow` (1) and `test-gotask` (3), are missing-binary tests that fail on
`main` as well. The pull request is #891.

## Left alone

`plugins/meow-loop/skills/run/SKILL.md` keeps its flag, because only a person
may start a run (REQ-0894).
