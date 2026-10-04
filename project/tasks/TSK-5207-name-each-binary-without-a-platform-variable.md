---
id: TSK-5207
artifact: task
status: approved
revised: 2026-10-04
realises: ADR-2790
fixes: [BUG-1401]
closes: [REQ-4132, REQ-4102, REQ-4110, REQ-4112]
---

# Name each binary without a platform variable

Every skill in every Pi package names its unit's binary by its plain
command and its supporting files relative to the skill's own directory, and
every package extension puts its bin directory on PATH. The method
extension's router call loads its prompt from the package's own
`prompts/` directory.

## Acceptance criteria

1. Given the Pi packages as shipped, when a skill's text is searched for
   `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`, then nothing matches.
   Closed by: `grep -r 'CLAUDE_SKILL_DIR\|CLAUDE_PLUGIN_ROOT' packages/`
   reporting no match.
2. Given `@meowshed/meow-flow` installed, when a Pi session runs the method
   skill's step 3, then `paw ready research` resolves and runs. Closed by:
   a session test on an installed copy.
3. Given the method extension's router tool, when it is invoked, then the
   router prompt loads from the package's own prompts directory and the
   reply shape travels into the nested call. Closed by: reading the
   extension source for the prompts path and a session dispatch.
4. Given the method extension and the kernel installed together, when a
   session starts, then no second copy of the reply shape is injected by
   the method extension. Closed by: counting the shape in the system
   prompt.
