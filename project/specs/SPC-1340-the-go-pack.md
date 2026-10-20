---
id: SPC-1340
artifact: spec
status: live
revised: 2026-10-20
states:
  [
    REQ-2334,
    REQ-0133,
    REQ-3048,
    REQ-2412,
    REQ-2414,
    REQ-2420,
    REQ-2428,
    REQ-2432,
    REQ-2434,
    REQ-2436,
    REQ-2450,
  ]
---

# The Go pack

## Scope

This covers `meow-go`, the language pack for Go. It states what `status`
detects and lists, what `bind` prints, what `check` finds, what `toolchain`
compares, and what the skill and `reviewing.md` carry.

Every rule SPC-1190 states for a language pack holds here, and this document
states only what is Go's. It leaves the evidence recipe with `gotestsum` and
`-artifacts`, the `go fix` modernisers and the vulnerability scan unbound,
because none of them is one of the five stages (RES-0102). Running a stage is
SPC-1040's.

ADR-2660 orders the packs, and ADR-2670 adds the rules every pack keeps.

## Boundary

| Surface                                  | What it is                                                       |
| ---------------------------------------- | ---------------------------------------------------------------- |
| `plugins/meow-go/bin/meow-go`            | The program: `status`, `bind`, `check` and `toolchain`           |
| `plugins/meow-go/skills/go/SKILL.md`     | The skill                                                        |
| `plugins/meow-go/skills/go/reviewing.md` | What a reviewer of Go needs beyond the commands                  |
| `plugins/meow-go/README.md`              | The unit's page                                                  |
| `.meowpaw/profile.toml`, `[go] race`     | `false` turns the race detector off in `test`; absent means on   |
| Each tracked `go.mod`                    | The marker, the language version, the `toolchain` line and tools |
| `go.work`                                | Shows the repository holds several modules                       |
| `.golangci.yml` and its siblings         | The linter's configuration, read by `bind` and `check`           |
| `staticcheck.conf`                       | Shows the repository configured staticcheck                      |

The program is the `go` feature of `crates/meow`, built by `build-units`.
`status`, `bind` and `check` run git alone, as SPC-1190 states. `toolchain`
runs `go version` with `GOTOOLCHAIN=local`, and nothing else.

The pack was observed against Go 1.26 and golangci-lint v2 as RES-0102 read
them (RES-0102, RES-0364).

## Behaviour

### Detection

A work tree holds Go where git tracks a `go.mod`, wherever it lies (REQ-2334,
REQ-0133). `status` reports once for each directory holding one, naming the
directory and the part that holds it (REQ-3048).

`bind` binds one module. Where git tracks two or more `go.mod` files, every
stage is printed `# <stage>: unresolved, several Go modules and no single
command reaching them: <files>`, because a workspace has no `./...` across its
modules (RES-0364). A single module below the root is reached with `cd
<directory> &&` in front of each command.

### What `status` reports

In this order, for each directory holding a `go.mod`:

1. The scope line and `marker: <file>`.
2. `go: <version> minimum`, from the `go` line, and `toolchain: <name> pinned
in <file>` where a `toolchain` line names one (RES-0102, RES-0364).
3. `workspace: go.work tracked` where git tracks a `go.work`.
4. `tool: <package>` for each `tool` directive, which RES-0102 reads as the
   project's declared executables.
5. `golangci-lint: <file>, version <n>` for the linter's configuration, or
   `golangci-lint: no configuration tracked`.
6. `race detector: on` or `race detector: off, as [go] race = false records`
   (REQ-2414).

### What `bind` prints

Each stage takes the first row that applies, and a comment under `lint` names
the linters golangci-lint enables for this configuration as the output of
`golangci-lint linters` (REQ-2432, RES-0102):

| Stage    | Printed as                                           | When                                                                                  |
| -------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `format` | `test -z "$(gofmt -l .)"`                            | No golangci-lint configuration with a `formatters` section                            |
| `format` | `# format: unresolved, <file> configures formatters` | A `formatters` section, because `golangci-lint fmt --diff` states no exit status      |
| `lint`   | `golangci-lint run`                                  | A `.golangci.yml`, `.yaml`, `.toml` or `.json` file                                   |
| `lint`   | `staticcheck ./...`                                  | A `staticcheck.conf` and no golangci-lint configuration                               |
| `check`  | `go vet ./...`                                       | Always, because the compiler is `build` and `vet` has the findings with no other home |
| `test`   | `go test -race ./...`                                | `[go] race` isn't `false`                                                             |
| `test`   | `go test ./...`                                      | `[go] race = false`, with a comment recording it                                      |
| `build`  | `go build ./...`                                     | Always                                                                                |
| any      | `# <stage>: unbound, looked for <files>`             | No row above applies                                                                  |

`gofmt`, `go vet`, `go build` and `go test` ship with Go and are configured by
the module, so they bind from `go.mod` alone. `lint` binds the tool the
repository configured and never picks between golangci-lint and staticcheck
(REQ-2420). `go test` runs the examples in the documentation that state their
output, so the stage runs them, and a runner that leaves them out never binds
(REQ-2412, RES-0364). The race detector is on unless the profile records
otherwise (REQ-2414). `build` writes an executable when `./...` matches a single
main package, and the README says so.

Where a `toolchain` line pins a version, a comment says the go command runs
that toolchain, and that `meow-go toolchain` compares it with the installed one
(REQ-2428). A `mise.toml` or a `Taskfile.yml` is named with the runner's pack.
A stage the profile already declares is left out, and `bind` exits 0 once it
prints the table.

### What `check` finds

`check` exits 1 on any finding, each naming the file (REQ-2434):

| Finding                                                           | When                                                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `<file>: declares no version "2", so it is a v1 configuration`    | A golangci-lint YAML configuration without a top-level `version: "2"`           |
| `<file> names <linter>, which golangci-lint v2 merged or removed` | The configuration names `stylecheck`, `gosimple`, `disable-all` or `enable-all` |
| `<file> doesn't parse as <format>: <message>`                     | A configuration or `go.mod` that doesn't parse                                  |

A supply-chain tool is read from the `tool` directives and the stages' commands.
Where `govulncheck` is one of them, `check` prints `supply chain:
govulncheck: covers direct and transitive dependencies, and reports a
vulnerable dependency only where the code reaches it, so reachability`
(REQ-2436, RES-0102). Where none is, it prints `supply chain: none configured`.

With no finding, `check` prints `no findings; rule groups enabled:` followed by
the settings it checked: the golangci-lint configuration's shape and the
linters it names.

### What `toolchain` compares

`meow-go toolchain` reads the pin: the `toolchain` line of the module's
`go.mod`. It runs `go version` in the module's directory with
`GOTOOLCHAIN=local`, so the go command doesn't switch to the pin and report it
as installed (RES-0364). It compares the installed version with the pin
(REQ-2428):

| State                         | Printed as                                                 | Exit |
| ----------------------------- | ---------------------------------------------------------- | ---- |
| No `toolchain` line           | `toolchain: nothing pinned`                                | 0    |
| The installed version matches | `toolchain: go <pin>, pinned in <file> and installed`      | 0    |
| The installed version differs | `unresolved: go <pin> pinned, <version> installed`         | 3    |
| `go` exits non-zero           | `unresolved: go <pin> pinned, none installed` and its line | 3    |
| `go` isn't on `PATH`          | `tool absent: go`                                          | 3    |
| `go` prints no version        | `tool broken: go printed <first line>`                     | 3    |

A `go` line alone is a minimum and not a pin, and `toolchain` reports it as
`toolchain: nothing pinned`.

### Generated files

`go.mod`, `go.sum`, `go.work`, `go.work.sum`, the golangci-lint configuration
and a `vendor/` directory the repository vendors are project state to commit.
Test binaries (`*.test`), coverage profiles and a directory a run keeps with
`-artifacts` are cache to ignore (REQ-2450). The README states both.

### What the skill carries

The skill's body gives, in order: detection, the stages and what `bind` prints
for each, the configuration shape, what to read before reporting a pass, and
the prohibitions. It forbids writing a v1-shaped golangci-lint configuration,
running `go fix` in place during a check, reporting a `go fix` suggestion as a
defect, and treating a scan without reachability as `govulncheck` (RES-0102).

`reviewing.md` carries what a Go reviewer checks that no command reports: the
`%w` boundary, context and cancellation, goroutine lifetime, interfaces the
consumer defines, table-driven subtests, and standard-library use beyond the
declared `go` version (RES-0102).

## Failure paths

Each is printed as SPC-1190 states, by every command it applies to:

| State                                       | Reported as                                                                                         | Exit |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------- | ---- |
| Git tracks no `go.mod`                      | `unresolved: not a Go repository`                                                                   | 3    |
| No profile, or a profile that doesn't parse | `unresolved: <what is wrong with the profile>`                                                      | 3    |
| Two or more modules                         | each stage `# <stage>: unresolved, several Go modules and no single command reaching them: <files>` | 0    |
| A `go.mod` that doesn't parse               | `unresolved: <file> doesn't parse: <message>`                                                       | 3    |
| `toolchain`: as its table states            | as its table states                                                                                 | 3    |
