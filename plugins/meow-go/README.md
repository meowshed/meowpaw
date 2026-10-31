---
reader: someone choosing or running meow-go
answers: what meow-go does, what it adds to a session and how to run it
kind: reference
describes: [meow-go@0.2.1]
description: "Detects Go from the modules git tracks, reports each module's language version, pinned toolchain, declared tools and golangci-lint configuration, prints a stages table bound from them with the race detector on in test, reports a golangci-lint configuration that is not the version 2 shape and states a supply-chain check's reach, and compares the pinned toolchain with the installed one, writing no file, and carries what a reviewer of Go checks that no command reports."
---

# meow-go

`meow-go` tells you whether your repository holds Go, lists each module's
language version, pinned toolchain, declared tools and linter configuration,
prints a `[stages]` table bound from them with the race detector on in `test`,
checks that your golangci-lint configuration is the version 2 shape, and
compares your pinned toolchain with the installed one. Its skill tells Claude
Code what a reviewer of Go checks that no command reports. `status`, `bind` and
`check` read the files git tracks and run git alone; `toolchain` runs `go
version`. It writes no file, and it installs on its own, with no other part of
the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-go@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-go status
```

From your own shell, run the same launcher by its path in the installed unit.

The program counts a repository as Go where git tracks a `go.mod`, wherever it
lies. `status` prints, for each module, a `scope: <directory>` line, or
`scope: <part> <directory>` where your profile's `[parts]` declares a part
holding it, then:

1. `marker: <file>`.
2. `go: <version> minimum`, from the `go` line.
3. `toolchain: <name> pinned in <file>`, where a `toolchain` line names one.
4. `tool: <package>` for each `tool` directive, which declares an executable the
   project uses.
5. `golangci-lint: <file>, version <n>`, or `golangci-lint: no configuration
tracked`.

After the modules it prints `workspace: go.work tracked` where git tracks a
`go.work`, and `race detector: on`, or `race detector: off, as [go] race = false
records`.

Every command that reads the profile first prints its state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for each
key no unit reads. `bind` prints them on standard error, so what it prints on
standard output stays ready to paste.

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
state: without them a collaborator resolves other dependencies or runs other
checks. Ignore `*.test` binaries, coverage profiles and a directory you keep
test artifacts in with `-artifacts`, because each is regenerated on the next run.

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

When Claude Code reviews Go, the skill has it run `status` first, and then load
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

Claude Code 2.1.280 or later, declared in
`plugins/meow-go/requires.toml`, and git. `toolchain` needs `go` on `PATH`. The
pack is current as of Go 1.26 and the golangci-lint v2 configuration shape its
migration guide describes, read on 2026-09-20. golangci-lint, staticcheck and
govulncheck are named, never required: the pack binds one only where your
repository configured it.
