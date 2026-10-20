---
name: lua
description: The stages a Lua repository or Neovim plugin binds, which host evaluates its Lua, and what a reviewer of Lua or of a Neovim plugin checks. It MUST be loaded before binding a stage in, reporting the toolchain of, or reviewing code in a repository holding a rockspec, a .luarc.json or a lua/ directory beside a plugin/ directory. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a Lua repository configured through the pack's program, and you
report what it printed. The program binds each stage from the files the
repository commits and runs no Lua tool, so its table is a proposal the person
accepts, never a result. Nothing in the Lua toolchain ships with the
interpreter and five runtimes differ in ways that pass review, so the host
comes first and an unbound stage is the normal state, not a fault.
</role>

<steps name="read the configuration">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-lua status` and show its output.
2. If it exits 3, report each line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each directory, the host, the formatter and the
   linter, and stop.
</steps>

<steps name="bind the stages">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-lua bind` and show the table it
   prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="review Lua">
1. Run `${CLAUDE_SKILL_DIR}/../../bin/meow-lua status` for the host.
2. Read `${CLAUDE_SKILL_DIR}/reviewing.md` before you review Lua or a Neovim
   plugin, and hold the change to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the stages">
- L1. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- L2. Write the profile, `.luarc.json`, `stylua.toml` or `selene.toml` only
  when the person asks, and never rewrite `.luacheckrc`, because it is a Lua
  program and editing it by pattern guesses at what the program does.
- L3. Where the program prints `Lua runtime not detected`, ask which runtime
  the code runs on before anything else, because Lua 5.1 to 5.4 and LuaJIT
  differ in integer division, `goto`, the bitwise operators and `_ENV`, and
  code right under one fails under another.
- L4. Run a Neovim plugin's tests inside `nvim --headless` with the harness the
  repository uses, because the `vim` module exists only in the editor's
  interpreter and a suite that mocks it tests the mock.
- L5. Run `lua-language-server --check` only with `--logpath` outside the
  working tree and `--checklevel` stated, and read the report file, because
  the default log path writes into the repository, the default level hides
  two severities, and the terminal carries no finding.
- L6. Name the versions the pack is current as of, luacheck 1.2.0 and
  Neovim 0.12 as the research read them in 2026-09 and LuaLS's settings as
  read on 2026-10-13, none observed running, and where an installed tool is
  newer, say a binding may be stale.
</rules>

<rules name="what must never happen">
- L7. Never substitute selene for luacheck or luacheck for selene, because
  they check different sets: selene omits whitespace and line length, so a
  repository moving to it stops checking those in silence.
- L8. Never report a type check of a file with no annotations as clean,
  because lua-language-server passes it vacuously.
- L9. Never leave a `log` directory in the working tree after a type check,
  because a check that modifies what it checks can't be trusted about it.
</rules>
