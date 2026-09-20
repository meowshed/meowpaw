---
id: RES-0004
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The platform

## Summary

The platform supports a marketplace of small plugins with declared
dependencies, so no installer of the harness's own is wanted. Commands and
skills are one mechanism, which collapses a distinction an earlier reading of
this page treated as real. Every contract between plugins is a file format or a
command, hook ordering between plugins is unsupportable, and the loading tiers
set the size budgets, which no preference of the harness's decides.

What Claude Code's plugin system actually provides, and what Anthropic's
prompting guidance says about how the documents inside a plugin should be
written. Both constrain the design, so both are recorded before it.

Sources: the [plugin reference](https://code.claude.com/docs/en/plugins-reference)
and the [prompt engineering guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

## Method

The published platform documentation was read on 2026-09-20: the plugin
reference, slash commands, skills, hooks, settings, permissions and the
prompting guidance. The sources section names what was taken from each.

Every page on that list is living documentation that changes under the same
address, so each entry is something to re-check and no settled fact, and the
date is part of the claim.

One finding corrects an earlier reading and observes nothing new: that commands
and skills are one mechanism contradicts an earlier reading of the same pages
by this project. The earlier reading is not preserved, so the correction is
recorded here, where a diff would have shown it.

Nothing was measured. Claims about cost in this document come from the
documentation's own statements and from the separate measurement recorded in
the skill-format research.

The session's tool record survives and was consulted for this section. It shows
these pages fetched directly, and read through no summaries, and it shows the
same pages fetched more than once as the reading was corrected.

## What a plugin can contain

```text
plugin-name/
  .claude-plugin/plugin.json    manifest
  skills/<name>/SKILL.md        progressive-disclosure skills, auto-discovered
  commands/<name>.md            slash commands
  agents/<name>.md              subagent definitions
  hooks/hooks.json              event hooks
  workflows/                    workflow scripts
  monitors/monitors.json        background processes
  output-styles/, themes/       presentation
  .mcp.json, .lsp.json          servers
  bin/, scripts/                executables on the Bash PATH
```

The parts that matter for this design:

Manifest. `name` is the only required field. `version`, `description`,
`author`, `license`, `keywords` and `homepage` are metadata. Two fields are
load-bearing here:

- `dependencies`, which takes plugin names with optional version ranges. This
  is what lets `meow-core` pull the method layer without a monolith.
- `userConfig`, typed per key (`string`, `number`, `boolean`, `directory`,
  `file`), with `sensitive` values stored in the OS keychain. Values reach
  skills and agents as `${user_config.KEY}` and hooks as
  `CLAUDE_PLUGIN_OPTION_<KEY>`.

Path behaviour. `skills` _extends_ the default `skills/` directory;
`commands`, `agents`, `workflows`, `outputStyles` and the experimental keys
_replace_ their defaults; `hooks`, `mcpServers` and `lspServers` _merge_ across
plugins. The merge behaviour of hooks is what allows several packs to attach
quality hooks without fighting.

Hooks. Events include `SessionStart`, `Setup`, `UserPromptSubmit`,
`PreToolUse`, `PostToolUse` and `PermissionRequest`. Hook types are `command`,
`http`, `mcp_tool`, `prompt` and `agent`. The mechanism `hephaestus` relies on

- a `PostToolUse` command hook that exits non-zero so its output is fed back to
  the model - is a documented pattern, and no trick.

Environment. `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` (a persistent
per-plugin directory under `~/.claude/plugins/data/`) and
`${CLAUDE_PROJECT_DIR}` resolve inside skill and agent content, hook commands,
and server configuration. `${CLAUDE_PLUGIN_DATA}` is a candidate home for run
state; a git-root key is still needed, because one plugin serves many
repositories.

Agents. Front matter takes `model`, `effort`, `maxTurns`, `tools`,
`disallowedTools`, `skills`, `memory`, `background` and `isolation:
"worktree"`. Two of these decide whether the `superpowers` dispatch pattern is
reproducible without a bespoke runtime: `tools` narrows what a reviewer can do,
and `isolation: "worktree"` gives an implementer its own checkout.

Evals. `claude plugin eval` runs a suite from a plugin's eval directory
(`experimental.evals`) and produces JSON and a report. This is the only
mechanism available for checking a requirement whose obligation is genuinely
about model behaviour.

Marketplace. A repository with `.claude-plugin/marketplace.json` is added
with `/plugin marketplace add <owner>/<repo>`, and plugins install as
`<plugin>@<marketplace>`. Marketplace plugins are cached per version under
`~/.claude/plugins/cache/`, and Node dependencies are installed from a lockfile
with no lifecycle scripts and a sixty-second timeout.

Skills directories. A directory with `.claude-plugin/plugin.json` under
`~/.claude/skills/` or a trusted `<cwd>/.claude/skills/` loads in place as
`<name>@skills-dir`. Useful for developing a plugin against a real repository
without publishing.

## Commands are skills now

The most consequential platform fact for this design, and one that contradicts
how every surveyed harness is built: **a custom slash command is a skill.**
`.claude/skills/<name>/SKILL.md` with frontmatter; the directory name becomes
the command. `.claude/commands/<name>.md` still works for compatibility, and
skills are preferred for new work because only they can carry supporting files.

The frontmatter that matters:

| Field                      | Does                                                               |
| -------------------------- | ------------------------------------------------------------------ |
| `description`              | What it does, and what Claude decides invocation on                |
| `argument-hint`            | Shown in autocomplete, such as `[issue-number]`                    |
| `arguments`                | Named arguments, referenced as `$name`                             |
| `allowed-tools`            | Pre-approves tools for this invocation, such as `Bash(git *) Read` |
| `model`, `effort`          | Override the session's model or effort for this command            |
| `disable-model-invocation` | `true` makes it user-only - Claude cannot invoke it                |
| `user-invocable`           | `false` hides it from the `/` menu - Claude-only                   |

Arguments: `$ARGUMENTS` for everything, `$0`-`$9` or `$ARGUMENTS[N]` positional,
or named through the `arguments` field. Namespacing is by subdirectory, and `/`
becomes `:` - `skills/meow/spec/SKILL.md` is `/meow:spec`.

Two capabilities no surveyed harness uses, and both are directly useful here:

- **Shell injection.** `` !`command` `` runs before the model sees the skill and
  injects the output. A non-zero exit **aborts the whole invocation**, so an
  expected failure needs `|| true`. Injected commands are checked against
  permission rules, which is what `allowed-tools` pre-approves.
- **File references.** `@path/to/file` inlines a file.

Together these mean a command can arrive with its context already gathered -
the profile, the pending gate, the current diff - and spend no turns fetching
it.

### What this changes for the design

The design distinguishes a **command** (a procedure, no reasons, tight budget)
from a **skill** (a judgement, reasons included). That distinction is still
right - it is what `vlie` demonstrates in practice - but it is now a convention
within one mechanism, where this project used to read two.

Three consequences:

1. Everything in section 13 about tiers, budgets and format applies to commands
   too, because they are loaded the same way. 2. `disable-model-invocation` is
   how a command that must not fire on its own - a gate, a release, a long run
   - is made user-only. That is a real safety control the design uses, where
     prose controls nothing. 3. A command's `description` is charged in every
     session like any skill's, so twenty commands is twenty descriptions. The
     budget applies to them too.

## What this rules in and out

- A marketplace of small plugins with declared dependencies is directly
  supported; no custom installer is needed. - Hook merging means a pack can
  attach an edit-time quality gate without coordinating with the kernel. -
  `userConfig` covers per-machine settings, so nothing secret needs to live in
  a committed file. - Plugins share no runtime and no memory beyond the
  filesystem. **Every contract between plugins is therefore a file format or a
  command, and must be specified as one.** - Nothing in the platform enforces
  ordering between hooks from different plugins. A design that needs "the
  kernel's hook runs before the pack's" is unsupportable and must be avoided.

## How the documents should be written

Anthropic's current guidance, applied to skills, commands and agent
definitions:

- **XML tags disambiguate** a prompt that mixes instructions, context, examples
  and input. Use a consistent tag vocabulary across the whole harness, and nest
  tags where the content has a natural hierarchy. - **Match the prompt's style
  to the intended output.** A skill written as terse bullets tends to produce
  terse bullets; a skill whose prose states reasons tends to produce work that
  states reasons. - **Be explicit about scope and stopping.** Current models
  follow an explicit boundary well, and over-verification instructions carried
  over from older prompt styles cost tokens without improving the result on the
  newest models. - **Ask for self-checks against named criteria**, because a
  general request checks nothing.

Two observations from the internal harnesses agree with this and sharpen it.
`meowctl`'s writing skill contrasts two samples of the same facts: one with an
author, a reader and a reason, and one written as truths handed down by nobody
in particular. The second is what most harness prompts read like. And a rule
whose reason is stated survives contact with a case its author did not foresee,
because the model can tell whether the reason applies; a rule without one gets
applied literally and wrongly.

The house tag vocabulary that follows from this is fixed in the design.

## Conclusions

1. A marketplace of small plugins with declared dependencies is supported
   directly. No installer of the harness's own is needed or wanted. 2. Commands
   and skills are one mechanism now. The harness has one kind of loadable unit
   to design for, and the distinction it keeps between a command and a skill is
   a convention inside that one mechanism. 3. Every contract between plugins is
   a file format or a command. Plugins share no runtime and no memory beyond
   the filesystem, so any contract the design assumes must be written down as
   one of those two. 4. Ordering between hooks from different plugins is
   unsupportable. A design that needs the kernel's hook to run before a pack's
   cannot be built, and must not be proposed. 5. Per-machine and secret
   configuration has a supported home outside the repository, so nothing secret
   needs to live in a committed file. 6. The loading tiers set the budgets. A
   description is paid for in every session, a body only on invocation, and
   supporting files only on demand. The size limits that follow are the
   platform's, and no preference of the harness's sets them. This document
   counted three tiers; there are six, and the three above the skill are
   enumerated in
   [RES-0202-progressive-disclosure.md](RES-0202-progressive-disclosure.md). 7.
   Prompts are written to match their intended output. Terse bullets produce
   terse work; prose that states reasons produces work that states reasons. A
   rule whose reason is stated survives a case its author did not foresee. 8.
   The platform can evaluate a plugin, which makes a change to the harness
   measurable, where an argument settles nothing.

## Sources

All read 2026-09-20. Every page on this list is living documentation that
changes under the same address, so each is something to re-check and no settled
fact. The commands-are-skills change below was itself a correction of an
earlier reading.

- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference)
  - manifest schema, component paths, hook events, environment variables,
    marketplace and caching behaviour.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) - that a
  command is a skill, the frontmatter fields, argument forms, shell injection,
  file references, namespacing, backward compatibility.
- [Agent Skills](https://code.claude.com/docs/en/skills) - the loading tiers,
  the description budget, compaction behaviour, `/skill-doctor`.
- [Configure permissions](https://code.claude.com/docs/en/permissions) -
  permission rule syntax, wildcard semantics, the limits of a Bash rule.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  - XML structuring, tag consistency, style propagation, scope and stopping.
