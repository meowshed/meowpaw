# meow-flow

## 0.54.1

- Its launcher runs the build beside it in a checkout. An installed unit resolves its binary as before.

## 0.54.0

- The method has six steps, research, requirements, design, spec, implement and review: a decision or a defect is one issue and one pull request, and carries a `## Plan`. Epics and tasks are retired, and `paw` reads them only from `archive/`.
- `/meow-flow:upgrade` and `paw upgrade` move a repository to this form, archiving epics and tasks, storing `done` on finished records and adding open tasks to their record's plan.
- `paw done`, `paw brief` and `paw ready implement` take a decision or a defect, and a defect can store `done`.
- This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.53.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.53.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.
- The method runs each push, merge, release, issue write and governance change as its own command, so the platform asks for each one, and never asks for an approval that covers the next.

## 0.52.0

- The method's steps work from a Pi package, and the session routes each request itself.
