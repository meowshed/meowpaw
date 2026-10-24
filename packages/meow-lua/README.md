---
reader: someone installing or running meow-lua on Pi
answers: what meow-lua provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-lua@0.1.0]
---

# @meowshed/meow-lua

Detects Lua and Neovim plugins from what git tracks, names the runtime or the editor that evaluates the code before it binds anything, prints a stages table bound from the formatter, linter, test runner and rockspec the repository configured, reports a plugin with no runtime declared or no help file, writing no file, and carries what a reviewer of Lua or of a Neovim plugin checks that no command reports. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-lua
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

## Bind your stages

`meow-lua bind` prints a `[stages]` table for you to paste into
`.meowpaw/profile.toml`, and never writes the profile itself:

```toml
[stages]
format = "stylua --check ."
lint = "selene ."
# check: unbound, lua-language-server --check writes its findings to a log file, so a stage reading its exit status hasn't read them; declare a command that reads the report, such as llscheck
test = "busted"
build = "luarocks make shop-1.0-1.rockspec"
```

| Stage    | Bound to                    | When                                                        |
| -------- | --------------------------- | ----------------------------------------------------------- |
| `format` | `stylua --check .`          | A `stylua.toml` or `.stylua.toml` in the directory or above |
| `lint`   | `selene .`                  | A `selene.toml` in the directory                            |
| `lint`   | `luacheck .`                | A `.luacheckrc` in the directory or above                   |
| `lint`   | `selene . && luacheck .`    | Both, because they check different sets                     |
| `check`  | nothing, printed as unbound | Always                                                      |
| `test`   | `busted`                    | A `.busted` in a directory whose host is a Lua runtime      |
| `build`  | `luarocks make <rockspec>`  | One rockspec in the directory                               |

A stage with no binding is a comment giving the reason. The pack binds the
linter you configured and never the other one, because selene leaves out
whitespace and line length, so swapping one for the other drops checks
without a word. A Neovim plugin's `test` stays unbound, because its tests run
inside `nvim --headless` and the harness, plenary or mini.test, is yours to
declare. `build` is unresolved without a rockspec, because Lua and a Neovim
plugin have no build without one. Where several directories activate, each
command runs in its own directory, and a stage one directory leaves unbound
is a comment naming that directory. `bind` prints nothing for a stage your
profile already declares.

## Check a Neovim plugin

`meow-lua check` prints a finding for each of these in a Neovim plugin, and
exits 1 on any:

| Line                         | When                                                                                                      |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| `<dir>: no .luarc.json, ...` | The package commits no `.luarc.json`, so the language server checks a Lua with no editor runtime declared |
| `<dir>: no doc/, ...`        | The package tracks nothing under `doc/`, so `:help` has nothing for its users                             |

With no finding it prints `no findings` and exits 0.

## What it reports instead of a table

| Line                                                  | Means                                         |
| ----------------------------------------------------- | --------------------------------------------- |
| `unresolved: not a Lua and Neovim plugins repository` | Git tracks no marker                          |
| `unresolved: Lua runtime not detected: ...`           | Nothing names the runtime for a directory     |
| `unresolved: no profile at .meowpaw/profile.toml`     | `check` found no profile                      |
| `unresolved: the profile doesn't parse: ...`          | `check` found a profile that isn't valid TOML |

Each exits 3.

## Generated files

Commit `.luarc.json`, `stylua.toml`, `selene.toml`, `.luacheckrc`, `.busted`
and the rockspec, because they're the configuration every binding reads.
Commit a Neovim plugin's generated help file under `doc/` as well, because
`:help` reads it from the repository, and a generator such as panvimdoc
rewrites it on each push. Ignore `log/`, which `lua-language-server --check`
writes into the directory it runs from unless `--logpath` names another.

## Review Lua or a Neovim plugin

When Pi reviews Lua, the skill has it run `status` first and then
load `reviewing.md`, which holds what no command reports: the runtime the
change runs on, a global made by a missing `local`, `pcall` and the error
object, the cost of an `__index` chain, `nil` holes in a sequence, and a file
with no annotations. For a package it adds startup cost, `setup()` merging
options, autocommand groups, handle validity and the fast event context,
`vim.system`, namespaces, opt loading under `vim.pack`, and a health check.
The skill never swaps one linter for the other, never rewrites `.luacheckrc`,
and never leaves a language server's `log` directory in your working tree.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when Lua is reviewed. The program is a native binary
shipped inside `meow-core`, and needs git on the machine. On a machine the
unit carries no binary for, it reports the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-lua --help` lists the subcommands, and `meow-lua <subcommand> --help`
names what it determines, what you read to reach the same answer without the
tool, and the first word of each kind of line it prints.
