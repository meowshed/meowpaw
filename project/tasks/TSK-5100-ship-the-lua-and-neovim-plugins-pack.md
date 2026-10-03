---
id: TSK-5100
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2560
closes: [REQ-2342, REQ-2344]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Ship the Lua and Neovim plugins pack

The language pack for Lua and Neovim plugins, named in its own document, is detected from a rockspec or `.luarc.json`, and a `lua/` tree beside a `plugin/` directory for a Neovim plugin, and resolves
the five verbs from what the repository commits, as SPC-1190 states under
"The supported packs". One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given a fixture repository of the language with its marker in a
   subdirectory, when the pack's `status` runs, then it reports for that
   directory and names the marker, and with no marker it prints
   `unresolved: not a Lua and Neovim plugins repository` and exits 3 (REQ-2342, REQ-2344). Closed by: a
   crate test naming REQ-2342, seen failing first.
2. Given a fixture repository of the language, when the pack's `bind` runs,
   then it prints all five verbs, each bound from what the fixture commits or
   printed as unresolved or unbound with a reason (REQ-2342, REQ-2344). Closed by: a crate
   test naming REQ-2342.
3. Given the fixture, when the pack's tests run, then they hold the shared
   rules that apply to Lua and Neovim plugins: the host or implementation detected before it binds, Neovim or a Lua runtime (REQ-2446), and the tool the repository configured where several serve a verb (REQ-2420). Closed by: the crate tests naming
   each requirement.
4. Given `docs/README.md`, when the pack ships, then its row reads `shipped`.
   Closed by: `tools/check_docs.py`.

## What to do

Before implementing, check that the pack's own specification exists beside
SPC-1190, written through the spec step, with `paw ready implement` on this
task; where it doesn't, stop and report it, because this task decides
nothing the pack's document states: its bindings, its findings and its
settings table. Build the pack as a feature of `crates/meow/` on EPC-2565's
shared layer, with a program carrying `status`, `bind` and `check`, a skill
and a page, as SPC-1190's Boundary states. The pack binds each verb from the
tool the repository configured, and never from what is installed. Add a
fixture repository of the language to the crate's tests. The pack's README
states the toolchain versions it is current as of.

## Depends on

- TSK-5095 (blocking): the packs ship one at a time in the order SPC-1190
  states, so a mistake in one is fixed before the next repeats it.

## Evidence

Not yet.

## Left alone

The other languages in the order, each its own task, and any binding the
pack's own document doesn't state.
