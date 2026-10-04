---
id: TSK-5207
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2710
closes: [REQ-4110, REQ-4112, REQ-4132]
issue: 849
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Name each binary without a platform variable

Every skill in every Pi package names its unit's binary by its plain command
and its supporting files relative to the skill's own directory, every
package extension puts its bin directory on PATH, and the method extension's
router loads its prompt from the package's own `prompts/` directory. Fixes
BUG-1401.

## Acceptance criteria

1. Given the Pi packages as shipped, when their text is searched for
   `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`, then nothing matches.
   Closed by: `grep -r 'CLAUDE_SKILL_DIR\|CLAUDE_PLUGIN_ROOT' packages/`
   reporting no match.
2. Given `@meowshed/meow-flow` installed, when a Pi session runs the method
   skill's step 3, then `paw ready research` resolves and runs. Closed by: a
   session test on an installed copy answering ready.
3. Given the method extension's router tool, when it is invoked, then the
   router prompt loads from the package's own prompts directory and the
   reply shape travels into the nested call as its system prompt. Closed
   by: reading the extension for the prompts path and the nested call's
   shape.
4. Given the method extension and the kernel installed together, when a
   session starts, then no second copy of the reply shape is injected by
   the method extension. Closed by: reading `method.ts` for the absence of
   a `promptGuidelines` push.

## What to do

Replace `${CLAUDE_SKILL_DIR}/../../bin/<unit>` with the plain command and
`${CLAUDE_SKILL_DIR}/<file>` with the skill-relative path in every package
skill; drop the `${CLAUDE_PLUGIN_ROOT}` path from the loop skill's start
command and the write skill's B6; keep the plugins' copies untouched.
Prepend each package's `bin/` to `process.env.PATH` in its extension's
factory.

## Depends on

- TSK-5206 (not blocking): the two share the PATH mechanism, which either
  task can land first; this task needs no artifact from it.

## Evidence

`paw check` reports no finding; the repository gate passes.
`grep -r 'CLAUDE_SKILL_DIR\|CLAUDE_PLUGIN_ROOT' packages/` reports no
match; a Pi session with `packages/meow-flow` installed in `/tmp` runs the
method skill's step 3 and answers `paw ready research: ready; research
needs no approved input`; the same session's `meow-loop start` is blocked
with the loop guard's reason relayed, proving the guards and the router's
prompt load; `method.ts` pushes nothing into `promptGuidelines`, so the
kernel's injection stands alone.

## Left alone

The plugins' skills, unchanged, because a released unit's prompt rewording
is a release of its own; the commands the extension registers, which load
skills by name and change nothing here.
