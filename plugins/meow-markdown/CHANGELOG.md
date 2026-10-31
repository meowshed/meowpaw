# meow-markdown

## 0.10.1

- Its launcher runs the build beside it in a checkout. An installed unit resolves its binary as before.

## 0.10.0

- Its launcher runs the shared executable, which now reads the record ADR-3090 describes; the unit itself is unchanged. This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.9.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.9.0

- Every unit's `requires.toml` now states its layer, the units it needs and, in a pack, the range of `meow-core` versions it works with, and the check fails a unit missing one.
- Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions.
- `bind` names under a stage each other tool configured for it, such as a `.mdformat.toml` beside a `.prettierrc`, so you can see which one runs.
- A clean `check` names the groups of settings it checked after `no findings`.
- `links` names each file lychee's run left in the working tree.
- `links` says its result is read from lychee's JSON report, and the page states which generated files to commit and which to ignore.

## 0.8.0

- The shared executable the unit's launcher runs is now named `paw`; reinstall the unit, because an install from before this release keeps no binary under the old name.
- The profile reads a personal file and refuses a machine path in it.
