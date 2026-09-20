---
id: RES-0122
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0005
---

# mise

## Summary

mise is three things at once, which makes it the most informative runner and
the one with the largest surface to understand before its answers can be
trusted. Configuration merges from parent directories and the user's home, and
task sections replace rather than merge, so a task may be defined outside the
repository and may silently supersede one inside it. Trust is a security
boundary and the harness is on the outside of it: an untrusted configuration
yields nothing, and that is correct.

Research for one supported tool. mise is three things at once: a task runner, a
version manager and an environment manager. That makes it the most informative
of the runners, and the one with the largest surface a pack understands before
it trusts what it reads.

It covers what marks a mise project, how tasks are declared and enumerated, and
where a task definition comes from. It also covers what trust means and why the
harness cannot grant it, what the pack authors, and what the skill has to
contain.

It does not cover the class of task runners, which is
[RES-0121-task-runners.md](RES-0121-task-runners.md).

## The question

A runner pack exists to read the project's own answer to _what does test mean
here_ rather than guess it. mise answers that, and it answers three other
questions at the same time: which toolchain versions this project pins, which
environment variables it expects, and what may run at all.

So the question is how much of that a pack may rely on, and where reading it is
itself an action with consequences.

## Method

We fetched and read the vendor documentation on 2026-09-20. The configuration
page gave the precedence order and the per-section merge rules, and the trust
command's page gave what an untrusted configuration does. The task
configuration page gave the full field set and the freshness rule, and the
development-tools page gave backends, the lockfile and activation.

The two-shape task model - table entries against executable files - was read
from the tasks pages rather than inferred, because it is the reason parsing the
configuration file alone is insufficient.

Nothing was installed or run, and no repository was left untrusted to observe
the behaviour described.

## Findings

### Configuration is hierarchical and reaches outside the repository

mise reads configuration in a defined precedence order, highest first:

1. `mise.local.toml` - personal overrides, not committed
2. `mise.toml` - the project's file
3. `mise/config.toml`, then `mise/conf.d/*.toml`
4. `.mise/config.toml` and `.mise/conf.d/*.toml`
5. `.config/mise/config.toml` and `.config/mise/conf.d/*.toml`
6. `~/.config/mise/config.toml` - the user's global configuration
7. `/etc/mise/config.toml` - system defaults

It also searches parent directories to the filesystem root, merging as it goes,
with child directories taking precedence over parents.

That list contains the finding. **A task mise runs may be defined outside the
repository**, in the user's home configuration or a parent directory. A pack
reporting the task list as _what this repository declares_ is wrong. What mise
reports is what _this machine, in this directory_ resolves to, which is not the
same claim and does not reproduce elsewhere.

The merge rules differ per section and the difference matters: `[tools]` are
additive with overrides, `[env]` overlays, and `[tasks]` **replace earlier
definitions entirely**. So a task of the same name in a higher-precedence file
does not extend the project's - it supersedes it silently.

Environment-specific files - `mise.development.toml`, `mise.windows.toml` - are
selected by `MISE_ENV` or the `auto_env` setting, which adds a second axis
along which the same directory resolves differently.

### Trust is a security boundary, and the harness is on the wrong side of it

mise requires a configuration to be trusted before it will parse and execute
it, because a configuration _"may execute code or affect the environment"_.
Without trust, mise _"may prompt, skip the config in some discovery paths, or
fail with an untrusted-config error when it cannot prompt."_

Not everything needs it: a file containing only `min_version`, plain `[tools]`
entries with literal version strings, and simple `[tasks]` without templates is
safe and does not require trust.

Three consequences follow, and they are the most important findings in this
document.

An untrusted repository yields nothing, and that is correct. A pack that sees
an empty or failing task list in a fresh clone is watching the security model
work, and no tool is broken. It reports that distinctly from _this project
declares no tasks_.

The harness must not run `mise trust` on the user's behalf. Trusting a
configuration is authorising code that came with a repository to run with the
user's environment. That is a decision for the person, and a harness that
grants it to make its own reporting smoother has removed the protection
silently. The pack surfaces the state and the command; the person runs it.

A cloned repository is the dangerous case. The threat model mise is
defending against is exactly the one a harness walks into: reading an
unfamiliar repository someone else wrote.

### Tasks come in two shapes, and reading one of them is reading half

TOML tasks live under `[tasks.<name>]` in `mise.toml` and suit short commands.
File tasks are executable scripts under `mise-tasks/` or another configured
task directory, and on macOS and Linux they need the executable bit.

A pack that parses only the TOML sees half the tasks. The enumeration command
is the only correct source.

### The task model is richer than the other runners', and the richness is readable

A task may declare:

| Field                | What it says                                                       |
| -------------------- | ------------------------------------------------------------------ |
| `run`                | The commands, inline or as a script, with parallel groups          |
| `depends`            | Prerequisites, shared ones running once                            |
| `depends_post`       | Cleanup that runs after, including its own dependency chain        |
| `wait_for`           | Waits on a task only if it is already scheduled, without adding it |
| `sources`, `outputs` | Inputs and outputs, for freshness                                  |
| `dir`                | The working directory, defaulting to the configuration root        |
| `env`                | Task-scoped environment variables                                  |
| `tools`              | The tool versions this task needs                                  |
| `usage`              | Arguments and flags, parsed into the invocation                    |
| `confirm`            | A prompt before the task runs                                      |
| `hide`               | Excluded from help and completion                                  |

Two of these change how a pack invokes a task rather than only how it describes
one.

`usage` means a task may take arguments and flags. A verb bound to a task
with required arguments cannot be invoked bare, which is the same trap just
recipes have, and the specification is declared rather than guessed at.

`confirm` means a task may be interactive by declaration. An automated run
either supplies the confirmation or skips the task, and skipping is the honest
default. A task whose author asked for confirmation is one whose author did not
want it run unattended.

### Freshness is real caching, and a skipped task is not a passing task

When `sources` and `outputs` are both declared, mise skips the task when the
newest source is older than the oldest output. The task definition itself
counts as an implicit source, so changing the task invalidates the cache.

For a harness this is a reporting problem rather than a performance feature. A
`test` verb that mise skipped as fresh did not run the tests, and evidence
citing it is citing a previous run. The pack reports _skipped as fresh_
distinctly from _passed_, or the evidence is a lie with a green tick on it.

### mise is also a version manager, which is what a mise pack buys beyond a

runner

mise installs tools and selects versions per project, across backends: its own
registry, aqua, cargo, npm, pipx, GitHub, GitLab, Forgejo, HTTP, S3, vfox
plugins and asdf plugins for compatibility. Tools may declare `os`
restrictions, `depends` on other tools, and postinstall commands.

`mise.lock` records resolved versions without replacing the version requests in
`mise.toml`, which separates what the project asked for from what it got - the
same separation a package lockfile makes.

Activation is either shell integration that updates `PATH` at each prompt, or
`mise exec -- <command>` and `mise run <task>` without touching shell startup
files, or shims for programs needing a stable path. For a harness the middle
one is the right answer, for the same reason `uv run` is in Python: it does not
depend on what the shell did first.

The consequence for verb resolution is the useful one. **A mise pack can tell
the harness which toolchain the project pins**, which is the question every
language pack answers by detection, answered here by declaration.

Idiomatic version files - `.node-version`, `.python-version`, `.nvmrc` - are
supported but **disabled by default**, for discovery cost, and enabled per tool
through a setting. So a repository with a `.python-version` and a mise
configuration may be pinning two different versions, and only one of them is in
effect. And mise reads only the field declaring the version the project is
built with, not a minimum or a floor.

### What the pack authors

`mise.toml` - tasks, tool versions, environment - as structured data. Never
`mise.local.toml`, which is the user's and is not committed.

Adding a tool is a two-part change: the request in `mise.toml` and the resolved
version in `mise.lock`, and writing one without the other leaves the project in
a state where a fresh machine resolves differently.

### What a reviewer needs that no command reports

Whether a task's `sources` and `outputs` are complete. An incomplete `sources`
list produces a task that is skipped where it should have run, which is the
failure mode of every caching build system and the one nothing detects.

Whether `depends` describes real ordering or accidental ordering that happens
to work.

Whether a tool version is pinned exactly or loosely, and whether the lockfile
agrees with the request.

Whether the environment section carries anything that should not be in a
committed file, which is the same question every environment mechanism raises.

### What the skill has to contain

In the body, in this order:

1. Trust, first. What an untrusted configuration does, that the harness
   does not grant trust, and how to report the state.
2. Where configuration comes from, including outside the repository, and
   that `[tasks]` replace rather than merge.
3. Enumeration. `mise tasks ls --json`, and that file tasks exist beside
   TOML tasks so parsing the file is not enough.
4. Invocation rules. `mise run` or `mise exec` rather than a shell; a task
   with `usage` arguments is not callable bare; a task with `confirm` is not
   run unattended.
5. Reporting rules. Skipped-as-fresh is not passed. A task defined outside
   the repository is reported as such.
6. What must never happen. Running `mise trust`. Writing
   `mise.local.toml`. Reporting a resolved task list as the repository's
   declaration. Citing a skipped task as evidence.

In supporting files: the configuration precedence list; the task field
table; the backend list and the lockfile relationship; the idiomatic version
file setting; and the dated facts with what to re-check.

## Conclusions

1. A mise project is marked by `mise.toml` and the other configuration
   paths in its precedence list, including directory-scoped and dotted
   variants.
2. Tasks are enumerated with `mise tasks ls --json`, never by parsing the
   TOML, because file tasks under `mise-tasks/` are not in it.
3. A resolved task list is reported as resolved, not as declared, since
   configuration is merged from parent directories and the user's home and
   does not reproduce on another machine.
4. A task defined outside the repository is named as such in the report,
   because a verb bound to it is not reproducible for anyone else.
5. `[tasks]` replace rather than merge, so a same-named task in a
   higher-precedence file supersedes the project's silently, which the pack
   detects and reports.
6. The harness never runs `mise trust`. Trust authorises repository code to
   run in the user's environment, and granting it to smooth reporting removes a
   protection the tool exists to provide.
7. An untrusted configuration is reported as untrusted, distinctly from a
   project that declares no tasks, because the two look identical and mean
   opposite things.
8. A task declaring `usage` arguments is invoked with them, since the
   specification is declared and a bare invocation is wrong.
9. A task declaring `confirm` is not run unattended, because its author
   asked for a person.
10. A task skipped as fresh is reported as skipped, never as passed, and is
    not cited as evidence, since the run did not happen.
11. Commands run through `mise exec` or `mise run` rather than a shell,
    so the result does not depend on shell activation.
12. A mise pack reports the pinned toolchain to the harness, which is the
    question language packs answer by detection and mise answers by
    declaration.
13. A `.python-version` beside a mise configuration is reported as possibly
    inert, because idiomatic version files are disabled by default and
    enabled per tool.
14. A tool added by the pack updates both `mise.toml` and `mise.lock`, or a
    fresh machine resolves a different version.
15. `mise.local.toml` is never written by the pack, because it is the
    user's and is not committed.
16. The skill body carries trust, configuration provenance, enumeration,
    invocation rules, reporting rules, and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [mise configuration](https://mise.jdx.dev/configuration.html) - the full
  precedence order from `mise.local.toml` down to `/etc/mise/config.toml`; the
  search of parent directories to the filesystem root with child directories
  taking precedence; the per-section merge rules where `[tools]` are additive,
  `[env]` overlays and `[tasks]` replace earlier definitions entirely;
  environment-specific and platform files selected by `MISE_ENV` or `auto_env`;
  and idiomatic version files disabled by default, enabled per tool, and read
  only for the version the project is built with.
- [mise trust](https://mise.jdx.dev/cli/trust.html) - that trust allows mise to
  read configuration which may execute code or affect the environment; that
  without trust mise may prompt, skip the configuration in some discovery
  paths, or fail with an untrusted-config error when it cannot prompt; and that
  a file containing only `min_version`, plain `[tools]` entries and simple
  `[tasks]` without templates does not require trust.
- [mise task configuration](https://mise.jdx.dev/tasks/task-configuration.html)
  - the task fields `run`, `depends`, `depends_post`, `wait_for`, `sources`,
    `outputs`, `dir`, `env`, `tools`, `usage`, `hide` and `confirm`; that shared
    dependencies run once and a `depends_post` chain runs after the parent
    finishes; and the freshness rule skipping a task when the newest source is
    older than the oldest output, with the task definition as an implicit source.
- [mise dev tools](https://mise.jdx.dev/dev-tools/) - per-project version
  selection; the backends including aqua, cargo, npm, pipx, GitHub, GitLab,
  Forgejo, HTTP, S3, vfox and asdf plugins; the `os` and `depends` fields and
  postinstall commands; `mise.lock` recording resolved versions without
  replacing the requests in `mise.toml`; and activation through shell
  integration, `mise exec`, `mise run` or shims.
- [mise tasks](https://mise.jdx.dev/tasks/) and
  [mise tasks ls](https://mise.jdx.dev/cli/tasks/ls.html) - TOML tasks under
  `[tasks.<name>]` against file tasks under `mise-tasks/` requiring the
  executable bit; and the `-J --json` flag alongside `--name-only`, `--hidden`
  and `--all`.
