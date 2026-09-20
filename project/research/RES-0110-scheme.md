---
id: RES-0110
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Scheme

## Summary

The language is standardised and the implementations are not, so the tools do
not transfer between them. The finding that shapes everything else is that a
command from the wrong implementation frequently succeeds and does something
else, and fails for nobody, which makes an unresolved verb strictly better than
a guessed one here. One implementation has a real toolchain with coverage; the
others have a toolkit and a portable test library, and no runner.

Research for one supported language. A toolchain is a set of tools, and Scheme
has several disjoint ones: the language is standardised and the implementations
are not, so the tools do not transfer between them and one implementation's
command frequently succeeds under another while doing something else.

It covers what marks a Scheme project, why the implementation has to be
identified before any verb resolves, what each implementation's tools are, what
the pack authors, and what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

R7RS fixes the language. Everything a pack needs - how a library is declared,
how a module is compiled, how a test is run, how coverage is measured - belongs
to the implementation, and the implementations disagree.

So the question is what happens when a pack cannot tell which Scheme it is
looking at, and the answer here is stronger than elsewhere: it must stop.

## Method

The documentation of the one implementation with a dispatching driver was
fetched and read on 2026-09-20: its command reference, its test command's
discovery and isolation model, its formatter and its coverage tool.

The other implementations were not read to the same depth. Their entries come
from the standard and from general knowledge of their tooling, which is a real
asymmetry in this document and is why the per-implementation table is thinner
outside the first column.

One search was used to confirm the formatter and coverage tools exist and are
current. Nothing was installed or run.

## Findings

### The markers name a file type

`*.scm`, `*.ss`, `*.sld` and `*.rkt` mark Scheme source. Only two lean towards
an implementation: `.rkt` is Racket's, and `.sld` is the R7RS library
declaration that several implementations read.

The files that identify one are the manifests: `info.rkt` for Racket, `guix.scm`
for a Guix package, an egg file for Chicken, a `.sld` naming a library the
implementation's loader understands.

A directory of `.scm` files with no manifest is Scheme whose implementation is
unknown, and that is the common case in a repository where the Scheme
configures something and is never the product.

### Guessing fails silently here, which is the finding that shapes everything else

In most languages a command from the wrong toolchain fails to run. In Scheme it
frequently succeeds and does something else: the file loads, the top-level
forms evaluate, the definitions that depend on the absent feature are never
reached, and the run exits zero.

That makes an unresolved verb strictly better than a guessed one, and it is the
sharpest case of a rule that holds generally.

### Racket has a real toolchain; the others have a toolkit

Racket is the outlier in having one command that dispatches subcommands, and
the set is comparable with any other language in this survey.

| Role       | Racket                                           | Elsewhere                                 |
| ---------- | ------------------------------------------------ | ----------------------------------------- |
| Format     | `raco fmt`, from the `fmt` package               | `schemat`, `scmindent`, or nothing        |
| Lint       | the compiler's warnings, Typed Racket where used | the implementation's, if any              |
| Compile    | `raco make`                                      | `guild compile`, `csc`, `compile-program` |
| Executable | `raco exe`, `raco distribute`                    | implementation-specific or absent         |
| Test       | `raco test` with RackUnit                        | SRFI-64, the `test` egg, `gauche.test`    |
| Coverage   | `raco cover`                                     | rarely anything                           |
| Packages   | `raco pkg`, `raco setup`                         | `guix`, `chicken-install`, none           |
| Docs       | Scribble, `raco docs`                            | implementation-specific                   |

`raco fmt` lexes with `syntax-color/module-lexer` and lays the result out with
an expressive pretty printer, writing to standard output, and editing nothing
in place - which is a detail a pack must know, because a `fmt` verb that
expects the file to be rewritten will find it unchanged.

`raco cover` runs each file and its `test` submodule and writes coverage into a
directory, HTML by default. That is a real coverage story, and it is the only
one in this document.

### `raco test` has a discovery model, and the model is the interesting part

`raco test` _"requires and runs the (by default) test submodule associated with
each path given on the command line"_. Given a directory it recursively finds
`.rkt`, `.scrbl`, `.ss` and `.scm` files, plus files named in
`test-command-line-arguments` in `info.rkt`.

`info.rkt` controls discovery through `test-omit-paths`, `test-include-paths`
and `test-command-line-arguments`. So the project declares what its tests are,
and no convention says, which is the same shape as a task runner and should be
read the same way.

Its execution model is configurable in a way that matters for isolation:
`--direct` in one thread, `--process` in a separate operating-system process
per test - the default for multiple files - or `--place`. `-j` sets
concurrency, `--timeout` bounds a run, and `-e` treats output on standard error
as a failure with `++ignore-stderr` to exempt patterns.

Machine-readable output is the gap. `--table` prints a summary of test and
failure counts, and `raco/testing` exposes `test-log!` for logging results
programmatically, which is the integration point a harness would use rather
than a report format it can read.

### The test story elsewhere is a library

SRFI-64 is a portable testing library, and it runs nothing. The command is
_evaluate this file with this implementation_, and the result is whatever the
file printed. The `test` egg for Chicken and `gauche.test` are equivalents with
the same property.

So for every implementation but Racket, a harness collecting evidence is
capturing output and an exit status, and any structure in it was arranged by
the project.

### Portability is the recurring defect, and it lives in the library declaration

The difference between a library, a module and a script is implementation
specific, and it is where portable-looking code stops being portable. A file
that is a script under one implementation is a library under another and never
runs its body.

Which SRFIs are assumed is the real dependency list, and it is usually written
nowhere. A file using SRFI-1's `fold` depends on a library the implementation
may not load by default.

### What the pack authors

The implementation's manifest: `info.rkt` for Racket - including the test
discovery keys, which is the highest-value edit a pack can make there - a
`.sld` library declaration, an egg file, or a `guix.scm`.

It does not author a portable configuration, because none exists.

### What a reviewer needs that no command reports

Tail position, and therefore where recursion is safe and where it is a stack
overflow waiting for a larger input. Nothing reports this and the code looks
identical either way.

Hygienic macros: what `syntax-rules` can express, and when `syntax-case` or an
explicit renamer is needed - which is also where portability breaks, since not
every implementation has the latter.

Continuations, and what `call/cc` does to resource cleanup and to
`dynamic-wind`.

Mutation as the exception, where the default is a value nobody changes, which
is a convention a reviewer enforces and no tool does.

Which SRFIs the file assumes, since that is the dependency list nobody wrote.

### What the skill has to contain

In the body, in this order:

1. Identify the implementation, before anything else, and the rule that every
   verb is unresolved until it is identified. 2. Why guessing is worse here, in
   one sentence with the mechanism: a command from the wrong implementation
   succeeds and does something else. 3. Per-implementation verb resolution,
   with Racket's dispatching driver separated from everyone else's assembled
   toolkit. 4. The two operational surprises. `raco fmt` writes to standard
   output and rewrites nothing; `raco test` discovery is declared in
   `info.rkt`. 5. What must never happen. Running a command from one
   implementation against another's project. Reporting a zero exit from a
   wrong-implementation run as a pass. Claiming coverage anywhere but Racket.

In supporting files: the per-implementation tool table; the `info.rkt` keys
that control test discovery; the evidence story per implementation; the
reviewer's knowledge; and the dated facts with what to re-check.

## Conclusions

1. The implementation is identified before any verb resolves, and where it
   cannot be, every verb is reported unresolved. 2. The manifest identifies the
   implementation, and the file extension identifies nothing. `info.rkt`,
   `guix.scm`, an egg file or a `.sld` library declaration say which Scheme;
   `.scm` says only that it is Scheme. 3. A command from the wrong
   implementation is worse than no command, because it frequently succeeds and
   does the wrong thing, failing for nobody, so a zero exit status from an
   unidentified implementation is not evidence. 4. Racket is the one
   implementation with a dispatching driver, covering formatting, testing,
   coverage, compilation, executables, packages and documentation. 5. `raco
fmt` writes to standard output and edits nothing in place, so a `fmt` verb
   that expects a rewritten file finds it unchanged. 6. `raco test` discovery
   is declared in `info.rkt` through `test-omit-paths`, `test-include-paths`
   and `test-command-line-arguments`, and the pack reads that declaration,
   inferring nothing from the file tree. 7. Test isolation in Racket is a
   choice and is stated. `--process` is the default for multiple files,
   `--direct` and `--place` are alternatives, and `-e` makes output on standard
   error a failure. 8. Evidence in Racket is `--table` plus `test-log!`,
   because there is no report format to read, and elsewhere it is captured
   output and an exit status. 9. Coverage exists in Racket and effectively
   nowhere else, which the pack reports and glosses over nowhere. 10. Elsewhere
   `test` means evaluating a file under the implementation, since SRFI-64 is a
   library that runs nothing. 11. The assumed SRFIs are the real dependency
   list and are reported where they are not declared. 12. The distinction
   between a library, a module and a script is the commonest portability
   defect, because a file that is a script under one implementation is a
   library under another and never runs. 13. No portable configuration is
   authored, because none exists; the pack writes the implementation's manifest
   or nothing. 14. The reviewer's knowledge is recorded with the pack: tail
   position, hygienic macros and what `syntax-rules` cannot express,
   continuations against `dynamic-wind`, mutation as the exception, and the
   assumed SRFIs. 15. The skill body carries implementation identification, the
   reason guessing is worse here, per-implementation resolution, the two
   operational surprises, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [The raco command reference](https://docs.racket-lang.org/raco/index.html) -
  `raco make` compiling source to bytecode; `raco exe` producing a stand-alone
  executable that runs without Racket installed; `raco test` running tests with
  configuration through submodules or `info.rkt`; and `raco pkg` and `raco
setup` for packages and installation.
- [raco test](https://docs.racket-lang.org/raco/test.html) - running the `test`
  submodule associated with each path; recursive discovery of `.rkt`, `.scrbl`,
  `.ss` and `.scm` files in a directory; `test-omit-paths`,
  `test-include-paths` and `test-command-line-arguments` in `info.rkt`; the
  `--direct`, `--process` and `--place` execution modes with `--process` as the
  default for multiple files; `-j`, `--timeout`, `-e` and `++ignore-stderr`;
  and `--table` plus `raco/testing`'s `test-log!` as the reporting surface.
- [fmt, an extensible code formatter for Racket](https://docs.racket-lang.org/fmt/index.html)
  - `raco fmt` lexing with `syntax-color/module-lexer`, laying out with an
    expressive pretty printer, and displaying the formatted program to standard
    output.
- [Cover, a test coverage tool](https://docs.racket-lang.org/cover/index.html)
  and [Basic usage of Cover](https://docs.racket-lang.org/cover/basics.html) -
  `raco cover` running each file and its `test` submodule and writing coverage
  into a directory, as HTML by default.
- [R7RS small language report](https://small.r7rs.org/) - the standard that
  fixes the language and the `define-library` form the `.sld` files declare,
  while leaving the tooling to each implementation.
