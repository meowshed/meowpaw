---
reader: someone installing or running meow-python on Pi
answers: what meow-python provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-python@0.2.1]
---

# @meowshed/meow-python

Detects a Python project from the pyproject.toml git tracks, reads the environment tool it declares, prints a stages table bound from the tools it configured and run through that environment, reports a stage that runs a tool outside the environment or lets a tool write into the working tree, and carries what a reviewer of Python checks that no command reports, writing no file. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-python
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

## The environment

The program reads the environment tool from what you committed, and never from
what is installed. A `uv.lock` or a `[tool.uv]` table declares `uv`, a
`poetry.lock` or a `[tool.poetry]` table declares `poetry`, and a `pdm.lock` or
a `[tool.pdm]` table declares `pdm`. A tool runs through it as `uv run <tool>`,
`poetry run <tool>` or `pdm run <tool>`, so the interpreter is the project's
and not whatever the shell finds first.

With none declared, `bind` still binds the tools you configured, run bare, and
adds a comment under each saying the interpreter that runs the tool is
whatever the shell finds. With two declared, every stage is unresolved and the
reason names both files.

## Bind your stages

`meow-python bind [<directory>]` prints a `[stages]` table for the project in
`<directory>`, or the root, to paste into the profile file its first line
names. It never writes the profile itself:

```toml
[stages]
format = "uv run ruff format --check --cache-dir \"${TMPDIR:-/tmp}/ruff-cache\" ."
lint = "uv run ruff check --cache-dir \"${TMPDIR:-/tmp}/ruff-cache\" ."
check = "uv run mypy --cache-dir=/dev/null"
test = "uv run python -B -m pytest -p no:cacheprovider"
# build: unbound, pyproject.toml names the build backend hatchling.build, and this pack binds no build
```

Each stage takes the first binding that applies:

| Stage    | Bound to                                  | When                                                                          |
| -------- | ----------------------------------------- | ----------------------------------------------------------------------------- |
| `format` | `ruff format --check ... .`               | A `.ruff.toml`, `ruff.toml` or `[tool.ruff]`                                  |
| `lint`   | `ruff check ... .`                        | A `.ruff.toml`, `ruff.toml` or `[tool.ruff]`                                  |
| `check`  | `mypy --cache-dir=/dev/null`              | A `mypy.ini`, `.mypy.ini`, `[tool.mypy]` or a `[mypy]` section of `setup.cfg` |
| `check`  | `pyright`                                 | A `pyrightconfig.json` or `[tool.pyright]`                                    |
| `check`  | `pyrefly check`                           | A `pyrefly.toml` or `[tool.pyrefly]`                                          |
| `check`  | `ty check`                                | A `ty.toml` or `[tool.ty]`                                                    |
| `test`   | `python -B -m pytest -p no:cacheprovider` | Any of the seven files pytest reads                                           |
| `build`  | nothing, printed as unbound               | Always, naming the build backend                                              |

The four type checkers disagree about what an error is, so the pack never
picks one: `check` binds the first in this table that you configured, and a
comment names the others. With none configured the stage is printed unbound,
which is an outcome and no failure. `bind` selects no Ruff rule group, so the
rules are the ones your configuration names, and a comment says a default
configuration leaves Ruff's security rules off. It passes no `--fix` and no
`--unsafe-fixes`.

Ruff, mypy and pytest write a cache into the working tree unless told not to.
The bindings point Ruff's cache at `${TMPDIR:-/tmp}/ruff-cache`, write no mypy
cache under `--cache-dir=/dev/null` (the form for a Unix system), and stop
pytest's cache package and the interpreter's bytecode with `-p
no:cacheprovider` and `-B`.

pytest runs the examples in your docstrings only under `--doctest-modules`. A
comment under `test` says the stage doesn't run them where the `addopts` of the
pytest configuration that applies holds neither `--doctest-modules` nor
`--doctest-glob`. Where the environment is `uv`, a comment says `uv run` brings
the environment up to date before it runs, so a stage may write into `.venv`.
`bind` prints nothing for a stage your profile already declares, names a
`mise.toml` or a `Taskfile.yml` with the runner's pack, `meow-mise` or
`meow-gotask`, and exits 0 once it prints the table.

## Check your settings

`meow-python check [<directory>]` reads the stages of the profile that governs
the project and reports each setting that is missing or has no effect, one line
for each finding, and exits 1 on any:

| Line                                                                      | When                                                                                                         |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `<stage> runs <tool> outside <environment>: write <prefix> <tool>`        | A stage runs Ruff, mypy, pyright, pyrefly, ty or pytest by its bare name, `python -m` included               |
| `<file> and <file> both declare an environment`                           | Two environment tools apply to the project                                                                   |
| `ruff would apply unsafe fixes: remove --unsafe-fixes`                    | A stage runs Ruff with `--unsafe-fixes`                                                                      |
| `ruff applies fixes in a check: remove --fix`                             | The `format` or `lint` stage runs Ruff with `--fix`                                                          |
| `ruff format rewrites the tree: pass --check`                             | A stage runs `ruff format` with neither `--check` nor `--diff`                                               |
| `ruff writes .ruff_cache into the tree: pass --cache-dir`                 | A stage runs Ruff with no `--cache-dir` and no `RUFF_CACHE_DIR`, and no tracked ignore file covers the cache |
| `mypy writes .mypy_cache into the tree: pass --cache-dir=/dev/null`       | A stage runs mypy with no `--cache-dir`, and no tracked ignore file covers the cache                         |
| `pytest writes .pytest_cache into the tree: pass -p no:cacheprovider`     | A stage runs pytest without the flag, and no tracked ignore file covers the cache                            |
| `<file> configures <tool> and <file> does too: <tool> reads <file> alone` | Two files configure Ruff, mypy, ty or pytest, which reads one alone                                          |

A word after an environment tool's `run` runs that tool through it. A command
that runs a tool through a runner's task, such as `mise run lint`, isn't read.
With no finding it prints `no findings`, followed on the same line by the
groups it checked: the environment, the fixes, the caches and the
configuration files. `check` runs no Ruff, so it names none of Ruff's rule
groups. It exits 3 where the profile is missing or doesn't parse.

## Generated files

Commit the lockfile your environment tool writes (`uv.lock`, `poetry.lock` or
`pdm.lock`), because it is the resolved dependency set every collaborator and
every CI run installs from, and edit it through the tool and never by hand.
Ignore `.venv/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`,
`__pycache__/` and `*.egg-info/`, because the next run regenerates each.

## What it reports instead of a table

Every command exits 0 when it reports what it was asked, `check` exits 1 on a
finding, and every command exits 3 when it can't:

| Line                                                                       | Means                                                             |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `unresolved: not a Python repository`                                      | Git tracks no `pyproject.toml`                                    |
| `unresolved: <directory> holds no pyproject.toml; one is in <directories>` | The directory you named has no tracked `pyproject.toml`           |
| `unresolved: <file> doesn't parse as TOML: ...`                            | A `pyproject.toml` isn't valid TOML; the parser's message follows |
| `unresolved: no profile at <path>`                                         | `check` found no profile                                          |
| `unresolved: the profile doesn't parse: ...`                               | The profile isn't valid TOML; the parser's message follows        |

## Review code

When Pi reviews Python, the skill has it read the environment and the
configured tools first, and then load `reviewing.md`, which holds eight points
no command reports: decorative typing, import-time side effects, mutable
defaults, fixture scope and test order, the clean import, the claimed
interpreter versions, and the absence of an architecture check and of a check
for unused dependencies. The skill never passes `--unsafe-fixes`, never
guesses a type checker, never runs `pip-audit --fix` in a verification step,
never edits a lockfile by hand and never reports a default `ruff check` as a
security pass.

## What it costs you

The skill's description stays in context on every turn, and `reviewing.md`
costs context only when code is reviewed. The program is a native binary shipped
inside the unit, and needs git on the machine. It runs no Python tool and
reaches no network. On a machine the unit carries no binary for, it reports
the repository as unresolved and exits 3.

## Read a subcommand's help

`meow-python --help` lists the subcommands, and `meow-python <subcommand>
--help` names what it determines, what you read to reach the same answer
without the tool, and the first word of each kind of line it prints. A test
holds each subcommand's output to those words.
