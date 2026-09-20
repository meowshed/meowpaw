---
id: RES-0109
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Starlark

## Summary

Starlark has a specification and no toolchain: the runtime is somebody else's
program, and the same file may be evaluated by three implementations with
different builtins. The specification is unusually strong, and it is what the
pack sells: deterministic, hermetic, values frozen after load, no recursion, no
unbounded loop. Every one of those is a defect class a reviewer can look for.
One formatter is shared, and it belongs to one host.

Research for one supported language. A toolchain is a set of tools, and this
one belongs to somebody else. Starlark has a specification and several
independent implementations, each embedded in a different host, and the tools
come from whichever host you are standing in.

It covers what marks a Starlark project, why only one verb has a widely shared
tool, and what the specification guarantees a reviewer can rely on. It also
covers what a build system does with linting when linting is itself a build
action, what the pack authors, and what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

Every other language in this survey runs its own code. Starlark's runtime is a
program somebody else wrote, and the same file may be evaluated by three
implementations with different builtins.

So the question is what a pack can promise when the language is a guest.

## Method

The specification was fetched and read in raw form on 2026-09-20, and is
quoted rather than paraphrased because the guarantees are the document's
contribution.

The formatter's documentation and the build tools' overview were fetched for
the tool behaviour, and the reference implementation's repository was read for
its stated limitation that it knows only standard Starlark.

One claim could not be verified: a search index lists the project's roadmap as
carrying a known weakness in the editing tool, and the page does not resolve.
It is recorded as reported and unverified, and the conclusion drawn from it is
weakened accordingly.

Nothing was installed or run.

## Findings

### The specification is unusually strong, and that is what the pack sells

The specification states the two properties the language exists for:

> The language is deterministic and hermetic. Executing the same file with the
> same interpreter leads to the same result. By default, user code cannot
> interact with the environment.

Three restrictions enforce it. Values freeze:

> Immediately after execution of a Starlark module, all values in its top-level
> environment are frozen.

That is what makes parallel evaluation safe without locking, and it is also the
defect class a reviewer looks for: code that mutates a module-level value works
during load and fails afterwards.

Recursion is forbidden: _"It is a dynamic error for a function to call itself
or another function value with the same declaration"_. No `while` statement
exists either, only `for` over finite sequences, so every program finishes.

And it is deliberately not Python, despite looking like it. _"Starlark syntax
is a strict subset of Python"_ with semantics that diverge: no user-defined
types, no inheritance, no reflection, no exceptions, static name resolution,
non-iterable strings.

Every one of those is a finding a reviewer can look for and no verb reports.

### One tool is shared, and it belongs to one host

`buildifier` is Bazel's and is the only widely shared Starlark tool. It formats
`BUILD`, `BUILD.bazel`, `WORKSPACE`, `.bzl` and unrecognised Starlark files,
detecting the type from the filename, with `WORKSPACE` formatted as `BUILD` is
and default files as `.bzl` files are. It lints with `--lint=warn` to report
and `--lint=fix` to apply, with the stated caveat that some findings cannot be
fixed automatically, and `--warnings` takes categories with `+` and `-`
modifiers.

Machine-readable output through `--format=json` works only with `--mode=check`.
A verb that needs a parseable result rather than a terminal dump uses the check
mode, and a pack that asks for JSON without it gets nothing.

`buildozer` is the other half of the same repository, and it is the tool a pack
needs for authoring. It applies commands - add, remove, set, rename - to
targets in `BUILD` files programmatically, which is how a build file is edited
without a text rewrite.

This document records its reported weakness carefully, because the source for
it could not be read. A search index lists Bazel's Starlark roadmap as carrying
buildozer's reliability around `select` and variables as a priority item, and
the page that would confirm it no longer resolves. So this document records it
as reported and unverified. A `BUILD` file whose attributes are computed may be
one buildozer cannot edit correctly, and a pack verifies the result of an edit
and assumes nothing.

`unused_deps` analyses Java dependencies declared but not used, which is
narrower than its name suggests, so nobody should expect it to generalise.

### The other verbs have no tool, and inventing one would be worse than reporting none

| Verb        | Command                                              |
| ----------- | ---------------------------------------------------- |
| `fmt`       | `buildifier`                                         |
| `lint`      | `buildifier --lint=warn`, with `--lint=fix` to apply |
| `typecheck` | unresolved - the language has no static types        |
| `test`      | the host's own evaluator; no standard runner exists  |
| `build`     | the host's, where the host is a build system         |

`typecheck` is unresolved as a property of the language; `test` is unresolved as
a property of the situation. The two deserve different words in a report,
because one will never resolve and the other might if the host is identified.

### The implementations differ, and the differences fail at evaluation

Bazel's build language, `starlark-go` and `starlark-rust` are independent
implementations of the same specification. `starlark-rust` ships a binary
providing _"interactive evaluation, IDE features and linter, exposed through a
command line"_. It also states the limitation that decides everything: _"the
starlark_bin binary is only aware of standard Starlark."_ It knows nothing of
the domain functions and types a host embeds.

So a file that reads correctly, formats cleanly under `buildifier` and passes
`starlark_bin`'s linter may call a function its actual evaluator does not have.
Detecting the host is part of detecting the language, and treating every
`.star` file as Bazel's is wrong in exactly the cases that matter.

### Where the build system is the host, linting becomes a build action

`rules_lint` answers a question this harness also has. It _"integrates linting
and formatting as first-class concepts under Bazel"_ through aspects attached
to existing targets, and it changes no ruleset and no `BUILD` file. The checks
run as ordinary Bazel actions, so they are incremental and work under remote
execution, and it lints only changed files under what it calls the water leak
principle.

Its taxonomy of lint against format is the part to carry:

|                       | Lint                          | Format                        |
| --------------------- | ----------------------------- | ----------------------------- |
| How many per language | Several, composing results    | One, to avoid conflicts       |
| Effect on the program | A suggested fix may change it | Never changes behaviour       |
| Suppression           | A violation may be suppressed | A change must apply           |
| Scope                 | May cover unchanged files     | May target changed files only |

That is a sharper statement of the distinction than this project had, and it
arrives from a build system rather than from a style guide.

### What the pack authors

`.bzl` libraries, `BUILD` files and `MODULE.bazel`, and it authors them through
`buildozer` and never as text wherever buildozer can express the change. The
unverified report about `select` and variables is a reason to verify an edit,
and never to discover the problem later.

### What a reviewer needs that no command reports

The specification's guarantees, listed above, each as a defect class: mutation
after freezing, anything resembling recursion, and anything reading a clock, a
filesystem or an environment, which is either a host builtin or a defect.

Which host evaluates this file, and therefore which builtins exist.

`load()` resolution, which is host-specific and is where a copied snippet stops
working.

Whether a macro should have been a rule, which is the recurring Bazel-specific
design question and has no tool at all.

### What the skill has to contain

In the body, in this order:

1. Detection, host first. The file markers, and then which implementation
   evaluates them, because the second decides what the first means.
2. Verb resolution, with the two kinds of unresolved distinguished: the
   language has no such thing, against the host has not been identified.
3. The specification's guarantees as a checklist, because they are the
   review, and they are short enough to sit in the body.
4. The machine-readable rule. `--format=json` needs `--mode=check`.
5. What must never happen. Treating every `.star` file as Bazel's.
   Rewriting a `BUILD` file as text where buildozer could do it. Claiming a
   type check.

In supporting files: the tool inventory, the buildifier warning categories, and
buildozer command recipes with the `select` caveat. Also the rules_lint
taxonomy for projects where Bazel is the host, the reviewer's knowledge, and
the dated facts with what to re-check.

## Conclusions

1. A Starlark project is marked by `*.star`, `*.bzl`, `BUILD`,
   `BUILD.bazel` and `MODULE.bazel`, and the host that embeds the language is
   detected alongside them.
2. The host is part of the detection. The implementations differ in
   builtins and in `load()` resolution, so a file that formats cleanly may call
   a function its evaluator does not have.
3. A standard-Starlark linter is not a check of the file as evaluated,
   because the reference binary states it knows only standard Starlark and
   nothing a host embeds.
4. `fmt` and `lint` resolve to `buildifier`, which detects the file type
   from the name and formats `WORKSPACE` as `BUILD` and default files as
   `.bzl`.
5. A machine-readable result uses `--mode=check`, because `--format=json`
   works only in combination with it.
6. `typecheck` is unresolved because the language has no static types,
   which is a different report from a verb whose tool is merely absent.
7. `test` and `build` are unresolved and the reason is the host, so the
   report names the host rather than the language.
8. Authoring goes through `buildozer` rather than text editing, because a
   `BUILD` file is structured and a text rewrite loses that structure.
9. A buildozer edit is verified rather than assumed, because its reported
   unreliability around `select` and variables could not be confirmed from a
   readable source and is carried as unverified.
10. `unused_deps` is recorded as Java-specific, so nothing expects it to
    generalise.
11. The specification's guarantees are the review: frozen values,
    no recursion, no `while`, and no interaction with the environment except
    through host builtins.
12. Anything reading a clock, a filesystem or an environment is a defect
    unless the host supplied it, because the language's stated purpose is
    that it cannot.
13. Where the build system is the host, linting is a build action, which
    makes it incremental, remotely executable and scopeable to changed files.
14. The lint-against-format distinction is taken as stated: several linters
    compose and one formatter does not, a lint fix may change the program and a
    format never does, a lint violation may be suppressed and a format change
    must apply.
15. The skill body carries host-first detection, verb resolution with the two
    kinds of unresolved, the specification checklist, the machine-readable
    rule, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [The Starlark specification](https://raw.githubusercontent.com/bazelbuild/starlark/master/spec.md)
  - that the language is deterministic and hermetic and that user code cannot
    interact with the environment by default; that all top-level values are
    frozen immediately after a module executes, which is what makes parallel
    evaluation safe; that a function calling itself is a dynamic error; that
    iteration is `for` over finite sequences with no `while` statement; and that
    the syntax is a strict subset of Python while the semantics differ in
    user-defined types, inheritance, reflection, exceptions, name resolution and
    string iteration.
- [buildifier](https://github.com/bazelbuild/buildtools/blob/master/buildifier/README.md)
  - formatting for `BUILD`, `WORKSPACE`, `.bzl` and unrecognised Starlark files
    with the type detected from the filename; `--lint=warn` and `--lint=fix` with
    the caveat that some findings cannot be fixed automatically; the `--warnings`
    flag with category modifiers; and that `--format=json` works only in
    combination with `--mode=check`.
- [bazelbuild/buildtools](https://deepwiki.com/bazelbuild/buildtools) -
  buildifier as the standard formatter and linter for `BUILD`, `WORKSPACE` and
  `.bzl` files; buildozer as a command interface for programmatic editing with
  add, remove, set and rename operations; and `unused_deps` as an analysis of
  declared but unused Java dependencies in `java_library` rules.
- The Bazel Starlark roadmap - reported by a search index as listing
  buildozer's reliability around `select` and variables as a priority item.
  **The page does not resolve** at the address the index gives, checked
  2026-09-20, so this is recorded as reported and unverified rather than
  cited.
- [starlark-rust](https://github.com/facebook/starlark-rust) - the binary
  providing interactive evaluation, IDE features through the language server
  protocol, a debugger through the debug adapter protocol, and a linter; and
  the stated limitation that it is aware only of standard Starlark and lacks
  the domain functions and types a custom embedding provides.
- [rules_lint](https://github.com/aspect-build/rules_lint) - linting and
  formatting as first-class concepts under Bazel through aspects, needing no
  changes to rulesets or `BUILD` files; lint checks as ordinary actions that
  are incremental and work under remote execution; results presentable as
  review comments, failing tests or command-line output; linting only changed
  files under the water leak principle; and the stated differences between lint
  and format in quantity per language, effect on program behaviour,
  suppressibility and scope.
