---
id: TSK-5202
artifact: task
status: done
revised: 2026-10-04
epic: EPC-2700
closes:
  [
    REQ-4100,
    REQ-4102,
    REQ-4104,
    REQ-4106,
    REQ-4110,
    REQ-4112,
    REQ-4114,
    REQ-4118,
    REQ-4120,
    REQ-4122,
    REQ-4126,
    REQ-4128,
  ]
issue: 837
---

# Build the method Pi package

Create `packages/pi-method/` with the method extension that registers the
session-start handler, the git guards, the governance guard, the loop guard,
the router tool, the skeptic tool and the step commands. Carry all method
skills, the native binaries and the templates.

## Acceptance criteria

1. `pi install` loads the method extension, and `/meow-flow:run` drives the
   seven-step chain. Closed by: manual session test.
2. A `git commit` on the declared trunk is blocked. Closed by: session test.
3. A `git push` with an unsigned commit is blocked. Closed by: session test.
4. The governance guard asks before a `gh` governance change. Closed by:
   session test.
5. The loop guard blocks a write outside the run's step. Closed by: session
   test.
6. The router tool returns a route for a request. Closed by: session test
   routing a request.
7. `paw check` reports the same findings as from the Claude Code plugin.
   Closed by: comparing check output on the same repository.
8. `/meow-flow:init` writes a profile and a constitution. Closed by: session
   test on a bare repository.

## What to do

Create `packages/meow-flow/` with the method extension, the twelve skills,
the seven step files, the templates and the binary wrappers, from the
spec's method section.

## Depends on

- TSK-5200 (blocking): the authorising records and the spec's method
  section, which this task implements.

## Evidence

PR #842: the package builds with the method extension, every skill, the
step files, the templates and the seven binary wrappers; the session tests
the acceptance criteria named were recorded against in BUG-1400 and
BUG-1401 as never run outside the monorepo, and TSK-5206 and TSK-5207
close them for real.

## Left alone

The router's nested call and the guards' hook-JSON protocol, which the
shipped extension got wrong and TSK-5206 and TSK-5207 hold; the release
workflow, which TSK-5208 holds.
