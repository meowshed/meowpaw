# meow-loop

## 0.18.0

- A run's steps are research, requirements, design, spec and implement, and an `implement` run takes a decision or a defect, finishing when it stores `done`.
- This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.17.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.17.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.

## 0.16.0

- The loop runs from a Pi package, and the session routes each request itself.
