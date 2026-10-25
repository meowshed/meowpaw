---
reader: someone choosing or running meow-lua
answers: what meow-lua does, what it adds to a session and how to run it
kind: reference
describes: [meow-lua@0.1.1]
description: "Detects Lua and Neovim plugins from what git tracks, names the runtime or the editor that evaluates the code before it binds anything, prints a stages table bound from the formatter, linter, test runner and rockspec the repository configured, reports a plugin with no runtime declared or no help file, writing no file, and carries what a reviewer of Lua or of a Neovim plugin checks that no command reports."
---

# meow-lua

`meow-lua` tells you where your repository holds Lua or a Neovim plugin and
which host evaluates that Lua, prints a `[stages]` table bound from the tools
you configured, and checks that a plugin declares its runtime and documents
itself. Its skill tells Claude Code what a reviewer of Lua or of a Neovim
plugin checks that no command reports. It writes no file and starts no Lua
tool: `status`, `bind` and `check` read the files git tracks and run git
alone. It installs on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-lua@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

<!-- host-specific: claude -->

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-lua status
```

From your own shell, run the same launcher by its path in the installed unit.

The program reports for each directory where git tracks a `*.rockspec` or a
`.luarc.json`, or tracks files under both `lua/` and `plugin/`, which is how a
Neovim plugin is laid out. Each directory's report opens with
`scope: <directory>` and one `marker:` line for each marker, the layout as
`lua/, plugin/`, and then `status` prints the host, the formatter and the
linter.

The host comes first, because Lua 5.1 to 5.4 and LuaJIT differ in ways that
pass review and fail at run time. A Neovim plugin's host is Neovim. Otherwise
the program reads `runtime.version` from the directory's `.luarc.json`, and
then `[lua] runtime` in your profile:

```toml
[lua]
runtime = "LuaJIT"
```

Where neither names a runtime, `status` prints `unresolved: Lua runtime not
detected` and exits 3, and `bind` prints every stage unresolved with that
reason, because the language server applies Lua 5.4 to a file that names
none, without saying so.

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

| Line                         | When                                                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| `<dir>: no .luarc.json, ...` | The plugin commits no `.luarc.json`, so the language server checks a Lua with no editor runtime declared |
| `<dir>: no doc/, ...`        | The plugin tracks nothing under `doc/`, so `:help` has nothing for its users                             |

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

When Claude Code reviews Lua, the skill has it run `status` first and then
load `reviewing.md`, which holds what no command reports: the runtime the
change runs on, a global made by a missing `local`, `pcall` and the error
object, the cost of an `__index` chain, `nil` holes in a sequence, and a file
with no annotations. For a plugin it adds startup cost, `setup()` merging
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

## What it needs

<!-- host-specific: claude -->

Claude Code 2.1.280 or later, declared in `plugins/meow-lua/requires.toml`,
and git. The pack is current as of luacheck 1.2.0 and Neovim 0.12, as the
research read them in September 2026, and of LuaLS's settings as read on
2026-10-13. None was observed running, so check a binding against a newer
tool's documentation before you trust it.
