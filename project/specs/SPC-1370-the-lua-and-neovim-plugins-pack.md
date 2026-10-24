---
id: SPC-1370
artifact: spec
status: live
revised: 2026-10-13
states: [REQ-2342, REQ-2344, REQ-2420, REQ-2422, REQ-2446, REQ-3048]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Lua and Neovim plugins pack

## Scope

This covers `meow-lua`, the language pack for Lua and for Neovim plugins
written in it, in one pack because Neovim is the host that evaluates the
plugin's Lua. It states what `status` detects, what `bind` prints and what
`check` finds. Every rule SPC-1190 states for a language pack holds here, and
this document states only what is Lua's. It leaves coverage, documentation
generation and the typed dialect Teal unbound.

ADR-2660 decides this pack and EPC-2560's TSK-5100 ships it.

## Boundary

| Surface                                    | What it is                                                         |
| ------------------------------------------ | ------------------------------------------------------------------ |
| `plugins/meow-lua/bin/meow-lua`            | The program: `status`, `bind` and `check`                          |
| `plugins/meow-lua/skills/lua/SKILL.md`     | The skill                                                          |
| `plugins/meow-lua/skills/lua/reviewing.md` | What a reviewer of Lua or of a Neovim plugin needs beyond commands |
| `plugins/meow-lua/README.md`               | The unit's page, with the toolchain versions it's current as of    |
| `.meowpaw/profile.toml`, `[lua] runtime`   | The Lua runtime, where `.luarc.json` doesn't name it               |

The program is the `lua` feature of `crates/meow`. It runs git alone and
starts no Lua tool (SPC-1190).

## Behaviour

### Detection

A directory activates the pack where git tracks a `*.rockspec` or a
`.luarc.json` in it (REQ-2342), or tracks files under both its `lua/` and its
`plugin/` subdirectories, which lays out a Neovim plugin (REQ-2344, RES-0106,
RES-0107). Each report names the directory and its markers, the layout as
`lua/, plugin/` (REQ-3048).

### The host

The pack decides which host evaluates the directory's Lua before it binds a
stage (REQ-2446):

1. A Neovim plugin's layout makes the host Neovim.
2. Otherwise `runtime.version` in the directory's `.luarc.json`, in the dotted
   or the nested form, names the runtime: `Lua 5.1` to `Lua 5.4` or `LuaJIT`
   (RES-0360).
3. Otherwise `[lua] runtime` in the profile names it.

A directory none of these names prints `unresolved: Lua runtime not detected`
in `status`, and `bind` prints every stage as unresolved with that reason,
because LuaLS applies `Lua 5.4` to a file that names none, in silence.

### What `bind` prints

| Stage    | Printed as                           | When                                                                   |
| -------- | ------------------------------------ | ---------------------------------------------------------------------- |
| `format` | `stylua --check .`                   | A `stylua.toml` or `.stylua.toml` in the directory or above it         |
| `lint`   | `selene .`                           | A `selene.toml` in the directory                                       |
| `lint`   | `luacheck .`                         | A `.luacheckrc` in the directory or above it                           |
| `lint`   | `selene . && luacheck .`             | Both, with a comment saying they check different sets                  |
| `check`  | `# check: unbound, ...`              | Always: `lua-language-server --check` writes its findings to a log     |
| `test`   | `busted`                             | A `.busted` in a directory whose host is a Lua runtime                 |
| `test`   | `# test: unbound, ...`               | A Neovim plugin: its tests run inside `nvim --headless`                |
| `build`  | `luarocks make <rockspec>`           | One rockspec in the directory                                          |
| `build`  | `# build: unresolved, ...`           | No rockspec, because Lua and a Neovim plugin have no build without one |
| any      | `# <stage>: unbound, looked for ...` | No row above applies                                                   |

The pack binds the linter the repository configured, and never picks one
where only the other is configured, because selene and luacheck check
different sets and substituting one drops checks in silence (REQ-2420). It
turns on no lint group or check level the repository didn't set (REQ-2422).
`check` stays unbound because a stage reading the language server's exit
status hasn't read its report, and a comment names `llscheck` as the wrapper a
repository can declare (RES-0106). Two rockspecs in one directory bind no
`build`, and the comment names both.

### What `check` finds

| Finding                      | When                                                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `<dir>: no .luarc.json, ...` | A Neovim plugin commits no `.luarc.json`, so the language server checks a Lua with no editor runtime declared |
| `<dir>: no doc/, ...`        | A Neovim plugin tracks nothing under `doc/`, so `:help` has nothing for its users                             |

`check` exits 1 on any finding, and prints `no findings` and exits 0 when
there is none (RES-0107).

## Failure paths

| State                                               | Reported as                                           | Exit |
| --------------------------------------------------- | ----------------------------------------------------- | ---- |
| No marker is tracked                                | `unresolved: not a Lua and Neovim plugins repository` | 3    |
| No host is detected for a directory                 | `unresolved: Lua runtime not detected`                | 3    |
| `check` finds no profile, or one that doesn't parse | `unresolved: <what is wrong with the file>`           | 3    |
| An unknown argument                                 | the usage line                                        | 2    |

## Questions

Answer each question from what this document states, or leave `unanswered`,
because a gap left visible is one a reader can act on, and a gap left out
reads as covered.

### What the part is for

Detects Lua and Neovim plugins written in it, binds its stages and checks its configuration.

### What it depends on

`meow-lua` lists `meow-core` in its `requires.toml`.

### What depends on it

No unit lists `meow-lua` in its `requires.toml`.

### Where its data lives

It holds none of its own: it reads the files git tracks and the profile, and SPC-1190 states that a pack's program writes no file.

### What crosses a trust boundary

unanswered

### How it fails

Stated under "Failure paths" in this document.

### How it is deployed

`meow-lua` installs as a plugin from the marketplace, `plugins/meow-lua/`, and ships as the Pi package `packages/meow-lua/`.
