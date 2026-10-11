# meow-gotask

## 0.5.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.

## 0.4.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- A test pins each subcommand's output to the words it opens with.
