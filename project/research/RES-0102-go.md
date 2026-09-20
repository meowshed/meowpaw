---
id: RES-0102
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Go

## Summary

Go has the least ambiguity of any language surveyed and three real questions
underneath it. The linter's configuration changed shape in a major version, so
a plausible-looking file configures a formatter as a linter and does less than
it says. The vulnerability checker reports only what the code actually reaches,
which is what lets it gate a change, where a report would only inform one. And
the current release deletes a test's own output files unless the run asked for
them.

Research for one supported language. A toolchain is a set of tools. This covers
which tools make up Go's, what each answers that the others cannot, and what
the verbs resolve to. It also covers the configuration break that makes a
plausible pack wrong, what the pack authors, and what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md), nor what a skill costs, which
is [RES-0005-skill-format.md](RES-0005-skill-format.md).

## The question

Go has the least ambiguity of any language here: one formatter, one vetter, one
test runner, all shipped with the toolchain. That makes the verbs easy and
hides three real questions - which linter configuration shape is current, how a
project declares the tools it uses, and where the evidence from a test run
goes.

## Method

We fetched and read the vendor documentation on 2026-09-20: the linter's
migration guide and linter list, the vulnerability-management page, and the
release notes for the current and previous versions. The artifact-directory
behaviour and the modernising tool came from the release notes.

The linter's default enabled set was deliberately not recorded, because the
documentation declines to publish one and directs the reader to ask the tool -
the document states that, and works around nothing.

Nothing was installed or run.

## Findings

### The marker is `go.mod`, and it fixes more than the module path

`go.mod` marks the project, names the module path that every internal import
resolves against, and carries a `go` directive naming the language version,
which changes what the compiler accepts.

Two newer directives matter to a pack. The `tool` directive lets a module track
executable dependencies directly, replacing the old convention of blank imports
in a file named `tools.go`, and `go tool` runs them. So the question _which
tools does this project use_ now has a declared answer in the module file,
where the convention used to hide it in a source file nobody compiles.

The `ignore` directive names directories the go command should skip.

`go.work` marks a multi-module workspace. A repository with several `go.mod`
files is several modules, and running the verbs from the root covers one of
them unless a workspace says otherwise.

One default is counter-intuitive, and a pack knows it before reporting on it:
`go mod init` writes a `go` version one release behind the toolchain. _"Running
`go mod init` using a toolchain of version 1.N.X will create a go.mod file
specifying the Go version go 1.(N-1).0"_, deliberately, to encourage modules
compatible with currently supported versions. A new module that looks a release
out of date is showing the tool's own default, and nobody neglected it.

### The toolchain, tool by tool

| Role            | Tool               | Ships with Go | What only it answers                                               |
| --------------- | ------------------ | ------------- | ------------------------------------------------------------------ |
| Driver          | `go`               | yes           | Build, test, module graph, tool execution                          |
| Format          | `gofmt`            | yes           | The canonical form                                                 |
| Format          | `gofumpt`          | no            | A stricter superset of `gofmt`                                     |
| Imports         | `goimports`, `gci` | no            | Import grouping and ordering                                       |
| Long lines      | `golines`          | no            | Wrapping, which `gofmt` declines to do                             |
| Analysis        | `go vet`           | yes           | Printf mismatches, lost cancels, bad struct tags                   |
| Modernise       | `go fix`           | yes           | Code that could use newer language and library features            |
| Lint            | `golangci-lint`    | no            | Over 130 linters behind one command and one configuration          |
| Lint            | `staticcheck`      | no            | The merged set that was `staticcheck`, `stylecheck` and `gosimple` |
| Vulnerabilities | `govulncheck`      | no            | Which advisories the code actually reaches                         |
| Test            | `go test`          | yes           | The tests, the race detector, coverage                             |
| Test output     | `gotestsum`        | no            | JUnit XML from a run                                               |
| Intelligence    | `gopls`            | no            | Editing, navigation, refactors                                     |
| Debug           | `delve`            | no            | Stepping a running program                                         |
| Benchmarks      | `benchstat`        | no            | Whether a benchmark difference is significant                      |
| Release         | `goreleaser`       | no            | Cross-platform artifacts and release notes                         |

The third column is what makes the fallbacks necessary. A machine with Go and
nothing else has `gofmt`, `go vet`, `go fix` and `go test`, and a pack that
resolves `fmt` to the aggregator unconditionally fails there.

### The linter's configuration changed shape, and a v1-shaped file is silently wrong

golangci-lint v2 moved four tools out of the linter list into a section of
their own. The migration guide states that `gci`, `gofmt`, `gofumpt` and
`goimports` were relocated to a formatters section, that `linters-settings` was
split into `linters.settings` and `formatters.settings`, and that a
configuration file carries a required `version: "2"` field.

Two further changes bear on what a pack may write. `stylecheck`, `gosimple` and
`staticcheck` merged into a single `staticcheck`, so a configuration enabling
the first two names tools that no longer exist. And `disable-all` and
`enable-all` became `linters.default: none` and `linters.default: all`.

The tool ships a `migrate` command that rewrites a v1 file, with its own stated
limitation: _"comments inside a configuration file are not migrated. You need
to add them manually after the migration."_

The failure this prevents is a configuration that looks right, names real
tools, and configures a formatter as though it were a linter - a file that does
less than it says while passing.

The default enabled set is deliberately not documented as a list; the
documentation directs the reader to `golangci-lint help linters` for what is on
by default and `golangci-lint linters` for what a given configuration enables.
A pack reports the second and assumes nothing about the first, because the
answer is per repository.

### Formatting became a verb of the linter

Because the formatters are a section of the configuration, `golangci-lint fmt`
formats using whatever that section enables. So `fmt` resolves to the linter
where the project configures one, and to a standalone tool where it does not.

| Verb        | Command                                                             |
| ----------- | ------------------------------------------------------------------- |
| `fmt`       | `golangci-lint fmt`, else `gofumpt -l -w .`, else `gofmt -l -w .`   |
| `lint`      | `golangci-lint run`                                                 |
| `typecheck` | `go vet ./...`                                                      |
| `test`      | `go test ./... -race`, through `gotestsum` where evidence is needed |
| `build`     | `go build ./...`                                                    |

### `typecheck` is `go vet`, and the choice is about what else there is

Go compiles as part of `build`, so a separate type pass would repeat it. `go
vet` is the nearest thing that reports something `build` does not: printf
argument mismatches, unreachable code, struct tags that do not parse, lost
cancel functions.

Leaving `typecheck` unresolved - the honest answer in a dynamically typed
language - would drop a set of findings Go has no other place for.

### `-race` is the only evidence about concurrency, and it is not the default

`go test ./...` passes on code with a data race. The detector is a build mode,
costs roughly an order of magnitude in time and memory, and reports only races
that actually occur during the run.

A test run without it produces no evidence about the property Go programs most
often get wrong. Including it by default and letting the project turn it off
puts the cost where it can be seen.

### The vulnerability check is reachability-based, which changes what a gate means

`govulncheck` is not a dependency scanner. The documentation is explicit, and
is quoted as written:

> The govulncheck command analyzes your codebase and only surfaces
> vulnerabilities that actually affect you, based on which functions in your
> code are transitively calling vulnerable functions.

It reads the Go vulnerability database at `vuln.go.dev`. That database
aggregates the national database, the GitHub advisory database and direct
reports from Go maintainers, stores reports in the OSV format, and is curated
by the Go security team.

That reachability analysis is why this can gate a change, where a report would
only inform one. A scanner that fires on the presence of a vulnerable module
produces findings nobody can act on, and somebody disables it within a week. A
tool that fires only where the vulnerable function is reachable produces
findings that are each a decision.

### Evidence from a test run has two answers and one of them is new

`gotestsum` wraps `go test` and emits JUnit XML, which is what makes a run
citable after the terminal has scrolled away.

Go 1.26 added a second, smaller answer for artifacts a test itself produces.
`T.ArtifactDir`, `B.ArtifactDir` and `F.ArtifactDir` return a directory for a
test's output files, and _"When `-artifacts` flag is provided to `go test`, the
directory is under the output directory"_. Without that flag the artifacts go
to a temporary directory that disappears when the test finishes.

That default is the finding. A test that writes a diagnostic file produces
evidence that is deleted unless the run asked for it, so a harness collecting
evidence passes `-artifacts` and an `-outputdir`, and hopes for nothing.

### `go fix` became a modernising tool, which is a new kind of finding

Go 1.26 rewrote `go fix` on the same analysis framework as `go vet`, making it
_"the home of Go's modernizers"_. Dozens of analysers rewrite code to use newer
language and library features: `minmax` for Go 1.21's `min` and `max`,
`rangeint` for range-over-integer, `stringscut` for `strings.Cut`. Every
historical fixer was removed. It also carries a source-level inliner driven by
`//go:fix inline` directives, which lets a library automate its own API
migration for consumers.

It edits files silently on success, discards any fix that touches generated
files, and has a `-diff` mode that previews instead.

For a pack this is a fifth kind of finding, distinct from the other four. It is
no defect, no style preference, no vulnerability and no type error: _this code
predates a feature that would express it better_. It belongs in a report and
gates nothing, and it runs with `-diff` and never in place, because a tool that
rewrites files during a check is doing something a check should not.

### What the pack authors

`go.mod` - including the `tool` directives, which is how a project now records
the executables it depends on - and `.golangci.yml` in its v2 shape, plus
`go.work` for a multi-module repository.

The `tool` directive matters more than it looks. A pack that installs a linter
globally and a pack that adds it to the module produce the same green run and
different repositories: only one of them will still work for the next person.

### What a reviewer needs that no command reports

Error wrapping with `%w`, and what that lets a caller recover with `errors.Is`
and `errors.As`. Every arrangement compiles and one is usable.

Context propagation and cancellation - whether a long operation is cancellable
at all, which no verb asks.

Goroutine lifetime: who stops it, and what happens when nobody does.

Interfaces defined by the consumer, where exporting one beside the
implementation is the common mistake, which is the convention a reviewer
enforces and no linter has.

Table-driven tests, and the subtests that make one failing case nameable.

Whether the code respects the `go` directive's version, since using a newer
standard-library function than the declared version allows fails for consumers
and never here.

### What the skill has to contain

In the body, in this order:

1. Detection. `go.mod` with the module path and `go` version, `go.work` for
   several modules, `tool` directives for declared executables, and that `go
mod init` writes a version one release behind by design. 2. Verb resolution
   with fallbacks, naming which tools ship with Go and what happens on a
   machine that has only those. 3. The configuration shape. A generated
   `.golangci.yml` declares `version: "2"`, puts the four formatters under
   `formatters`, and never names `stylecheck`, `gosimple`, `disable-all` or
   `enable-all`. 4. What to read before reporting a pass. Whether `-race` was
   in the test invocation; what `golangci-lint linters` reports as enabled
   here, where the default list answers nothing. 5. What must never happen.
   Writing a v1-shaped configuration. Running `go fix` in place during a check.
   Reporting a `go fix` suggestion as a defect. Treating a vulnerability scan
   without reachability as equivalent to `govulncheck`.

In supporting files: the tool inventory, and templates for `.golangci.yml`,
`go.work` and `tool` directives. Also the evidence recipe with `gotestsum`,
`-artifacts` and `-outputdir`, the reviewer's knowledge, and the dated facts
with what to re-check: the configuration version, the merged linters, the `go
mod init` default and the artifact flags.

## Conclusions

1. A Go project is marked by `go.mod`, which names the module path and the
   language version, and a repository with several of them is several modules
   unless a `go.work` says otherwise. 2. The `tool` directives are read as the
   project's declared executables, replacing the `tools.go` convention, and a
   pack adds to them, installing nothing globally. 3. A new module's `go`
   version being one release behind is the tool's default, which nobody
   neglected, and no report calls it staleness. 4. A generated `.golangci.yml`
   declares `version: "2"` and puts `gci`, `gofmt`, `gofumpt` and `goimports`
   under `formatters`, where they used to sit under `linters`. 5. A pack never
   names a merged or removed linter. `stylecheck` and `gosimple` are
   `staticcheck`, and `disable-all` and `enable-all` are `linters.default`. 6.
   Migrating an existing configuration uses the tool's own `migrate` command,
   and the comments it drops are restored by hand, because the tool states it
   does not carry them. 7. The enabled linter set is reported from
   `golangci-lint linters` for this repository, and from no documented default,
   because the documentation deliberately publishes none. 8. `fmt` resolves to
   `golangci-lint fmt` where formatters are configured and falls back to
   `gofumpt` then `gofmt`, so a machine with only the Go toolchain still
   formats. 9. `typecheck` resolves to `go vet`, because the compiler is
   already `build` and `vet` is where findings with no other home live. 10.
   `test` runs with `-race` by default, because a run without it is evidence
   about everything except the property Go programs most often get wrong, and
   the project may turn it off with the cost stated. 11. Test evidence is
   collected as JUnit XML through `gotestsum`, because a result that exists
   only in a terminal cannot be cited. 12. A run that collects artifacts passes
   `-artifacts` with an `-outputdir`, since otherwise a test's own output files
   are written to a temporary directory and deleted. 13. Vulnerability checking
   uses `govulncheck` and its reachability analysis, because a scanner that
   fires on presence produces findings nobody can act on and a gate that
   produces those is disabled. 14. `go fix` is a fifth kind of finding, and the
   pack reports it and applies none of it. It runs with `-diff` during a check,
   and its suggestions modernise code that already works. 15. The reviewer's
   knowledge is recorded with the pack: the `%w` boundary, context and
   cancellation, goroutine lifetime, consumer-defined interfaces, table-driven
   subtests, and standard-library use beyond the declared `go` version. 16. The
   skill body carries detection, verb resolution with fallbacks, the
   configuration shape, what to read before reporting a pass, and the
   prohibitions, in that order. 17. The inventory, templates, evidence recipe,
   reviewer knowledge and dated facts live in supporting files, each with what
   to re-check.

## Sources

All read 2026-09-20.

- [golangci-lint migration
  guide](https://golangci-lint.run/docs/product/migration-guide/) - that `gci`,
  `gofmt`, `gofumpt` and `goimports` moved to a formatters section; that
  `linters-settings` split into `linters.settings` and `formatters.settings`;
  the required `version: "2"` field; the merge of `stylecheck` and `gosimple`
  into `staticcheck`; the replacement of `disable-all` and `enable-all` by
  `linters.default`; and the `migrate` command with its stated failure to carry
  comments. - [golangci-lint linters](https://golangci-lint.run/docs/linters/)
  - over 130 linters available; the merge of `stylecheck` and `gosimple` into
    `staticcheck`; and the instruction to use `golangci-lint help linters` and
    `golangci-lint linters`, because no published default list exists. -
    [golangci-lint formatters](https://golangci-lint.run/docs/formatters/) - the
    formatters as a first-class section run by `golangci-lint fmt`. - [Go
    vulnerability management](https://go.dev/doc/security/vuln/) - that
    `govulncheck` surfaces only vulnerabilities reached by functions the code
    transitively calls; the Go vulnerability database at `vuln.go.dev` drawing on
    the national database, the GitHub advisory database and maintainer reports;
    the OSV report format; and curation by the Go security team. - [Go 1.26
    release notes](https://go.dev/doc/go1.26) - the rewritten `go fix` as the
    home of the modernisers on the same analysis framework as `go vet`, with
    every historical fixer removed and a source-level inliner driven by `//go:fix
inline`; the `go mod init` default of `go 1.(N-1).0` and its stated reason;
    the removal of `cmd/doc` and `go tool doc`; and `T.ArtifactDir`,
    `B.ArtifactDir` and `F.ArtifactDir` with the `-artifacts` flag and the
    temporary directory used when it is absent. - [Using go fix to modernize Go
    code](https://go.dev/blog/gofix) - the modernisers `minmax`, `rangeint` and
    `stringscut`; `go fix ./...` updating files silently and discarding fixes
    that touch generated files; the `-diff` preview; and the semantic conflicts
    that surface as compilation errors. - [Go 1.25 release
    notes](https://go.dev/doc/go1.25) - tools not invoked by build or test being
    built and run by `go tool` as needed, and the `go.mod` `ignore` directive.
