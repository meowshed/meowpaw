---
id: SPC-1330
artifact: spec
status: live
revised: 2026-10-20
states:
  [
    REQ-0083,
    REQ-0085,
    REQ-0133,
    REQ-2336,
    REQ-2412,
    REQ-2420,
    REQ-2426,
    REQ-2432,
    REQ-2434,
    REQ-2442,
    REQ-2450,
    REQ-3048,
  ]
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# The Python pack

## Scope

This covers `meow-python`, the language pack for Python. It states what
`status` detects and lists, which environment each project runs its tools
through, what `bind` prints and what `check` finds, and what the skill and
`reviewing.md` carry.

Every rule SPC-1190 states for a language pack holds here, and this document
states only what is Python's. It leaves the matrix runners, coverage, the
supply-chain check and the type checker the repository never configured
unbound. Running a stage is SPC-1040's.

ADR-2660 orders the packs and EPC-2560 realises this one.

## Boundary

| Surface                                          | What it is                                                            |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| `plugins/meow-python/bin/meow-python`            | The program: `status`, `bind [<directory>]` and `check [<directory>]` |
| `plugins/meow-python/skills/python/SKILL.md`     | The skill                                                             |
| `plugins/meow-python/skills/python/reviewing.md` | What a reviewer of Python needs beyond the commands                   |
| `plugins/meow-python/README.md`                  | The unit's page                                                       |
| `.meowpaw/profile.toml`, `[stages]`              | What `check` reads                                                    |

The program is the `python` feature of `crates/meow`. `status`, `bind` and
`check` read the files git tracks and run git alone, as SPC-1190 states, so
none of them starts Python, an environment tool or a tool it names. The pack
reads no settings table of its own, so the profile holds no `[python]` table.

The pack is current as of Ruff 0.17.0, mypy 2.4.0, pyright 1.1.414, pyrefly
1.3.2, ty 0.0.86, pytest 9.1.1, uv 0.13.0, Poetry 2.5.1 and PDM 2.29.2, and
its README names them (REQ-0085, RES-0363).

## Behaviour

### Detection

Each `pyproject.toml` git tracks marks its directory as a project, and the
pack reports for each such directory (REQ-2336, REQ-0133, REQ-3048, RES-0103).
A tool's configuration counts for a project where it sits in the project's
directory, because the tools the pack binds read theirs from the directory
they run in or above it. A `setup.py`, `setup.cfg` or `requirements.txt`
without a `pyproject.toml` beside it is named by `status` as a marker of an
older layout and makes no project (RES-0103).

### The environment

Each project runs its tools through one environment tool, read from what the
repository commits and never from what is installed (REQ-2426, RES-0103):

| Tool     | Declared by                                                                            |
| -------- | -------------------------------------------------------------------------------------- |
| `uv`     | A `uv.lock` in the project's directory, or a `[tool.uv]` table in its `pyproject.toml` |
| `poetry` | A `poetry.lock` in the project's directory, or a `[tool.poetry]` table                 |
| `pdm`    | A `pdm.lock` in the project's directory, or a `[tool.pdm]` table                       |

A tool runs through the environment tool as `uv run <tool>`, `poetry run
<tool>` or `pdm run <tool>` (RES-0363). A project that declares none of them
has no environment tool, and `bind` then prints every stage that binds a tool
with the comment `no environment declared: the interpreter that runs <tool> is
whatever the shell finds`, because a result attributable to no interpreter
can't be told from another machine's (RES-0103). A project that declares two
or more leaves the environment unresolved, and `bind` prints every stage
unresolved with `<file> and <file> both declare an environment`.

### What `status` reports

Its first line is `meow-python status`, followed by the profile's state as
SPC-1080 states. Then, for each project, in the order of its directory:

1. `scope: <directory>`, or `scope: <part> <directory>` where a declared part
   holds it (REQ-3048).
2. `marker: <path>`, naming its `pyproject.toml`, and `older layout: <file>`
   for each `setup.py`, `setup.cfg` or `requirements.txt` in the directory.
3. `environment: <tool>, declared by <file>`, or `environment: none declared`,
   or `environment: unresolved, <reason>`.
4. `pinned: python <version> in .python-version` where the file is tracked.
   `status` compares it with no installed interpreter, because it runs none
   (RES-0103).
5. `configured: <file>: <tool>` for each configuration it recognises: Ruff
   (`.ruff.toml`, `ruff.toml`, `[tool.ruff]`), mypy (`mypy.ini`, `.mypy.ini`,
   `[tool.mypy]`, a `[mypy]` section of `setup.cfg`), pyright
   (`pyrightconfig.json`, `[tool.pyright]`), pyrefly (`pyrefly.toml`,
   `[tool.pyrefly]`), ty (`ty.toml`, `[tool.ty]`), pytest (`pytest.toml`,
   `.pytest.toml`, `pytest.ini`, `.pytest.ini`, `[tool.pytest]`,
   `[tool.pytest.ini_options]`, a `[pytest]` section of `tox.ini`, a
   `[tool:pytest]` section of `setup.cfg`), `noxfile.py` and `tox.ini`.

With no `pyproject.toml` tracked, `status` prints `unresolved: not a Python
repository` and exits 3.

### What `bind` prints

`bind [<directory>]` binds the project in `<directory>`, the root where none
is given. Each stage takes the first row that applies, and each tool's command
runs through the environment tool (REQ-2336, REQ-2420, REQ-2426, RES-0363):

| Stage    | Printed as                                                       | When                                                       |
| -------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| `format` | `ruff format --check --cache-dir "${TMPDIR:-/tmp}/ruff-cache" .` | A Ruff configuration                                       |
| `lint`   | `ruff check --cache-dir "${TMPDIR:-/tmp}/ruff-cache" .`          | A Ruff configuration                                       |
| `check`  | `mypy --cache-dir=/dev/null`                                     | A mypy configuration                                       |
| `check`  | `pyright`                                                        | A pyright configuration                                    |
| `check`  | `pyrefly check`                                                  | A pyrefly configuration                                    |
| `check`  | `ty check`                                                       | A ty configuration                                         |
| `test`   | `python -B -m pytest -p no:cacheprovider`                        | A pytest configuration                                     |
| `build`  | `# build: unbound, ...`                                          | Always, naming the build backend `pyproject.toml` declares |
| any      | `# <stage>: unbound, looked for <files>`                         | No row above applies                                       |

Where two type checkers
are configured, the first in this table binds and a comment names the other,
so the choice is visible and `bind` never picks between them (REQ-2420,
RES-0103). A project with none configured gets `# check: unbound, looked for
mypy.ini, .mypy.ini, pyrightconfig.json, pyrefly.toml, ty.toml and the tool
tables of pyproject.toml`, which is an outcome and not a failure (RES-0103).
The pack turns on no Ruff rule group: it binds `ruff check` with no `--select`
word, so the rules are the ones the repository's configuration names
(REQ-2434). A comment under `lint` says a default configuration leaves the
security rules off. Ruff's `--fix` and `--unsafe-fixes` never appear in a
binding.

Ruff's cache defaults to `.ruff_cache` at the project root, so the binding
points `--cache-dir` at `${TMPDIR:-/tmp}/ruff-cache`, outside the tree, and
mypy writes no cache under `--cache-dir=/dev/null`, the documented form for a
Unix system (REQ-2442, RES-0363). The pytest binding stops the cache plugin
and the interpreter's bytecode from writing into the tree for the same reason.
The binding is the same where the repository's tracked ignore files cover the
caches, because it must not depend on a file the checkout may lack.

Where pytest is configured and the `addopts` of the configuration that applies
holds neither `--doctest-modules` nor `--doctest-glob`, a comment under `test`
says the stage doesn't run the examples in the project's documentation and
names the option that runs them; where it holds one, the stage runs them, and
`bind` prints no comment (REQ-2412, RES-0363). `check` reports no finding for
this, because a project without doctests is not at fault and the pack reads no
source file to tell.

Where the environment is `uv`, a comment under the table says `uv run` brings
the project environment up to date before it runs, so a stage may write into
`.venv`, which a repository ignores (RES-0103). A `mise.toml`, `.mise.toml`,
`Taskfile.yml` or `Taskfile.yaml` at the root is named with the runner's pack.
A stage the profile already declares is left out, and `bind` exits 0 once it
prints the table.

### What `check` finds

`check [<directory>]` reads the stages of the profile that governs the project
in `<directory>`, the root where none is given, and exits 1 on any finding,
each on a line of its own:

| Finding                                                                        | When                                                                                                                                    |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `<stage> runs <tool> outside <environment>: write <prefix> <tool>`             | A stage's command runs Ruff, mypy, pyright, pyrefly, ty or pytest by its bare name (REQ-2426)                                           |
| `<file> and <file> both declare an environment`                                | Two environment tools apply to the project (REQ-2426)                                                                                   |
| `ruff would apply unsafe fixes: remove --unsafe-fixes`                         | A stage runs Ruff with `--unsafe-fixes` (REQ-2434, RES-0103)                                                                            |
| `ruff applies fixes in a check: remove --fix`                                  | The `format` or `lint` stage runs Ruff with `--fix` (REQ-2442, RES-0103)                                                                |
| `ruff format rewrites the tree: pass --check`                                  | The `format` stage runs `ruff format` with neither `--check` nor `--diff` (REQ-2442)                                                    |
| `<tool> writes <cache> into the tree: pass <flag>`                             | A stage runs Ruff, mypy or pytest with no flag that moves or stops its cache, and no tracked ignore file covers it (REQ-2442, RES-0363) |
| `<loser> configures <tool> and <winner> does too: <tool> reads <winner> alone` | Two files of one tool configure it, and the tool reads one alone (REQ-2434, RES-0363)                                                   |

A command runs a tool where a word at the start of the command, or after
`&&`, `||`, `;` or `|`, is the tool's name, or where the word after a
`python -m` is. A word after `uv run`, `poetry run` or `pdm run` runs that
tool through the environment. A command that runs a tool through a runner's
task isn't read. With no finding, `check` prints `no findings; rule groups
enabled: the environment, the fixes, the caches, the configuration files` and exits 0
(REQ-2432). Ruff's own rule groups aren't named, because `check` runs no Ruff;
the clean report says what `check` covered and no more.

### Generated files

The README's `Generated files` section names `uv.lock`, `poetry.lock` and
`pdm.lock` as project state to commit, written by the tool and edited by hand
by nobody, and `.venv/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`,
`__pycache__/` and `*.egg-info/` as cache to ignore (REQ-2450, RES-0103).

### What the skill carries

The skill's body gives, in order: detection and what an older marker means,
the environment rule, stage resolution with `check` taken from configuration
and never guessed, what to read before reporting a pass, and the prohibitions
(RES-0103). It forbids passing `--unsafe-fixes`, guessing a type checker,
running `pip-audit --fix` in a verification step, editing a lockfile by hand,
and reporting a default `ruff check` as a security pass. It names the versions
the pack is current as of.

`reviewing.md` carries what a reviewer of Python checks that no command
reports (REQ-0083, RES-0103): whether the typing is checked or decorative,
import-time side effects, mutable default arguments, fixture scope and test
order, whether the package imports from a clean environment, and which
interpreter versions it claims.

## Failure paths

Each is printed as SPC-1190 states, by every command it applies to:

| State                                           | Reported as                                                         | Exit |
| ----------------------------------------------- | ------------------------------------------------------------------- | ---- |
| No tracked `pyproject.toml`                     | `unresolved: not a Python repository`                               | 3    |
| `<directory>` holds no tracked `pyproject.toml` | `unresolved: <directory> holds no pyproject.toml; one is in <dirs>` | 3    |
| `bind`: the profile doesn't parse               | `unresolved: the profile doesn't parse: <message>`                  | 3    |
| `check`: no profile, or one that doesn't parse  | `unresolved: <what is wrong with the profile>`                      | 3    |
| A `pyproject.toml` that doesn't parse           | `unresolved: <file> doesn't parse as TOML: <message>`               | 3    |
| An unknown argument                             | the usage line                                                      | 2    |

## Questions

Answer each question from what this document states, or leave `unanswered`,
because a gap left visible is one a reader can act on, and a gap left out
reads as covered.

### What the part is for

Detects Python, binds its stages and checks its configuration, naming the environment each project runs its tools through.

### What it depends on

`meow-python` lists `meow-core` in its `requires.toml`.

### What depends on it

No unit lists `meow-python` in its `requires.toml`.

### Where its data lives

It holds none of its own: it reads the files git tracks and the profile, and SPC-1190 states that a pack's program writes no file.

### What crosses a trust boundary

unanswered

### How it fails

Stated under "Failure paths" in this document.

### How it is deployed

`meow-python` installs as a plugin from the marketplace, `plugins/meow-python/`, and ships as the Pi package `packages/meow-python/`.
