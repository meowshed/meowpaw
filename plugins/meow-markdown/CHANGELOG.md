# meow-markdown

## 0.9.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.
- `bind` names under a stage each other tool configured for it, such as a `.mdformat.toml` beside a `.prettierrc`, so you can see which one runs.
- A clean `check` names the groups of settings it checked after `no findings`.

## 0.8.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- The profile reads a personal file and refuses a machine path in it.
