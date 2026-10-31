# meow-scm

## 0.9.0

- The commit skill maps one decision or defect to one branch and one pull request.
- This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.8.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.8.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.
- The commit skill uses worktrunk only for operations whose result it then reads from git.

## 0.7.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- The commit skill loads for each source-control operation its rules bound, and a tool's operations are bounded in it.
- A test pins each subcommand's output to the words it opens with.
