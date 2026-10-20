---
id: RES-0364
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0102
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# What the go command decides for the Go pack

## Summary

`gofmt` and `golangci-lint fmt` document no exit status for a file that needs
formatting, so a format check reads `gofmt -l`'s output, and the documented
part of golangci-lint is that `run` reports its formatters' issues. A
workspace has no `./...` that reaches every module, so a command run from the
root of a `go.work` covers one module or none. `go test` runs an example that
carries an `Output:` comment. The `toolchain` line in `go.mod` names the
toolchain the go command switches to, and `GOTOOLCHAIN=local` turns the
switch off. This adds to RES-0102 what the Go pack needs to bind its stages.

## The question

RES-0102 gives the commands each stage resolves to, among them `gofmt -l -w .`
for `format`, which rewrites files, so it can't serve a check. It doesn't say
how a check learns that a file is unformatted, how a command reaches each
module of a workspace, whether `go test` runs the examples in the
documentation, or how a pinned toolchain is read.

## Method

I read the vendor pages listed under Sources on 2026-10-13 and searched for
the exit status of `golangci-lint fmt --diff` and for the workspace pattern.
Nothing was installed or run. The search found no page stating either exit
status, which is recorded as a gap and not filled by a guess.

## Findings

### A format check reads `gofmt -l`, because no exit status is documented

The `gofmt` page says `-l` prints a file's name "If a file's formatting is
different from gofmt's", `-d` prints the difference, and `-w` overwrites the
file. It states no exit status for a difference. A check that fails on a
difference therefore fails on what `-l` prints, as in
`out=$(gofmt -l .) && test -z "$out"`, which also fails where `gofmt` itself
exits non-zero.

golangci-lint's command reference gives `fmt --diff` as "Display diffs
instead of rewriting files" and states no exit status for it. Its formatters
page says `run` "executes enabled linters and the formatters defined in
formatters, but it does not format the code", and `run --issues-exit-code`
defaults to 1.

### A workspace has no `./...` across its modules

`go help` describes a workspace as a `go.work` file whose `use` directives
name module directories, used "as root modules". Go issue 50745 states there
is "no equivalent of `./...` in workspace mode", and issue 71294 proposes a
`work` pattern, accepted for Go 1.25. I found no release note confirming it
shipped.

### `go test` runs an example that states its output

The `testing` package says an example with a concluding `Output:` comment is
compiled and run, its standard output compared with the comment, and
"Example functions without output comments are compiled but not executed".

### The `toolchain` line is the pinned toolchain, and `GOTOOLCHAIN=local` stops the switch

The toolchain page says the `toolchain` line "declares a suggested toolchain",
which the go command runs where the default toolchain is older, and a
`go.mod` without one behaves as if it had `toolchain go<V>` for its `go`
line's version. `GOTOOLCHAIN=local` "always runs the bundled Go toolchain",
and a toolchain refuses to run a module that requires a newer Go version.

### `-C` and `go tool` place and name a command

The go command's page says `-C dir` changes to `dir` before running and must
be the first flag. `go tool` runs a tool declared by a `tool` directive by its
full package path, or by its last path component "if it is unique among
declared tools". `go build` writes an executable for a single main package and
discards the result for several packages, and `-race` is supported only on
some platforms.

## Conclusions

1. A `format` check bound to `gofmt` fails on what `gofmt -l` prints, and
   never relies on its exit status for a difference.
2. A `format` stage configured through golangci-lint's `formatters` section
   has no documented check command, so it is reported unresolved, and the
   `lint` stage's `golangci-lint run` reports those formatters' issues.
3. A repository whose root holds a `go.work`, or several `go.mod` files with
   no `go.work`, has no single command reaching each module from the root.
4. `go test` runs each documentation example that states its output, so a
   `test` stage bound to it runs them.
5. A pinned Go toolchain is the `toolchain` line of `go.mod`, or the `go`
   line where there is none, and `GOTOOLCHAIN=local go version` reports the
   installed one without switching.
6. A tool a `tool` directive declares runs as `go tool <name>`.

## Sources

- Read 2026-10-13: [gofmt](https://pkg.go.dev/cmd/gofmt) - the `-l`, `-d` and `-w` flags, and
  no stated exit status for a difference.
- Read 2026-10-13: [golangci-lint, command line](https://golangci-lint.run/docs/configuration/cli/) -
  `fmt --diff` with no stated exit status, and `run --issues-exit-code`.
- Read 2026-10-13: [golangci-lint, formatters](https://golangci-lint.run/usage/formatters) -
  that `run` executes the linters and the formatters a configuration enables
  and formats nothing.
- Read 2026-10-13: [The go command](https://pkg.go.dev/cmd/go) - `-C`, `go tool` naming,
  what `go build` writes, workspaces, and `-race`'s platforms.
- Read 2026-10-13: [Go issue 50745](https://golang.org/issue/50745) and
  [Go issue 71294](https://go.dev/issue/71294) - no `./...` across a
  workspace, and the proposed `work` pattern.
- Read 2026-10-13: [testing, Examples](https://pkg.go.dev/testing) - which examples `go test`
  runs and which it only compiles.
- Read 2026-10-13: [Go toolchains](https://go.dev/doc/toolchain) - the `toolchain` line,
  `GOTOOLCHAIN=local` and `auto`, and the refusal to run a module needing a
  newer Go.
