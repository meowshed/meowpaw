---
id: EPC-2700
artifact: epic
status: done
revised: 2026-10-04
realises: ADR-2780
---

# Ship the harness as Pi packages with TypeScript extensions

Realises ADR-2780. The epic is complete when every meowpaw layer ships as a
Pi package, each Claude Code plugin component has its Pi analogue, the
dual-platform contract holds, and every requirement ADR-2780 addresses is
closed.

## Acceptance criteria

Taken from ADR-2780's list of how it will be known realised:

1. `pi install npm:@meowshed/meow-core` loads the kernel package, and a Pi
   session shows the reply shape in the system prompt.
2. `pi install npm:@meowshed/meow-flow` loads the method package, and
   `/meow-flow:run` drives the seven-step chain.
3. A `git commit` with a prose defect is blocked by the prose gate extension.
4. A `git commit` on the declared trunk is blocked by the git guard
   extension.
5. A `git push` with an unsigned commit is blocked by the push guard
   extension.
6. The router tool returns a route for a request, and the model follows it.
7. The skeptic tool refutes a verified claim and produces a defect.
8. Skills load by description on both platforms and produce the same
   behaviour.
9. `paw check` runs from the Pi package and reports the same findings as from
   the Claude Code plugin.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-5200 write the research, requirements, decision and specification
      closes: REQ-4100, REQ-4102, REQ-4104, REQ-4106, REQ-4108, REQ-4110, REQ-4112, REQ-4114, REQ-4116, REQ-4118, REQ-4120, REQ-4122, REQ-4124, REQ-4126, REQ-4128
- [x] T-002 TSK-5201 build the kernel Pi package
      closes: REQ-4100, REQ-4102, REQ-4106, REQ-4108, REQ-4112, REQ-4114, REQ-4116, REQ-4118, REQ-4120
- [x] T-003 TSK-5202 build the method Pi package
      closes: REQ-4100, REQ-4102, REQ-4104, REQ-4106, REQ-4110, REQ-4112, REQ-4114, REQ-4118, REQ-4120, REQ-4122, REQ-4126, REQ-4128
- [x] T-004 TSK-5203 build the practice Pi package
      closes: REQ-4100, REQ-4102, REQ-4106, REQ-4114, REQ-4118, REQ-4120
- [x] T-005 TSK-5204 build the pack Pi packages
      closes: REQ-4100, REQ-4102, REQ-4106, REQ-4114, REQ-4118, REQ-4120
- [x] T-006 TSK-5205 verify the dual-platform contract
      closes: REQ-4102
      The four defects found after this epic closed — the extensions reading
      the monorepo's plugins directory, the skills naming a platform variable,
      every package injecting the reply shape, and the installer's ESM defect
      (BUG-1400 to BUG-1403) — are fixed by EPC-2710, which realises ADR-2790.

## Coverage

TSK-5200 produces the authorising records. TSK-5201–5204 build each package
and test its extension against the acceptance criteria that concern it.
TSK-5205 is an integration check that skills produce the same behaviour on
both platforms.

## Not covered

Porting native binaries to TypeScript. The eval runner. Per-user
configuration on Pi. Dynamic tool registration, virtual models and structured
output.
