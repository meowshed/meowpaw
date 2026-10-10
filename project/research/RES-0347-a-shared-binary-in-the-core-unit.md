---
id: RES-0347
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The platform can install the core unit with each unit and shows a path to it, and a shared binary saves about 34 MB

## Summary

Claude Code's plugin manifest has a `dependencies` field that installs the
named plugin with the dependent one, and it keeps a plugin's `bin/` on the Bash
tool's `PATH` while the plugin is enabled. It names no variable for a
dependency's directory, and it names no `PATH` for hooks. The data directory of
a plugin sits at a documented path, `~/.claude/plugins/data/<id>/`, which a
second plugin can read. A single build of the tool in the core unit would
replace 13 per-unit builds whose archives sum to 41 MB with one of about 7 MB.
It would also reverse two approved requirements, that a unit doesn't require
another and that each installs independently.

The document covers whether the platform allows one binary for the units and
what it saves. It doesn't cover the build, which a task measures.

## The question

Can the units' programs run from one build of the tool shipped in `meow-core`,
with each unit depending on `meow-core`, and what does it cost?

The assumption behind the question is that the per-unit binaries are the cost
worth removing. They are 13 copies of one program, and each archive carries
seven platform binaries, but the install is a one-time download, and the cost
of the change falls on the units' independence, which the records chose
(ADR-1270). Doing nothing is therefore an option.

## Method

I read the plugin manifest reference, the plugin dependencies page and the
components page of the Claude Code documentation on 2026-10-10. I read the
release assets of the 16 units' current versions and of `meow-full-v0.1.0` with
`gh release view`. I read a unit's launcher, `plugins/meow-scm/bin/meow-scm`,
the manifest of the core unit, and the pack code that looks beside itself for
`meow-scm` (`crates/meow/src/git.rs`). I did not install a unit with a
dependency to see the behaviour, and I did not test whether a hook has the
plugin `bin/` on its `PATH`, which the documentation doesn't say.

## Findings

### The manifest has a dependencies field

`dependencies` is an "array of strings or objects: plugins that must be enabled
for this one to work". An entry is a name, `name@marketplace`, or an object with
a `version` range. Installing a plugin installs its missing dependencies, and
`/reload-plugins`, auto-update and re-running install do the same. For a
dependency whose source is an archive, as this marketplace's are, the range
isn't what picks the version: it is checked when the plugin loads, against the
`version` in the dependency's `plugin.json`, and the dependent plugin is
disabled if it doesn't satisfy it.

### A dependency's `bin/` is on the Bash tool's PATH, and nothing says hooks

"Files in `bin/` at the plugin root are on the `PATH` of the Bash tool's shell
while the plugin is enabled, so Claude can run them as bare commands", and
"plugin `bin/` directories come after the user's own `PATH` entries". The
variable for the plugin's root resolves to the plugin's own installed version,
and the page names no variable for another plugin's directory. The units' hooks
run a script under their own root today, and hook commands aren't run by the
Bash tool, so a hook can't be assumed to find `meow` by name.

### A plugin's data directory is at a documented path

`${CLAUDE_PLUGIN_DATA}` resolves to `~/.claude/plugins/data/<id>/`, where `<id>`
is the plugin identifier with every character other than a letter, digit, `_`
or `-` replaced by `-`. It survives updates. A hook of `meow-core` that writes
its own root there at session start gives every other plugin a path to the
binary that is built from documented parts only.

### The archives of the 13 program units sum to 41 MB

The latest archives on 2026-10-10: `meow-flow` 4.6 MB, `meow-loop` 4.5,
`meow-gotask` 4.1, `meow-author` 4.0, `meow-mise` 3.9, `meow-scm` 3.7,
`meow-licence` 3.7, `meow-prose-gate` 3.5, `meow-github` 2.0, `meow-markdown`
2.0, `meow-checks` 1.9, `meow-unattended` 1.8 and `meow-git` 1.7. The one
archive that holds the binary built with every unit's feature, `meow-full`
0.1.0, is 7.1 MB, and the Pi packages already take it (REQ-4136).

### A pack already looks beside itself for another unit's launcher

`find_meow_scm` in `crates/meow/src/git.rs` takes `MEOW_SCM` first, then a
`meow-scm` directory beside the pack's own, then the newest `meow-scm` in the
plugin cache. That is a precedent for resolving another unit's file, built on
the cache layout, which the documentation doesn't promise.

## Comparison

| Option                                             | Better at                                         | Why it falls short                                                       |
| -------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------ |
| Keep a binary in each unit                         | Each unit works alone, the rule the records chose | 13 copies, 41 MB, and 12 feature builds on every release                 |
| One binary in `meow-core`, units depend on it      | One build, 7 MB, and one place for a fix          | Reverses two approved requirements, and a unit needs the core installed  |
| One binary in a new unit that the others depend on | Keeps `meow-core` free of a program               | A 17th unit for the same cost, and the owner asked for the core unit     |
| Download the binary at first use                   | Units stay small                                  | A network call at run time, which the records refuse                     |

## The case against

A unit that needs the core unit is no longer a harness on its own, and the
rule that it is has been held for a long time (ADR-1270,
`tools/check_standalone.py`). The core unit is the kernel, the one the other
units already assume, so the dependency points down and not sideways. A hook
that can't find the binary still has to report unresolved and never pass. The
documented data path depends on the core unit's session start having run, so
the first hook of a session can find nothing and must say so.

## Conclusions

1. The core unit ships the one build of the tool for every platform, with every
   unit's program in it, and the units ship no binary of their own (Findings:
   the archives of the 13 program units sum to 41 MB).
2. A unit that runs a program of the tool declares the core unit under
   `dependencies`, and no other unit (Findings: the manifest has a
   dependencies field).
3. A unit finds the shared binary through the core unit's data directory, whose
   path the platform documents, and not through the cache layout (Findings: a
   plugin's data directory is at a documented path; a dependency's `bin/` is on
   the Bash tool's PATH, and nothing says hooks).
4. A unit that finds no shared binary reports each of its checks unresolved and
   names the core unit as what would supply it (Findings: a pack already looks
   beside itself, and the case against).

## Sources

- [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference), read 2026-10-10 - the `dependencies` field and the data directory path.
- [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies), read 2026-10-10 - how dependencies install, resolve and are checked.
- [Add components to a plugin](https://code.claude.com/docs/en/plugins/components), read 2026-10-10 - the `bin/` directory and the Bash tool's PATH.
- `gh release view` of each unit's current release and of `meow-full-v0.1.0`, read 2026-10-10 - archive sizes.
- `crates/meow/src/git.rs` and `plugins/meow-scm/bin/meow-scm` as of pull request 880, read 2026-10-10 - the lookup and the launcher.
