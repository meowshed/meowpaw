# meow-go

## 0.1.1

- Its launcher runs the shared executable, which now carries `serde_json` 1.0.154 and `sha2` 0.11.1; the unit itself is unchanged.

## 0.1.0

- Detects Go from each tracked `go.mod`, and reports a directory for each.
- `bind` prints a `[stages]` table bound from the module and its linter configuration, with the race detector on in `test` unless `[go] race = false` records otherwise.
- `check` reports a golangci-lint configuration that is not the version 2 shape or names a merged or removed linter, and states a supply-chain check's reach.
- `toolchain` compares the pinned toolchain with the installed one.
- The page states the toolchain versions the pack is current as of, and which generated files to commit and which to ignore.
