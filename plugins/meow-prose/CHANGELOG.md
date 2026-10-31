# meow-prose

## 0.9.0

- The writing standard loses the epic and task record types, and a decision and a defect carry their plan.
- This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.8.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.

## 0.7.0

- The standard ships as a Pi package, and the session routes each request itself.
