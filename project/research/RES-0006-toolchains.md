---
id: RES-0006
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Verification toolchains

## Summary

Eleven ecosystems answer the same four questions, and the five verbs covered
every one of them with no sixth required. The four are what marks the project,
what the verbs resolve to, what the pack authors, and what a reviewer needs.
Where a language lacks a tool for a verb, the verb does not resolve, and the
two reasons for that are different reports: nothing can resolve it, or nothing
has. Command names barely moved in three years; what moved is what the same
command does.

The shape every toolchain pack shares: what identifies a project, what the five
verbs resolve to, what the pack must be able to author, and what a reviewer
needs that no command reports.

One language per document. This one holds what is true across all of them, and
the survey of what the existing provisioning already installs.

## The question

The harness claims to support a set of languages and tools. That claim holds
only if the same four questions have an answer for each of them, and a reader
can trust it only where a stale answer shows as stale.

So: what are the four questions, and what happens when one of them has no
answer.

## The documents

| Language                  | Document                                                                       |
| ------------------------- | ------------------------------------------------------------------------------ |
| Rust                      | [RES-0101-rust.md](RES-0101-rust.md)                                           |
| Go                        | [RES-0102-go.md](RES-0102-go.md)                                               |
| Python                    | [RES-0103-python.md](RES-0103-python.md)                                       |
| TypeScript and JavaScript | [RES-0104-typescript-and-javascript.md](RES-0104-typescript-and-javascript.md) |
| C#                        | [RES-0105-csharp.md](RES-0105-csharp.md)                                       |
| Lua                       | [RES-0106-lua.md](RES-0106-lua.md)                                             |
| Neovim plugins            | [RES-0107-neovim-plugins.md](RES-0107-neovim-plugins.md)                       |
| Godot and GDScript        | [RES-0108-godot-and-gdscript.md](RES-0108-godot-and-gdscript.md)               |
| Starlark                  | [RES-0109-starlark.md](RES-0109-starlark.md)                                   |
| Scheme                    | [RES-0110-scheme.md](RES-0110-scheme.md)                                       |
| Markdown                  | [RES-0111-markdown.md](RES-0111-markdown.md)                                   |

## Method

This document holds what is true across the eleven per-language documents,
each of which carries its own sources and read date. It states nothing about a
language that is not stated there, so its method is theirs.

Its own additional source is the provisioning. We read the components and
bundles of the internal standard library from its working tree on 2026-09-20
for the availability survey, which lists what is installed and claims nothing
about what works.

Nothing was run for this document.

## Findings

### The four questions, and why they are these four

What marks the project. A marker file identifies a toolchain without guessing,
which is what lets several languages in one repository resolve per location,
where one answer for the whole tree would be wrong.

What the verbs resolve to. Five commands, or fewer where the language has
no tool for one of them.

What the pack authors. Running a tool is not enough. Every ecosystem's most
common change is a change to its own configuration, and a pack that invokes a
build but cannot add a task to it leaves that change unsupported.

What a reviewer needs. Knowledge that differs per language and is not derivable
from the verbs. No documentation generates this part, which is why somebody
writes each document and nothing scrapes it.

### A verb with no tool does not resolve, and the reason is reported

Across eleven languages the five verbs were enough and no language needed a
sixth. Several languages lack a tool for one verb, and the answer in every case
is that the verb does not resolve.

The surveys separate two reasons for that, and the reports read differently:

- **The language has no such thing.** Starlark and Markdown have no static
  types; most Lua projects have no build. Nothing will ever resolve these.
- **The project has not said.** Python's type checker, Scheme's
  implementation, a `make` target that might be the test. Something could
  resolve these and nothing has.

Guessing is worse than reporting in both cases, and worst in Scheme, where a
command from the wrong implementation frequently succeeds and does the wrong
thing, and fails for nobody.

### Type checking is the verb with the least convergence

In Rust, Go and C# it is the compiler, and the honest resolution says so rather
than naming a tool that adds nothing. In Python four credible checkers disagree
about what is an error. In Lua it is a language server pointed at a runtime
declaration. In Starlark and Markdown it is nothing.

That is why the resolution order consults the repository's own declaration
before any detection: the detection is right for three languages and wrong for
one, and the declaration is right for all of them.

### The configuration goes stale, and the command does not

The command names in this survey barely changed over three years. What changed
is what the same command does: a reorganised configuration file, a removed
configuration format, a renamed binary, a new default edition.

So every pack states what it is current as of. A reader in a year needs to know
what to re-check, where being told to trust it helps nobody.

### A fact about a tool taken from a rival is an interested source

Two of the language documents record a claim made by one tool about another
that was wrong or stale when checked. The rule that came out of it: a
comparison page is a primary source about its own tool and a secondary,
interested source about everything else.

## Availability under the existing provisioning

`meowctl-stdlib` already ships components for many of these, which decides how
much work a pack costs to make usable, where correctness alone is cheaper.

Present: `git`, `gh`, `jj`, `worktrunk`, `mise`, `just`, `make`, `node`,
`go`, `golangci_lint`, `gopls`, `rust`, `rust_analyzer`, `uv`, `ruff`,
`pyright`, `python`, `lua_language_server`, `luarocks`, `stylua`, `godot`,
`neovim`, `tree_sitter`, `difftastic`, `delta`, `pre_commit`, `shellcheck`,
`shfmt`, `gitleaks`, plus `rust-development`, `go-development`,
`python-development` and `lua-development` bundles.

Absent, and needed by a pack named in the design: `qmd`, `repomix`,
`task` (go-task), `buildifier`, `cargo-nextest`, `cargo-deny`, `gdtoolkit`,
`selene`, `busted`, `vusted`, `markdownlint-cli2`, `codespell`, `lychee`,
`biome`, `oxlint`, `dotnet`, a type checker for the `ty` and `mypy` case, and a
Scheme implementation - `racket` or `guile` - for `meow-scheme`.

Every one of those except `dotnet` installs through `mise`, which is the
preferred route. It keeps the version in the project's own `mise.toml`, where a
runner pack can already read it, and never in a machine-level package manager.
`git` is the exception in the other direction - it is assumed present and
installed by nothing.

## Conclusions

1. The five verbs cover every language surveyed, and no language needed a
   sixth. Where a language has no tool for a verb, the answer is that the verb
   does not resolve, and never that the verb does not exist. 2. Type checking
   is the verb with the least convergence. Several languages have one obvious
   answer and one has none, so the resolution order must consult the
   repository's own declaration before any detection. 3. A marker file
   identifies a toolchain reliably, which is what makes detection possible
   without guessing, and what lets several languages in one repository resolve
   per location, where one answer for the whole tree would be wrong. 4. Running
   a tool is not enough. Every ecosystem's most common change is to its own
   configuration, so a pack that can invoke a build but cannot add a task to it
   leaves that change unsupported. 5. A pack carries reviewer knowledge as well
   as commands. What a reviewer must know differs per language and is not
   derivable from the verbs. 6. Version facts go stale fastest. Every pack
   states what it is current as of, because a toolchain's defaults change under
   the same command name. 7. The provisioning already covers most of the
   toolchains and not all of them. What is missing is enumerable, installable
   through the project's own toolchain manager, and therefore a task somebody
   can schedule. 8. An unresolved verb states which kind of unresolved it is:
   nothing can resolve it, or nothing has. The two are different reports and
   lead to different actions. 9. A comparison a tool publishes about a rival is
   an interested source, and is checked against the rival before it is
   repeated.

## Sources

All read 2026-09-20.

- The eleven language documents listed above, each carrying its own sources and
  its own read date. This document states nothing about a language that is not
  stated there.
- `~/workspace/meowctl-stdlib/components/` and `bundles/` - the components and
  bundles the existing provisioning ships, read for the availability survey.
