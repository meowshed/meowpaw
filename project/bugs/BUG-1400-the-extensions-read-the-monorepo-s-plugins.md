---
id: BUG-1400
artifact: bug
status: approved
severity: major
violates: REQ-4108, REQ-4110, REQ-4112, REQ-4116
enters: implement
found: 2026-10-04
revised: 2026-10-04
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Pi extensions read the monorepo's plugins directory

Every Pi package extension shipped in EPC-2700 loads its prompt files through
a path that walks up to this repository's `plugins/` directory:
`join(packageRoot, "..", "..", "plugins", plugin, ...)`. That path holds only
in a checkout of the meowpaw monorepo. After `pi install`, the package sits in
Pi's own package directory with no `plugins/` beside it, so every read fails
and the extension silently runs with empty strings.

## Expected

`@meowshed/meow-core`, installed on its own, injects the reply shape
(REQ-4108) and holds the prose gate's two-judge call with its judge prompt
(REQ-4116). `@meowshed/meow-flow` loads the router's prompt for its nested
call (REQ-4110) and carries the reply shape into it (REQ-4112).

## Actual

`grep -n 'readPluginFile' packages/*/extensions/*.ts` in the tree at
`84f8ee63` shows every prompt load going through `readPluginFile`, which
resolves `packages/<name>/../../plugins/<plugin>/...`. Installed alone in
`~/.pi/agent/packages/`, the read throws ENOENT, the catch returns an empty
string, and:

- `before_agent_start` pushes an empty string into guidelines, so the reply
  shape never reaches the model;
- the prose gate's judge runs with no prompt, so the two-judge call returns
  nothing and blocks nothing;
- the router tool answers "Router unavailable" for every request.

The TSK-5201 and TSK-5202 acceptance criteria named manual session tests that
were never run against an installed package; the packages were marked done
from a monorepo checkout where the path accidentally holds.

## Reproduction

1. `cd packages/meow-core && node -e "const {readFile}=require('fs/promises'); readFile('../.. /plugins/meow-core/output-styles/meow.md'.replace(' ',''),'utf8').then(()=>console.log('holds in monorepo')).catch(e=>console.log(e.code))"` — `holds in monorepo`.
2. `pi install ./packages/meow-core`, then in a Pi session run any request:
   the reply shape's rules do not shape the reply, because the extension
   pushed an empty string.
3. `ls "$(pi list --json | jq -r '.[0].path')"` shows no `plugins/` directory
   beside the installed package.

## Environment

Pi 1.0.2 on macOS 15 (aarch64); meowpaw at `84f8ee63`; package
`@meowshed/meow-core` 0.4.0 and `@meowshed/meow-flow` 0.47.0 as shipped by
EPC-2700.
