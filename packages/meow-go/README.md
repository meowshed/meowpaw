---
reader: someone installing or running meow-go on Pi
answers: what meow-go provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-go@0.1.1]
---

# @meowshed/meow-go

Detects Go from the modules git tracks, reports each module's language version, pinned toolchain, declared tools and golangci-lint configuration, prints a stages table bound from them with the race detector on in test, reports a golangci-lint configuration that is not the version 2 shape and states a supply-chain check's reach, and compares the pinned toolchain with the installed one, writing no file, and carries what a reviewer of Go checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-go
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## Run it

The package puts its launcher on `PATH`, so the skill runs `meow-go status`,
`meow-go bind`, `meow-go check` and `meow-go toolchain` in your repository.
They behave as the Claude Code unit's page describes in
`plugins/meow-go/README.md`: `status` lists each module, `bind` prints a
`[stages]` table with the race detector on in `test`, `check` reports a
golangci-lint configuration that is not the version 2 shape, and `toolchain`
compares your pinned toolchain with the installed one.

## Bind your stages

`meow-go bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[stages]
format = "test -z \"$(gofmt -l .)\""
lint = "golangci-lint run"
# golangci-lint linters lists the linters this configuration enables
check = "go vet ./..."
test = "go test -race ./..."
build = "go build ./..."
```

The pack binds each stage from the module and the configuration beside it, and
never from what is installed:

| Stage    | Bound to                       | When                                                                             |
| -------- | ------------------------------ | -------------------------------------------------------------------------------- |
| `format` | `test -z "$(gofmt -l .)"`      | No golangci-lint configuration with a `formatters` section                       |
| `format` | nothing, printed as unresolved | A `formatters` section, because `golangci-lint fmt --diff` states no exit status |
| `lint`   | `golangci-lint run`            | A `.golangci.yml`, `.yaml`, `.toml` or `.json` file                              |
| `lint`   | `staticcheck ./...`            | A `staticcheck.conf` and no golangci-lint configuration                          |
| `check`  | `go vet ./...`                 | Always                                                                           |
| `test`   | `go test -race ./...`          | `[go] race` isn't `false`                                                        |
| `test`   | `go test ./...`                | `[go] race = false`                                                              |
| `build`  | `go build ./...`               | Always                                                                           |

`gofmt`, `go vet`, `go test` and `go build` ship with Go and are configured by
the module. `format` checks what `gofmt -l` prints, because `gofmt` documents no
exit status for a file that differs. A repository that configures golangci-lint
formatters has `format` printed as unresolved, and `lint` reports their issues.
`lint` binds the linter your repository configured, golangci-lint before
staticcheck where both are, and names the other. A module below the root is
reached with `cd <directory> &&` in front of each command, and a repository with
two or more `go.mod` files gets every stage printed as unresolved, because a
workspace has no `./...` across its modules.

`go test` runs the examples in your documentation that state their output, so
the `test` stage runs them. The race detector is on, because a run without it
is evidence about everything except the defect Go programs most often have. Turn
it off by recording it in the profile, which `bind` then names:

```toml
[go]
race = false
```

`go build ./...` writes an executable into the working directory when `./...`
matches a single main package. A stage your profile already declares is left
out, and a `mise.toml` or a `Taskfile.yml` is named with the runner's pack.

## Check your settings

`meow-go check` reports a golangci-lint configuration that is the wrong shape,
one line for each finding, and exits 1 on any:

| Line                                                            | When                                                             |
| --------------------------------------------------------------- | ---------------------------------------------------------------- |
| `<file>: declares no version "2", so it is a v1 configuration`  | The configuration has no top-level `version: "2"`                |
| `<file> names <name>, which golangci-lint v2 merged or removed` | It names `stylecheck`, `gosimple`, `disable-all` or `enable-all` |
| `<file> doesn't parse as <format>: ...`                         | The configuration isn't valid YAML, TOML or JSON                 |

With no finding it prints `no findings` and the groups of settings it checked.
Either way it ends with a `supply chain:` line. Where `govulncheck` is a `tool`
directive or a word of a stage's command, the line says it covers direct and
transitive dependencies and reports a vulnerable dependency only where your code
reaches it, so a finding is a reachable one. Otherwise it says `supply chain:
none configured`.

## Compare the toolchain

`meow-go toolchain` reads the `toolchain` line of your `go.mod` and runs `go
version` there with `GOTOOLCHAIN=local`, so the go command doesn't switch to the
pin and report it as installed. It is the one command that starts a tool. A `go`
line alone is a minimum and not a pin.

| Line                                                   | Means                                      | Exit |
| ------------------------------------------------------ | ------------------------------------------ | ---- |
| `toolchain: nothing pinned`                            | No `toolchain` line                        | 0    |
| `toolchain: go 1.26.0, pinned in go.mod and installed` | The installed version matches the pin      | 0    |
| `unresolved: go 1.25.4 pinned, 1.26.0 installed`       | The installed version differs              | 3    |
| `unresolved: go 1.25.4 pinned, none installed: ...`    | `go` exited non-zero, and its line follows | 3    |
| `tool absent: go`                                      | `go` isn't on `PATH`                       | 3    |
| `tool broken: go printed ...`                          | `go` printed no version                    | 3    |

## Generated files

Commit `go.mod`, `go.sum`, `go.work`, `go.work.sum`, your golangci-lint
configuration and a `vendor/` directory if you vendor, because each is project
state. Ignore `*.test` binaries and coverage profiles, because each is
regenerated on the next run.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check` exits 1 on a
finding, and every command exits 3 when it can't:

| Line                                              | Means                                                      |
| ------------------------------------------------- | ---------------------------------------------------------- |
| `unresolved: not a Go repository`                 | Git tracks no `go.mod`                                     |
| `unresolved: no profile at .meowpaw/profile.toml` | The repository has no profile                              |
| `unresolved: the profile doesn't parse: ...`      | The profile isn't valid TOML; the parser's message follows |
| `unresolved: <file> doesn't parse: ...`           | A `go.mod` has no `module` directive                       |

`bind` exits 0 whatever comments its table holds, because a stage printed with
its reason is settled.

## Review Go

When Pi reviews Go, the skill has it run `status` first, and then load
`reviewing.md`, which holds six points no command reports: the `%w` boundary,
context and cancellation, goroutine lifetime, interfaces the consumer defines,
table-driven subtests, and standard-library use beyond the declared `go`
version. The skill never writes a v1-shaped golangci-lint configuration, never
runs `go fix` in place during a check, never reports a `go fix` suggestion as a
defect, and never treats a scan without reachability as `govulncheck`.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Go is reviewed. The program is a native binary shipped
inside the unit, and needs git on the machine. On a machine the unit carries no
binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-go --help` lists the subcommands, and `meow-go <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool, and
the first word of each kind of line it prints. A test holds each subcommand's
output to those words.

## What it needs

git, and `go` on `PATH` for `toolchain`. The pack is current as of Go 1.26 and
the golangci-lint v2 configuration shape its migration guide describes, read on
2026-09-20.
