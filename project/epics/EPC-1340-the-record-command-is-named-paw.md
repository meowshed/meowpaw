---
id: EPC-1340
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1350
---

# The record's command is `paw`

Realises exactly one authorising record, ADR-1350. The epic is complete when
a person runs the record's command as `paw`, and `meow-method` still works for
one release while saying it is deprecated.

## Acceptance criteria

Taken from ADR-1350, from its list of how I will know it was realised, before
the tasks below were written:

1. `plugins/meow-method/bin/paw check` checks the record, and every message
   and usage line it prints names `paw`.
2. `plugins/meow-method/bin/meow-method check` prints to standard error that
   the command is `paw` and that 0.31.0 removes the alias, and its standard
   output and exit status equal `paw`'s.
3. No skill, hook, template, specification, documentation page, `CLAUDE.md`
   or the profile runs `meow-method` as a command.
4. REQ-3166 lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-2020 the record's command is `paw`, with `meow-method` as a deprecated alias
      closes: REQ-3166
      evidence: three fixtures in `Named`, seen failing first, and the `test` verb passing.

## Coverage

ADR-1350 addresses 1 requirement, which lands in the one task above. That
task is the smallest set that tests the decision.

## Not covered

The task removing the alias in 0.31.0, which ADR-1350 leaves to be written
when 0.30.0 is released.
