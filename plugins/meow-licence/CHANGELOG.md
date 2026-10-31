# meow-licence

## 0.7.1

- Its launcher runs the build beside it in a checkout. An installed unit resolves its binary as before.

## 0.7.0

- Its launcher runs the shared executable, which now reads the record ADR-3090 describes; the unit itself is unchanged. This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.6.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.6.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.

## 0.5.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- A test pins each subcommand's output to the words it opens with.
