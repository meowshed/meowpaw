# meow-go

## 0.2.1

- Its launcher runs the build beside it in a checkout. An installed unit resolves its binary as before.

## 0.2.0

- Its launcher runs the shared executable, which now reads the record ADR-3090 describes; the unit itself is unchanged. This release retires epics and tasks. Before using it, run `paw upgrade` to preview and `paw upgrade --write` on a branch: `paw` refuses a record holding `tasks/` or `epics/` until then.

## 0.1.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.1.0

- Detects Go from each tracked `go.mod`, and reports a directory for each.
- `bind` prints a `[stages]` table bound from the module and its linter configuration, with the race detector on in `test` unless `[go] race = false` records otherwise.
- `check` reports a golangci-lint configuration that is not the version 2 shape or names a merged or removed linter, and states a supply-chain check's reach.
- `toolchain` compares the pinned toolchain with the installed one.
- The page states the toolchain versions the pack is current as of, and which generated files to commit and which to ignore.
