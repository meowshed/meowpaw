<role>
What a reviewer of Lua or of a Neovim plugin checks that no command reports.
Read it when you review Lua code, after `status` has named the host. A clean
lint says the linter found nothing in what it checks, and each point here
asks what it can't see.
</role>

<rules name="reviewing Lua">
- R1. Check the change against the runtime the host names, because a change
  right under Lua 5.4 can fail under LuaJIT, and the review is otherwise about
  the wrong language.
- R2. Look for a global created by a missing `local`, because it is valid Lua
  and a linter catches it only where the standard library is declared.
- R3. Check what each `pcall` returns and what the error object is, because
  anything may be thrown and a caller assuming a string mishandles a table.
- R4. Check the cost of an `__index` chain on a hot path, because metatable
  lookups are invisible until a loop walks them.
- R5. Look for `nil` holes in a sequence, because the length operator stops
  being defined and `ipairs` stops early.
- R6. Report a file with no annotations, because the language server checks
  annotations and a file without them passes vacuously.
</rules>

<rules name="reviewing a Neovim plugin">
- R7. Check what runs at startup against what could load lazily, because a
  file under `plugin/` runs on every start and its cost is every user's.
- R8. Check that `setup()` merges the user's options into the defaults and
  replaces none, because a replaced table drops every default the user
  didn't restate.
- R9. Check that each autocommand sits in a group cleared on reload, because
  a reload otherwise registers it twice.
- R10. Check a buffer or window handle's validity before use, and the fast
  event context before calling the API, with `vim.schedule` where needed,
  because a handle can close between the event and the call.
- R11. Prefer `vim.system` over `jobstart` and keep highlights and extmarks
  in the plugin's own namespace, because both keep the plugin from touching
  what another plugin owns.
- R12. Report a plugin that assumes it loads as a start plugin, because the
  built-in manager, `vim.pack`, loads plugins as opt.
- R13. Expect a health check, because `:checkhealth` is the only diagnosis a
  user has without the author.
</rules>
