# meow-scm

## 0.8.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.

## 0.7.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- The commit skill loads for each source-control operation its rules bound, and a tool's operations are bounded in it.
- A test pins each subcommand's output to the words it opens with.
