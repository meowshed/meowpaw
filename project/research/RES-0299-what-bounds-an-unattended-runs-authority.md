---
id: RES-0299
artifact: research
status: approved
revised: 2026-09-28
elaborates: RES-0074
---

# An unattended run's authority is bounded by its flags and deny rules, except where a project's settings and the limits of Bash and Edit rules still reach it

## Summary

Claude Code 2.1.280, installed on this machine, has every flag RES-0074 named
for an unattended run: `-p`, `--bare`, `--plugin-dir`, `--permission-mode`,
`--permission-prompts none`, `--disallowed-tools`, `--output-format`,
`--max-budget-usd` and `--settings`. The documentation read on 2026-09-28 adds
three limits and one guarantee that RES-0074 didn't record. Under `--bare`, a
project's `env` block in its settings files still applies. A deny rule beats
an allow rule from any settings scope, which is the guarantee. A Bash deny rule
stops only the form Claude usually writes, so `Bash(git push *)` doesn't stop
`git -C . push origin main`. And an Edit deny rule doesn't reach a subprocess
that writes a file without naming it. `--bare` reads no subscription login, so
a bare run needs an API key in its environment or an `apiKeyHelper` in
`--settings`, and a key in the environment is visible to every command the run
executes.

This covers the flags and settings that bound what an unattended run may do
before it starts, and how a bare run authenticates. It doesn't cover the
sandbox, scrubbing credentials from a command's environment or the network,
which RES-0074 covers. No run was observed, because this session's permissions
refused to start one, so every statement about behaviour at run time comes
from the documentation or the installed help text.

## The question

RES-0074 concluded that an unattended run's authority is fixed before it
starts and that the run can't widen it, and that the harness is loaded by name.
The question is which flags and settings bound that authority on the Claude
Code installed today, and what each one leaves open.

The assumption behind the question is that a run's authority is what its
command line and settings say. That assumption fails wherever something the
repository commits reaches the run without appearing on its command line, so
the findings look for those paths first.

## Method

I read `claude --help` from Claude Code 2.1.280 on 2026-09-28. I read three
documentation pages the same day: the page on running Claude Code
programmatically, the permissions page and the CLI reference. I read the
permissions page from its full text. I read the other two through a
summarising reader, and I quote only what the installed help text or the full
permissions page confirms, because the summary of the CLI reference described
`--restricted`, `--setting-sources` and `--strict-mcp-config` differently from
the installed help text.

I tried to observe a bare run without credentials in a scratch repository
holding a `.mcp.json` server and a `SessionStart` hook, to read its `system/init`
event without spending anything. This session's permissions refused to start
`claude`, so no run was observed.

## Findings

### Every flag RES-0074 named exists in the installed version

`claude --help` from 2.1.280 lists `--bare`, `--plugin-dir <path>` (repeatable,
and "a folder of plugins loads each child"), `--plugin-url <url>`,
`--permission-mode` with the choices `acceptEdits`, `auto`,
`bypassPermissions`, `manual`, `dontAsk` and `plan`, `--permission-prompts`
with `host` and `none`, `--disallowed-tools`, `--output-format` with
`stream-json`, `--max-budget-usd` ("only works with --print") and `--settings
<file-or-json>`. The headless page says `--permission-prompts` needs 2.1.259 or
later. The units in this repository name 2.1.280 or 2.1.283 in their
`requires.toml`, both above 2.1.259.

The installed version, 2.1.280, is older than the 2.1.283 most units require,
so every finding here comes from a version below the one those units run on. A
flag that changed between the two versions wouldn't show in these findings.

### `--bare` loads plugins only by name, and a folder given to `--plugin-dir` is discovery

The headless page says `--bare` skips "auto-discovery of hooks, skills, custom
commands, subagents, installed plugins, MCP servers, auto memory, and
CLAUDE.md", and loads a plugin through `--plugin-dir` or `--plugin-url`. The
installed help says `--plugin-dir` given a folder of plugins loads each child,
so a run that passes the folder holding the units loads whatever that folder
contains. Loading by name therefore needs one `--plugin-dir` for each unit's
own directory.

The `system/init` event lists `plugins` that loaded and `plugin_errors` for
each that didn't, and a `--plugin-dir` failure still lets the run continue, the
headless page says. A run that checks nothing starts without a unit it named.

### A project's `env` block still reaches a bare run

The permissions page lists what a repository can supply to a `claude -p` run
in a folder never trusted, and says of `--bare`: "The project's `env` block and
helpers such as `awsAuthRefresh` in its settings files still apply, and Claude
Code reads `apiKeyHelper` only from `--settings`." So a committed
`.claude/settings.json` can set environment variables in a bare run, and those
variables appear on no command line the run was planned from.

The same page says `permissions.allow` rules in a project's
`.claude/settings.json` are "Not used" by a `-p` run in a folder never trusted.
It doesn't say whether a bare run reads the user's own `permissions.allow` or
the user's own `env` block, and nothing observed settles either.

### `--setting-sources` names which settings files load, and the help doesn't say what it does to the `env` block

`claude --help` from 2.1.280 describes `--setting-sources <sources>` only as a
"Comma-separated list of setting sources to load (user, project, local)". It
doesn't say whether leaving `project` out keeps the project's `env` block out
of a bare run, or whether an empty list is accepted. The summary of the CLI
reference described the flag differently, so whether `--setting-sources` or
`--restricted` keeps the `env` block out of a bare run is unknown.

### A deny rule wins over an allow rule from any scope

The permissions page says rules "are evaluated in order: deny, then ask, then
allow", that "an allow rule can't carve an exception out of a deny rule", and
that "a user-level deny blocks a project-level allow, because deny rules from
any scope are evaluated before allow rules". So a deny rule passed in
`--settings` holds whatever the other settings files allow. Managed settings
can add deny rules, and no allow rule from any scope overrides such a rule.

### A Bash deny rule covers the usual form of a command and no other

The permissions page gives `Bash(git push *)` as stopping `git push origin
main` and not `git -C . push origin main`, `git -c push.default=current push
origin main` or `git 'push' origin main`. It says such a rule "isn't a security
boundary around the program", and points to the sandbox for enforcement that
doesn't depend on the command's text.

### An Edit deny rule covers the file tools and the file commands Claude Code recognises

The permissions page says Edit deny rules apply to the built-in file tools, to
recognised file commands such as `sed` and `tee`, and to redirection targets.
They don't apply to "arbitrary subprocesses that read or write files
indirectly, like a Python or Node script that opens files itself". A path
beginning `//` is absolute from the filesystem root, and a single leading `/`
is relative to the settings source. A deny rule also applies where a symlink
resolves to the denied file.

### `bypassPermissions` lifts the protection on `.claude` and `.git`

The permissions page says that in `bypassPermissions` mode "Claude Code skips
permission prompts, including for writes to protected paths such as `.git` and
`.claude`", and that the mode belongs only in containers or virtual machines.

### `--bare` skips settings hooks and installed plugins' hooks

The installed help says `--bare` skips "hooks (those defined in settings and by
installed plugins)". A plugin passed through `--plugin-dir` is loaded for the
session, not installed, and neither the installed help nor the headless page
says whether its hooks run in a bare run.

### `--permission-prompts none` removes the tools that need a person

The headless page says that with `--permission-prompts none` anything that
would prompt is denied unless a `PermissionRequest` hook allows it, that
Claude is told not to retry, and that Claude Code "removes the tools that need
an answer from a person, such as `AskUserQuestion`". The permission mode and
the rules still decide each call first. With `--output-format stream-json`,
each denial appears as a `permission_denied` message and the result lists them
in `permission_denials`. The page's own streaming example passes `--verbose`
with `stream-json`.

### A bare run authenticates only by an API key or a helper passed in `--settings`

The headless page says that in bare mode Claude Code "never reads OAuth
credentials or the system keychain", and takes `ANTHROPIC_API_KEY` from the
environment or an `apiKeyHelper` from `--settings`. The installed help says
the same: "Anthropic auth is strictly ANTHROPIC_API_KEY or apiKeyHelper via
--settings (OAuth and keychain are never read)". So a bare run carries a
credential in its own environment, which RES-0074's finding on inherited
environments makes visible to every command the run executes unless it's
scrubbed. Neither page says whether a key an `apiKeyHelper` returns is placed
in the environment of the commands the run executes, so whether the helper
route keeps the key from them is unknown.

### The installed help describes a `--restricted` mode that ignores every settings file

`claude --help` from 2.1.280 says `--restricted` removes the tools that run
code unless `--tools` names them, "ignores user, project and local settings
files (managed settings and --settings still apply)", confines the file tools
to the working directories, refuses `bypassPermissions`, and lets only a
person or the permission handler approve writes to settings, git and
tool-configuration files. The summary of the CLI reference read the same day
described the flag differently, and no run was observed, so what `--tools`
must name for a run to keep its shell is unknown.

## Conclusions

1. An unattended run loads each unit through its own `--plugin-dir`, never a
   folder of units, because a folder loads whatever it contains.
2. Whatever starts an unattended run checks the `system/init` event's
   `plugins` against the units it named, because a unit that fails to load
   doesn't stop the run.
3. The deny rules that bound a run's authority are passed in `--settings`,
   because it's the one settings source visible on the run's command line and
   the help says it still applies under `--restricted`, and a deny rule there
   holds against an allow rule from any other scope.
4. A project settings file carrying an `env` block is part of an unattended
   run's authority that its command line doesn't show, because `--bare` still
   applies that block and whether `--setting-sources` or `--restricted` keeps
   it out is unknown.
5. A deny rule on pushing to a branch is stated as covering the usual form of
   the command only, because the documentation says it isn't a boundary, and
   enforcement that holds needs the sandbox.
6. A deny rule on editing a file is stated as covering the file tools and the
   recognised file commands only, because a subprocess that writes the file
   itself isn't matched.
7. Whether a bare run applies the user's own `permissions.allow` rules and the
   user's own `env` block is observed before a design relies on either answer,
   because the permissions page doesn't say and no run was observed.
8. `--restricted` and `--setting-sources` are observed before a design relies
   on them, because two descriptions of each read on the same day disagree.
9. An unattended run doesn't run in `bypassPermissions`, because that mode
   lifts the protection on `.claude` and `.git`, where a run could write an
   `env` block or rules that the next unattended run applies, and because the
   documentation keeps the mode to containers and virtual machines.
10. An unattended run's authority isn't enforced by a hook from settings or
    from an installed plugin, because a bare run skips both. Whether a bare run
    runs the hooks of a unit passed through `--plugin-dir` is observed before a
    design relies on either answer, because neither the help nor the headless
    page says.
11. Running every unattended run under `--bare` costs the subscription login.
    The run is billed through an API key, because a bare run reads only
    `ANTHROPIC_API_KEY` or an `apiKeyHelper`. A key in `ANTHROPIC_API_KEY` has
    to be kept out of the environment of every command the run executes,
    because RES-0074 found that a command inherits the run's environment.
    Whether an `apiKeyHelper` passed in `--settings` keeps the key out of that
    environment is observed before a design relies on it, because neither
    page says.

## Sources

- `claude --help`, Claude Code 2.1.280, read on this machine 2026-09-28 - the
  flags, their choices, `--plugin-dir` loading each child of a folder,
  `--bare` skipping settings hooks and installed plugins' hooks and its
  authentication, `--setting-sources`, and `--restricted` ignoring the
  settings files.
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless), read 2026-09-28 -
  what `--bare` skips and how it loads a plugin; the `system/init` event's
  `plugins` and `plugin_errors`; `--permission-prompts none` removing
  `AskUserQuestion` and needing 2.1.259; the denial messages; bare mode's
  authentication.
- [Configure permissions](https://code.claude.com/docs/en/permissions), read 2026-09-28 -
  in full: rule order and precedence across scopes; what a Bash rule doesn't
  match; the reach of Edit deny rules and their path anchors; what a `-p` run
  in an untrusted folder uses, including the `env` block under `--bare`.
- [CLI reference](https://code.claude.com/docs/en/cli-reference), read 2026-09-28 -
  through a summarising reader: the rows for `--bare`, `--plugin-dir`,
  `--plugin-url`, `--permission-mode`, `--permission-prompts`,
  `--disallowedTools` and `--max-budget-usd`, used only where the installed
  help text agrees.
- `plugins/*/requires.toml` in this repository, read 2026-09-28 - the Claude
  Code version each unit names.
- RES-0074, read 2026-09-28 - the gate table, the platform's unattended
  surface, the reason `--bare` matters and the finding on inherited
  environments.

## Open review findings

- RES-0001, round 1, findings 1 to 8 and 10: each is about content RES-0001
  held before this change, which adds only its index row. RES-0001 is
  approved, so each fix has to arrive as a new research record or through the
  amendment path, and the `<maintenance>` clause of `CLAUDE.md` that tells
  authors to index research in RES-0001 is outside this change. I left them for
  a change of their own.
- RES-0001, round 1, finding 11, allocation: RES-0299 is the first identifier
  in the block of five this work was allocated, and an identifier near
  RES-0059 or RES-0074 would collide with another block. I kept the identifier
  and changed "fixes" to "bounds" in the title and the index row.
- RES-0001, round 2, findings 2 to 9, and preference 10: the same content as
  round 1, reported again. RES-0001 is approved, so an edit to it would reword
  a frozen record, and each fix still needs a new record or the amendment
  path. Finding 1 is fixed: the index row now names the Edit rule's limit, the
  version read and that no run was observed. It leaves `--setting-sources`
  and `--restricted` to "no run observed", because naming them would widen
  the column and re-pad every row of an approved record. Preference 11 is
  met because RES-0299 is approved in the change that adds its row.
- RES-0299, round 2, preference 8: the RES-0001 entries stay here, because
  RES-0001 is approved and can't carry them, and the pull request that adds
  this record repeats them for whoever amends RES-0001.
