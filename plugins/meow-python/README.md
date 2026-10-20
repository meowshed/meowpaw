---
reader: someone choosing or running meow-python
answers: what meow-python does, what it adds to a session and how to run it
kind: reference
describes: [meow-python@0.1.0]
---

# meow-python

`meow-python` tells you which Python projects your repository holds, which
environment tool each declares, and which tools each configured. It prints a
`[stages]` table bound from that configuration, with every tool run through the
environment, and checks that your stages apply no fix and keep each tool's
cache out of the working tree. Its skill tells Claude Code what a reviewer of
Python checks that no command reports. It writes no file. `status`, `bind` and
`check` read the files git tracks and run git alone, so they start neither
Python nor a tool they name. It installs on its own, with no other part of the
`meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://paw.retran.me/meowpaw/marketplace.json
claude plugin install meow-python@meowpaw
```

Installing this unit also enables `meow-core`, which ships the shared `paw` binary its launcher runs, and the platform keeps `meow-core` enabled while this unit is on, so you can't disable `meow-core` alone.

Its launcher stops on a Claude Code older than the version its `requires.toml` names, printing both versions, because the unit's behaviour was never seen on an older one.

## Run it

Claude Code puts the unit's `bin/` directory on its Bash tool's `PATH`, so
Claude Code runs it in your repository as:

```bash
meow-python status
```

From your own shell, run the same launcher by its path in the installed unit.

The program counts a repository as Python where git tracks a `pyproject.toml`.
It reports once for each directory that holds one, so a repository with two
projects gets two reports. A `setup.py`, `setup.cfg` or `requirements.txt`
beside a `pyproject.toml` is named as an older layout, and one without a
`pyproject.toml` makes no project, because it predates the convention.

`status` prints, for each project directory:

1. `scope: <directory>`, or `scope: <part> <directory>` where your profile's
   `[parts]` declares a part holding it.
2. `marker: <file>`, and `older layout: <file>` for each file named above.
3. `environment: <tool>, declared by <file>`, `environment: none declared`, or
   `environment: unresolved, <reason>`.
4. `pinned: python <version> in .python-version` where the file is tracked.
   `status` compares it with no installed interpreter, because it starts no
   tool.
5. `configured: <file>: <tool>` for each configuration it recognises: Ruff,
   mypy, pyright, pyrefly, ty, pytest, `noxfile.py` and `tox.ini`.

Every command that reads the profile first prints its state, `profile: absent`,
`profile: unparseable` or `profile: parsed`, and `unknown key: <path>` for
each key no unit reads. `bind` prints them on standard error, so what it
prints on standard output stays ready to paste. None of them changes the exit
status.

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
pytest's cache plugin and the interpreter's bytecode with `-p
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

When Claude Code reviews Python, the skill has it read the environment and the
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

## What it needs

Claude Code 2.1.280 or later, declared in `plugins/meow-python/requires.toml`,
and git. The pack is current as of Ruff 0.17.0, mypy 2.4.0, pyright 1.1.414,
pyrefly 1.3.2, ty 0.0.86, pytest 9.1.1, uv 0.13.0, Poetry 2.5.1 and PDM 2.29.2.
