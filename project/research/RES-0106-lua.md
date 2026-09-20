---
id: RES-0106
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Lua

## Summary

Lua ships an interpreter and nothing else, so every verb resolves to a tool
the project installed and there is frequently nothing that says which. The two
linters check different sets on purpose, so substituting one silently drops
checks. And the type verb is unlike every other in the survey: it writes its
findings to a log file, defaults that path inside the repository, and hides two
severities at its default level.

Research for one supported language. A toolchain is a set of tools, and Lua's
is assembled entirely from third-party pieces, several maintained by one
person, against four incompatible versions of the language in production use at
once.

It covers what marks a Lua project, what each verb resolves to, and why the two
linters are not interchangeable. It also covers how the type verb reports its
results, what the pack authors, and what the skill has to contain.

It does not cover Neovim plugins, which are a Lua project plus a platform and
are [RES-0107-neovim-plugins.md](RES-0107-neovim-plugins.md), nor what every
toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

Lua ships an interpreter and nothing else. Every verb resolves to a tool the
project installed, and the language has no manifest, so there is frequently
nothing that says which tools those are.

So the question is what a pack may assume when the project has said nothing,
and the answer turns out to be less than in any other language here.

## Method

We fetched and read the vendor documentation on 2026-09-20. The language
server's usage and configuration pages gave the log path, the check level and
the configuration override, and one linter's own comparison page gave the rest.

That comparison page makes a claim about its rival that was checked against the
rival's repository and found stale. We cite both and record the contradiction
here, resolving it silently nowhere.

One search was used to survey the wider tool set. Nothing was installed or
run.

## Findings

### The markers are configuration files, because the language has no manifest

`.luarc.json`, `*.rockspec`, `stylua.toml` or `.stylua.toml`, `.luacheckrc`,
`selene.toml` and `.busted` each mark a Lua project, and a project may have any
subset including none. A directory of `.lua` files with no configuration is a
Lua project that has chosen no tools.

That is unlike every other language here and it decides the pack's default
posture: detect what is configured, report the verbs that do not resolve, and
do not assume a stack.

A `*.rockspec` is the closest thing to a manifest. It declares the package, its
dependencies and its build rule, and it is the only file in the list that says
what the project _is_, where the others say how a tool should treat it.

### The language version is load-bearing and is rarely written down

Lua 5.1, 5.2, 5.3, 5.4 and LuaJIT are all in use. They differ in integer
division, in `goto`, in the bitwise operators, in `setfenv` against `_ENV`, and
in how varargs are handled. Code that passes review under one fails at run time
under another.

luacheck supports Lua 5.1 through 5.4 and LuaJIT, told which through its
standard-library setting. selene is explicit about the opposite choice: it
declines Lua versions beyond 5.1, citing limited demand.

So the version is not a detail a pack can defer. A project that has not stated
one has a linter guessing, and the guess differs per linter.

### The toolchain, tool by tool

| Role          | Tool                          | What only it answers                                             |
| ------------- | ----------------------------- | ---------------------------------------------------------------- |
| Interpreter   | `lua`, `luajit`               | What the code actually runs on                                   |
| Packages      | `luarocks`                    | Dependencies, and installing the rest of this table              |
| Format        | `stylua`                      | The canonical form, with `--check` to verify                     |
| Lint          | `selene`                      | Standard-library-aware calls: argument types and counts          |
| Lint          | `luacheck`                    | Undefined globals, unused values, whitespace and line length     |
| Typecheck     | `lua-language-server --check` | Diagnostics from the annotations and the declared runtime        |
| Typecheck     | `llscheck`                    | The same, wrapped into a usable exit status and report           |
| Typed dialect | `teal`                        | Static types, for a project that opted into a different language |
| Test          | `busted`                      | The tests, with the idiomatic describe-and-it shape              |
| Test          | `luaunit`                     | The same for a project that chose it                             |
| Coverage      | `luacov`                      | Which code paths a run did not reach                             |
| Docs          | `ldoc`                        | The generated API documentation                                  |

Nothing in this table ships with the interpreter. The consequence is that every
verb has a real chance of being unresolved on a given machine, and a pack that
reports that honestly is more useful than one that fails.

### The two linters differ in what they will lint, on purpose

selene's own comparison states its position. Written in Rust against luacheck's
Lua, faster and multithreaded. Configured in TOML, where a `.luacheckrc`
executes Lua, and its lints are named where luacheck numbers them. Its
standard-library mechanism configures argument types and counts, so it catches
calls luacheck does not.

It also states what it declines to do. selene omits lints for long lines and
whitespace, on the stated ground that _"it is unclear whether style issues like
these are fit for a linter or better under the scope of a Lua beautifier."_

That omission is why the two are not interchangeable. A project using luacheck
for line length and switching to selene loses the check with no output saying
so.

One claim on that page is stale, and where it came from is why this document
records it. selene describes luacheck as last updated in October 2018; the
maintained repository is `lunarmodules/luacheck`, its current release is v1.2.0
and its continuous integration runs. A tool's comparison page is a primary
source about itself and a secondary, interested and possibly stale source about
its rival.

`.luacheckrc` executing Lua is a second-order finding. A configuration file
that is a program is a configuration file a pack cannot safely read without
running it, and reading it by pattern is guessing at a program's output.

### The type verb writes its findings to a log file

`lua-language-server --check` is a language server in a batch mode, and its
interface is unlike every other verb in this survey.

It takes `--check=<workspace>`. `--checklevel` defaults to `Warning` and
suppresses `Information` and `Hint` below it. `--logpath` defaults to `./log`
and is _where the diagnosis report is written_, and `--configpath`, once given,
makes the server ignore configuration from other sources.

Three consequences follow directly:

- **The result is a file, and standard output carries none of it.** A pack that
  reads the terminal reads nothing useful, and a pack that reads the exit
  status alone has not read the findings. - **The default log path writes into
  the repository.** A verb that leaves `./log` behind has modified the working
  tree during a check, which a check must not do. The path is set explicitly,
  outside the tree. - **The default level hides two severities.** A clean check
  at the default level is not a clean check, and the pack states the level it
  ran at.

`llscheck` exists because of exactly this, wrapping the invocation into
something with a conventional exit status, and a project that configures it has
solved the problem already.

What the server checks depends entirely on `.luarc.json`: the runtime version,
the globals, the libraries on the path. Without that file it checks a language
with no standard library declared.

### The verbs

| Verb        | Command                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------------------------------- |
| `fmt`       | `stylua .`, with `--check` to verify                                                                          |
| `lint`      | `selene .`, else `luacheck .`                                                                                 |
| `typecheck` | `lua-language-server --check` with an explicit `--logpath` and `--checklevel`, or `llscheck` where configured |
| `test`      | `busted`, else `luaunit`                                                                                      |
| `build`     | usually none; `luarocks make` where a rockspec exists                                                         |

`build` is genuinely absent for most Lua projects, and saying so beats
resolving it to a command that runs and does nothing.

### What the pack authors

`.luarc.json` - the runtime version, the library globals, the workspace
libraries, and the diagnostic severities, which is the file that makes the type
verb mean anything.

`stylua.toml`, `selene.toml` and the selene standard-library definition, which
is where the project says what globals exist.

A `*.rockspec` where the project is a package, and a `.busted` configuration
where the test layout is not the default.

Not `.luacheckrc`, which is a Lua program. A pack that needs to change luacheck
configuration in a project that uses it says what to change, and rewrites no
program it has not read.

### What a reviewer needs that no command reports

Which Lua version and which standard library, because that decides whether the
rest of the review is about the right language.

Globals created by accident - a missing `local` is valid Lua, and a linter
catches it only where the standard library is declared.

`pcall` and what an error object actually is, given that anything may be
thrown.

Metatables and the cost of an `__index` chain, invisible until a hot path walks
it.

One-based indices, and `nil` holes in a sequence, where the length operator
stops being defined.

Whether annotations exist at all, since `lua-language-server` checks
annotations and a file with none passes vacuously.

### What the skill has to contain

In the body, in this order:

1. Detection. The six configuration markers and the rockspec, and that a
   project with none of them present is in a normal state that no error
   describes. 2. The version question, before the verbs. Which Lua, and what to
   do when nothing says. 3. Verb resolution, with the expectation that some
   verbs are unresolved on a given machine because nothing here ships with the
   interpreter. 4. The type verb's operational rules, which are unlike the
   rest: set `--logpath` outside the tree, set `--checklevel`, and read the
   report file, because the terminal carries nothing. 5. What must never
   happen. Substituting one linter for the other silently. Rewriting
   `.luacheckrc`. Leaving a `log` directory in the working tree. Reporting a
   default-level check as clean.

In supporting files: the tool inventory, and templates for `.luarc.json`,
`stylua.toml`, `selene.toml` and a selene standard library. Also the reviewer's
knowledge, and the dated facts with what to re-check: selene's stance on Lua
versions, luacheck's maintenance state and the language-server flags.

## Conclusions

1. A Lua project is marked by its tool configuration or a rockspec, and no
   manifest identifies it, and a project with none of those files has chosen no
   tools. 2. The pack reports unresolved verbs and assumes no stack, because
   nothing in the Lua toolchain ships with the interpreter and no stack is
   conventional. 3. The language version is read before anything else - 5.1
   through 5.4 and LuaJIT differ in ways that pass review and fail at run time
   - and a project that states none is reported. 4. The linter is detected, and
     the pack chooses none. selene and luacheck check different sets by design,
     so substituting one silently drops checks. 5. selene's omission of
     whitespace and line-length lints is recorded, so a project moving from
     luacheck knows what it stops checking. 6. A claim a tool makes about a rival
     is treated as an interested source. selene's description of luacheck as
     unmaintained since 2018 is contradicted by the maintained repository and its
     current release. 7. `.luacheckrc` is not authored by the pack, because it is
     a Lua program and no data file, and editing it by pattern guesses at a
     program's behaviour. 8. `typecheck` reads a report file, because the
     terminal carries nothing, since `lua-language-server --check` writes its
     diagnosis to the log path. 9. The log path is set explicitly and outside the
     working tree, because the default writes into the repository and a check
     does not modify the tree. 10. The check level is set and stated, since the
     default suppresses two severities and a clean run at the default is not a
     clean run. 11. `llscheck` is preferred where the project configures it,
     because it already wraps the invocation into a conventional exit status. 12.
     `typecheck` depends on `.luarc.json`, and a project without one has a check
     pointed at a language with no standard library declared. 13. A file with no
     annotations passes the type check vacuously, which is reported and counted
     as no coverage. 14. `build` is reported as absent for most Lua projects, and
     never resolved to a command that succeeds without doing anything. 15. The
     reviewer's knowledge is recorded with the pack: the language version,
     accidental globals, `pcall` and error objects, metatable cost, `nil` holes
     in sequences, and whether annotations exist. 16. The skill body carries
     detection, the version question, verb resolution, the type verb's
     operational rules, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [lua-language-server usage](https://luals.github.io/wiki/usage/) - `--check`
  producing a diagnosis report; `--checklevel` defaulting to `Warning` and
  excluding lower severities; `--logpath` defaulting to `./log` and naming
  where the report is written; and `--configpath` causing configuration from
  other sources to be ignored. - [lua-language-server
  configuration](https://luals.github.io/wiki/configuration/) - `.luarc.json`
  as the configuration file and the root markers the server recognises. -
  [selene, compared with
  luacheck](https://kampfkarren.github.io/selene/luacheck.html) - that selene
  is written in Rust and is multithreaded, configures in TOML where a
  `.luacheckrc` executes Lua, names its lints where luacheck numbers them, and
  configures argument types and counts in its standard library; that it
  deliberately omits long-line and whitespace lints on the stated ground that
  such style issues may belong to a beautifier; that it declines Lua versions
  beyond 5.1 for lack of demand; and its claim that luacheck was last updated
  in October 2018. -
  [lunarmodules/luacheck](https://github.com/lunarmodules/luacheck) - the
  maintained repository at v1.2.0, with support for Lua 5.1 to 5.4 and LuaJIT,
  detection of undefined globals, unused variables and values, uninitialised
  access and unreachable code, and the project's own statement that the module
  interface may change between minor releases. Read as the contradiction of the
  staleness claim above. - [busted](https://lunarmodules.github.io/busted/) -
  the test framework, its configuration file, and its support for coverage
  analysis. - [LuaCov](https://luarocks.org/modules/mpeterv/luacov) - coverage
  analysis producing a statistics file from a run, processed into a report of
  the paths not traversed. -
  [LDoc](https://luarocks.org/modules/lunarmodules/ldoc) - the documentation
  generator, including for C extension sources. - [Lua linters in
  MegaLinter](https://megalinter.io/8/descriptors/lua/) - that luacheck, selene
  and stylua are the three tools an aggregator runs for Lua, and that selene
  and stylua are expected on the path, which the project installs neither of.
