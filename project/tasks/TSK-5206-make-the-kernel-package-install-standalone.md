---
id: TSK-5206
artifact: task
status: approved
revised: 2026-10-04
realises: ADR-2790
fixes: [BUG-1400, BUG-1402]
closes: [REQ-4130, REQ-4134, REQ-4108]
---

# Make the kernel package install standalone

The kernel extension loads the reply shape and the judge prompt from files
bundled inside the package, injects the reply shape into the system prompt
as the one extension that does, and puts the package's bin wrappers on PATH.

## Acceptance criteria

1. Given `@meowshed/meow-core` installed from a copy with no `plugins/`
   directory anywhere above it, when a Pi session starts, then the reply
   shape is injected into the guidelines and the prose gate's judge prompt
   is loaded. Closed by: installing from a copied package directory and
   inspecting the session's system prompt.
2. Given the kernel and any other layer installed together, when a session
   starts, then the reply shape appears in the system prompt once. Closed
   by: installing both packages and counting the shape's occurrences.
3. Given a session with the kernel installed, when a skill calls
   `meow-prose-gate` by name, then the wrapper resolves. Closed by: running
   the wrapper's status command from a Pi session.
