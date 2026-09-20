---
id: RES-0107
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0106, RES-0005
---

# Neovim plugins

## Summary

A plugin is a Lua project plus a platform, and the platform supplies
everything that makes this a separate document. Two verbs need the embedded
interpreter, because the editor module exists nowhere else and a suite that
mocks it tests the mock. The two test harnesses differ in process model rather
than in syntax, and only one can take a screenshot. Neither emits a
machine-readable report, so evidence here is captured output and an exit
status.

Research for one supported target. A Neovim plugin is a Lua project plus a
platform. The formatting and linting verbs come from Lua unchanged, and the
platform supplies everything that makes this document necessary: the
interpreter lives inside the editor, the documentation is a generated format,
and a manager that shipped with the editor in March 2026 distributes the
plugin.

It does not cover the Lua toolchain, which is
[RES-0106-lua.md](RES-0106-lua.md), nor what every toolchain document shares,
which is [RES-0006-toolchains.md](RES-0006-toolchains.md).

## The question

Two verbs behave differently here than in plain Lua, because the `vim` module
exists nowhere but inside the editor. A test that runs under a standalone Lua
interpreter is testing a program the plugin is not.

The platform also moved in March 2026, which makes a plugin's installation
section, its language-server setup and its claimed minimum version all
potentially out of date at once.

## Method

We fetched and read the primary sources on 2026-09-20. The built-in plugin
manager's guide, written by its author and carrying its stated limits. One test
harness's repository and its comparison with the other. And the language-server
configuration plugin that supplies the editor's runtime library paths.

The absence of a machine-readable report from either harness was checked by
reading both, and we record it as an absence, which this survey omitted
nowhere.

One search was used to find the documentation generators. Nothing was
installed or run.

## Findings

### The markers are a layout, and the layout is a contract

`lua/` beside `plugin/` or `doc/` marks a plugin; a `.luarc.json` naming the
Neovim runtime confirms it; a `Makefile` or `Justfile` invoking `nvim
--headless` usually means tests exist. A `*.rockspec` marks a plugin
distributed through luarocks, which a minority are.

The layout is not a convention the author chose:

- `plugin/` runs at startup for every user, whether or not they use the plugin.
- `lua/<plugin>/init.lua` is what `require` resolves.
- `doc/` with a tagged help file and a generated `tags` file is what `:help`
  finds.
- `lua/<plugin>/health.lua` is what `:checkhealth` runs.
- `ftplugin/`, `after/` and `queries/` each have load semantics of their own.

A file in the wrong directory changes when its code runs, which is a defect no
linter reports.

### The toolchain, tool by tool

| Role          | Tool                           | What only it answers                                                  |
| ------------- | ------------------------------ | --------------------------------------------------------------------- |
| Format        | `stylua`                       | The canonical form - the Lua verb unchanged                           |
| Lint          | `selene`, `luacheck`           | The Lua verb unchanged, configured with `vim` as a global             |
| Typecheck     | `lua-language-server --check`  | Diagnostics against the Neovim runtime declared in `.luarc.json`      |
| Typecheck     | `llscheck`                     | The same with a conventional exit status                              |
| Runtime types | `lazydev.nvim`, the LLS addons | Which library paths the server should load                            |
| Test          | `plenary.nvim`                 | A busted-style harness, one headless Neovim per file                  |
| Test          | `mini.test`                    | Hierarchical tests, screen tests, an explicitly managed child process |
| Test          | `vusted`, `busted` with `nlua` | busted proper, with a Neovim interpreter                              |
| Docs          | `panvimdoc`                    | A vimdoc help file generated from Markdown                            |
| Docs          | `ts-vimdoc.nvim`               | The same with no dependency beyond a treesitter parser                |
| Distribution  | `vim.pack`                     | Installation, updating and removal, built into the editor             |
| Health        | `vim.health`                   | What a user sees when the plugin is misconfigured                     |

### The two test harnesses differ in process model, and the difference is the choice

`plenary.nvim` executes each test file in a separate headless Neovim process
with a customisable init file, in a busted-style syntax familiar to anyone who
has written Lua tests.

`mini.test` runs in the current process and encourages the test to manage a
_child_ Neovim explicitly. That inversion is what buys it screen tests: a
helper creates the child process and takes and verifies screenshots of it,
which is the only way to test what the user actually sees. It also provides
hierarchical sets, hooks, parametrisation, filtering from the cursor position,
busted-style emulation and customisable reporters, with two supplied - a buffer
reporter for interactive use and a stdout reporter for headless runs.

The trade is legible. Plenary's isolation is per file and automatic; mini.test's
isolation is explicit and therefore controllable, which is what a screen test
requires.

Neither documents a machine-readable report format. That is the finding for a
harness. A Neovim plugin's test run produces human-readable output, so the
evidence is the captured output plus the exit status, and no JUnit file, unless
the project wired up something itself.

### The type verb needs the editor's own library paths

`lua-language-server --check` is the type verb, and what it checks depends
entirely on `.luarc.json`: the runtime version, the globals - `vim` above all -
and the library paths.

`lazydev.nvim` is how a modern configuration supplies those, _"lazily updating
your workspace libraries"_ as it sees `require` calls and module annotations,
replacing the older `neodev.nvim`. Its note is the one a pack should carry:
Neovim types are no longer needed as a separate library on Neovim 0.10 and
later, because the editor ships them.

So a plugin pinning an external types library is describing an older editor,
and that is reportable.

The operational rules from the Lua document apply unchanged, and they bite
harder here. The report goes to `--logpath` and never to the terminal, the
default path writes into the repository, and the default `--checklevel` of
`Warning` hides two severities.

### Documentation is a generated artifact, and the generated file is committed

`doc/` holds vimdoc, which is a format with its own tag syntax, and `tags` is
generated from it by `:helptags`. Most plugins now write Markdown and generate
the vimdoc. `panvimdoc` does it through Pandoc, usually wired as a continuous
integration action so a push regenerates the committed help file.
`ts-vimdoc.nvim` does it with a treesitter parser and no other dependency.

Two consequences for a pack. **The generated file is in the repository**, so a
check that does not know it is generated reports drift as a defect. The actual
defect is the Markdown changing while the vimdoc does not, and the check has to
notice that. And **a plugin with no `doc/` is not documented for its users**,
regardless of how good its readme is, because `:help` is where a Neovim user
looks.

### The platform gained a plugin manager, and that changes what an installation section should say

Neovim 0.12.0 was released on 29 March 2026 with `vim.pack`, a plugin manager
built into the editor. Its surface is three functions: `vim.pack.add()` to
install if missing and load, `vim.pack.update()` and `vim.pack.del()`. Two
autocommand events come with them, `PackChangedPre` and `PackChanged`, carrying
the plugin name, its specification and a `kind` of `install`, `update` or
`delete`.

Its documented limits decide what a plugin author may rely on:

- Only Git repositories are managed; anything else is manual. - An installation
  hook must exist _before_ the `vim.pack.add()` call that triggers the
  installation. - Lazy loading is supported but is not a design goal. - Every
  plugin loads into the `core` package as an _opt_ plugin, and never as a
  _start_ plugin.

That last one is load-bearing for a plugin author: a plugin that assumes it
will be on the runtime path at startup is assuming a shape `vim.pack` does not
produce by default.

For a pack the consequence is narrow and useful: a readme offering only an
external manager's snippet documents one of several shapes, and the built-in
one is what a user with a stock editor has.

### The language-server surface changed, and the old pattern still works

`vim.lsp.config()` and `vim.lsp.enable()` are the current way to configure and
activate a language server. The older `require('lspconfig').<server>.setup({})`
still works and is the legacy approach.

"Still works" is what makes this a review question that no check settles.
Nothing fails; a configuration written against the old surface keeps working
against the old surface, and only a reader notices.

### The claimed minimum version became a live question again

0.12 carried breaking changes that configurations had to absorb, alongside
native insert-mode completion, a reworked default interface and statusline, and
a much larger built-in language-server surface - inline completion, document
colours, code lens refresh, workspace diagnostics, dynamic registration.

So the minimum Neovim version a plugin claims is something to check, because
nothing keeps it stable, and the honest form of the claim is a version the
plugin is actually tested against. That makes a version matrix in continuous
integration part of the plugin's evidence, and no nicety.

### What the pack authors

`.luarc.json` with the Neovim runtime and `vim` as a global, and the selene or
luacheck standard-library definition for the same reason. A test bootstrap: the
minimal init file that puts the plugin and its test dependency on the runtime
path. A `doc/` generation step, and a `health.lua` skeleton.

The minimal init file is where a pack helps most, and it is the one most often
wrong by hand. It has to add paths in an order that depends on none of the
user's own configuration.

### What a reviewer needs that no command reports

Lazy loading: nothing expensive at require time, because `plugin/` runs at
startup and a slow plugin is a slow editor for everyone who installed it.

`setup()` merging user options into defaults and replacing none of them, which
is the difference between a configurable plugin and one that demands every
field.

Autocommand groups cleared on reload, or handlers accumulate.

Buffer and window handle validity, because the user may have closed either
between the scheduling of a callback and its execution.

`vim.schedule`, and what may not run in a fast event context.

`vim.system` for running a process, where `jobstart` is the older call.

A health check that says something useful, since `:checkhealth` is the only
diagnosis a user has without the author.

Whether the plugin pollutes the global namespace or the default keymaps, which
is a question about politeness that no tool asks.

### What the skill has to contain

In the body, in this order:

1. Detection and the layout contract. What each directory means and when
   its code runs.
2. The embedded-interpreter rule. Tests run inside `nvim --headless`; a
   suite that mocks `vim` tests the mock.
3. Verb resolution, noting which verbs are the Lua ones unchanged and which
   are not.
4. The type verb's operational rules, inherited from Lua: explicit log
   path outside the tree, explicit check level, read the report file.
5. Evidence. Neither harness emits a machine-readable report, so evidence
   is captured output plus exit status, and the version matrix is part of it.
6. What must never happen. Mocking `vim`. Assuming a start plugin.
   Reporting generated vimdoc drift as an authored defect. Leaving `log` in the
   tree.

In supporting files: the harness comparison and when a screen test earns its
cost, a minimal init template per harness, and a `.luarc.json` template. Also
the `doc/` generation wiring, the `vim.pack` limits, the reviewer's knowledge,
and the dated facts with what to re-check: the 0.12 release, the
language-server surface, and the types library nobody needs now.

## Conclusions

1. A Neovim plugin is detected by its layout: `lua/` beside `plugin/` or
   `doc/`, with a `.luarc.json` naming the runtime as confirmation. 2. The
   layout is checked and never assumed, because which directory a file sits in
   decides when its code runs. 3. `test` runs inside `nvim --headless`, because
   the `vim` module and the editor's event loop exist only in the embedded
   interpreter and a suite that mocks them tests the mock. 4. The harness is
   detected, and the pack chooses none, since plenary isolates per file
   automatically and mini.test manages a child process explicitly, and only the
   second can take a screenshot. 5. A screen test is the only evidence about
   what the user sees, and a plugin whose value is an interface has no other
   way to check it. 6. Test evidence is captured output plus exit status,
   because neither harness documents a machine-readable report, and the pack
   states that limitation, papering over nothing. 7. A version matrix is part
   of the plugin's evidence, since 0.12 carried breaking changes and a claimed
   minimum nothing runs against is a guess. 8. `typecheck` needs the Neovim
   runtime declared in `.luarc.json`, or the server is checking a Lua with no
   editor in it. 9. An external Neovim types library is reported as unnecessary
   on 0.10 and later, because the editor ships them and pinning one describes
   an older editor. 10. The type verb's log path is explicit and outside the
   tree, and its check level is stated, inherited unchanged from the Lua pack. 11. `fmt` and `lint` are the Lua verbs unchanged, so the plugin pack extends
   the language pack and replaces none of it. 12. Generated vimdoc is
   recognised as generated, and the reported defect is Markdown that changed
   while the help file did not. 13. A plugin with no `doc/` is reported as
   undocumented for its users, whatever its readme contains, because `:help` is
   where a Neovim user looks. 14. Installation documentation covers the
   built-in manager, since `vim.pack` ships with the editor as of 0.12.0 on 29
   March 2026. 15. The documented limits of `vim.pack` are part of the pack's
   knowledge: Git repositories only, hooks created before the `add` call, lazy
   loading supported without being a design goal, and plugins loaded as opt and
   never as start. 16. A plugin that assumes it is a start plugin is reported,
   because the built-in manager loads it as opt. 17. A configuration written
   against `lspconfig`'s `setup` is reported as legacy, and never as broken,
   because it still works and only a reader notices. 18. A health check is
   expected, since `:checkhealth` is the only diagnosis a user has without the
   author. 19. The reviewer's knowledge is recorded with the pack: startup cost
   and lazy loading, `setup()` merging options and replacing none, autocommand
   groups cleared on reload, handle validity, `vim.schedule` and the fast event
   context, `vim.system` over `jobstart`, and namespace politeness. 20. The
   skill body carries the layout contract, the embedded-interpreter rule, verb
   resolution, the type verb's operational rules, the evidence limitation, and
   the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [A guide to
  vim.pack](https://echasnovski.com/blog/2026-03-13-a-guide-to-vim-pack) - the
  three functions `add`, `update` and `del`; the `PackChangedPre` and
  `PackChanged` events with their name, specification, active flag and `kind`
  of install, update or delete; and the stated limits that only Git
  repositories are managed, that an installation hook must exist before the
  `add` call that triggers it, that lazy loading is supported without being a
  design goal, and that plugins load into the `core` package as opt and never
  as start. - [mini.test](https://github.com/nvim-mini/mini.test) -
  hierarchical tests, hooks, parametrisation, filtering from the current file
  or cursor position, screen tests, busted-style emulation and customisable
  reporters; the child Neovim helper designed for taking and verifying
  screenshots; and the two supplied reporters, `buffer()` for interactive use
  and `stdout()` for headless runs. - [mini.test against
  plenary](https://nvim-mini.org/mini.nvim/TESTING.html) - that plenary
  executes each file in a separate headless Neovim process with a customisable
  init file while mini.test executes in the current process and encourages a
  manually managed child process. -
  [lazydev.nvim](https://github.com/folke/lazydev.nvim) - configuring
  lua-language-server by lazily updating workspace libraries as `require` calls
  and module annotations appear; replacing `neodev.nvim`; the library option
  with word, module and file triggers; and its statement that Neovim types are
  no longer needed on Neovim 0.10 and later. - [lua-language-server
  usage](https://luals.github.io/wiki/usage/) - `--check` writing its diagnosis
  report to `--logpath`, the `Warning` default for `--checklevel`, and
  `--configpath` overriding other configuration sources. -
  [panvimdoc](https://github.com/kdheepak/panvimdoc) - generating a vimdoc help
  file from Pandoc Markdown, and its use as a continuous integration action so
  the committed help file is regenerated automatically. -
  [ts-vimdoc.nvim](https://github.com/ibhagwan/ts-vimdoc.nvim) - the same
  conversion through a treesitter parser with no dependency beyond it. -
  [Neovim 0.12 has been
  released](https://alternativeto.net/news/2026/3/neovim-0-12-has-been-released-with-a-built-in-plugin-manager-major-lsp-and-ui-upgrades)
  and [What's new in Neovim
  0.12](https://dotfiles.substack.com/p/whats-new-in-neovim-012) - the release
  on 29 March 2026; the built-in plugin manager; the expanded built-in
  language-server support including inline completion, document colours, code
  lens refresh, workspace diagnostics and dynamic registration; native
  insert-mode completion; the reworked default interface and statusline; and
  the breaking changes configurations had to absorb. -
  [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig) - that
  `vim.lsp.config()` and `vim.lsp.enable()` are the current surface and that
  the older `require('lspconfig').<server>.setup({})` pattern still works as
  the legacy approach.
