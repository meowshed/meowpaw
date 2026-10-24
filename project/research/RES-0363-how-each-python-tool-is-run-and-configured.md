---
id: RES-0363
artifact: research
status: approved
revised: 2026-10-13
elaborates: RES-0103
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# How each Python tool is run and configured

## Summary

`uv run`, `poetry run` and `pdm run` each run a command in the project's
environment. Ruff reads `.ruff.toml` over `ruff.toml` over `pyproject.toml`,
`ruff format --check` exits 1 on a file it would reformat and writes none, and
Ruff keeps its cache in `.ruff_cache` at the project root unless
`--cache-dir` points elsewhere, since `--no-cache` disables reads alone. mypy
reads `mypy.ini`, `.mypy.ini`, `[tool.mypy]` or a `[mypy]` section of
`setup.cfg`, writes `.mypy_cache` in the current directory, and writes none
under `--cache-dir=/dev/null`. pyright, pyrefly and ty each have a file and a
`pyproject.toml` table of their own. pytest reads the first of seven files
that configures it, collects doctests under `--doctest-modules`, which a
project makes permanent in `addopts`, and stops writing `.pytest_cache` under
`-p no:cacheprovider`. `python -B` writes no `.pyc` file. This adds to
RES-0103 the command lines and file names a pack binds; it leaves out the
matrix runners, coverage and the supply-chain check.

## The question

RES-0103 names `uv run` as the environment rule, Ruff for format and lint,
four type checkers and pytest, but not the words that run each, nor the files
each reads, nor what each writes into the working tree. A pack that binds a
stage prints those words and keeps the tree clean, so each fact has to come
from the tool's own documentation.

## Method

I read each tool's own documentation on 2026-10-13, as listed under Sources,
and the current version of each from PyPI the same day. I ran none of the
tools. Pyright's own page on its command line states no default for a run
with no files, beyond that the files on the command line override the ones its
configuration names.

## Findings

### Three environment tools run a command in the project's environment

RES-0103 records that `uv run` brings the project environment up to date
before it runs the command. Poetry's `run` "executes the given command inside
the project's virtualenv", and `pdm run` runs a command that is no defined
script "in the environment that is aware of packages in your project
environment".

### Ruff's files, its check and its cache

In one directory "the `.ruff.toml` file will take precedence over the
`ruff.toml` file", and "the `ruff.toml` file will take precedence over the
`pyproject.toml` file", where Ruff reads the `[tool.ruff]` table. `ruff format
--check` "will avoid writing any formatted files back" and exits 1 where "one
or more files would be formatted". "By default, Ruff stores cache results in a
`.ruff_cache` directory in the current project root", `--cache-dir` names
another, and `--no-cache` is documented as "Disable cache reads".

### mypy's files, and the flag that keeps its cache out of the tree

mypy searches each directory upwards for `mypy.ini`, `.mypy.ini`, a
`pyproject.toml` with a `[tool.mypy]` section and a `setup.cfg` with a
`[mypy]` section, and merges none of them. With no file on the command line it
checks what its `files` option lists. "By default, mypy stores all cache data
inside of a folder named .mypy_cache in the current directory", it writes the
cache "even when incremental mode is disabled", and "To disable writing to the
cache, use --cache-dir=/dev/null (UNIX) or --cache-dir=nul (Windows)."

### pyright, pyrefly and ty each read their own file

pyright's usage is `pyright [options] [files...]`, and files named on the
command line override those `pyrightconfig.json` or `pyproject.toml` names. It
exits 0 with no errors, 1 with errors, 2 on a fatal error, 3 where its
configuration "could not be read or parsed" and 4 on an illegal parameter.
pyrefly checks a project with `pyrefly check`, configured in `pyrefly.toml` or
`[tool.pyrefly]`. ty checks with `ty check`, "all Python files in the working
directory or project by default", and reads `ty.toml` or `[tool.ty]`, where
"`ty.toml` files take precedence over `pyproject.toml` files".

### pytest reads the first file that configures it

pytest reads `pytest.toml`, `.pytest.toml`, `pytest.ini`, `.pytest.ini`, a
`pyproject.toml` with a `[tool.pytest]` or `[tool.pytest.ini_options]` table,
a `tox.ini` with a `[pytest]` section and a `setup.cfg` with a `[tool:pytest]`
section, in that order, and "the first match wins". `pytest.toml` takes
precedence "even when empty".

### pytest runs doctests where the project asks it to

pytest runs the examples in docstrings under `--doctest-modules`, and a project
makes the option permanent in its configuration, as `addopts =
["--doctest-modules"]` in the documentation's own example.

### pytest and Python write into the tree unless told not to

pytest's cache plugin "is enabled by default, but can be disabled if needed",
and its documented example writes `.pytest_cache` under the project root.
`pytest -p no:NAME` prevents the plugin named `NAME` from loading, and the
cache plugin's name is `cacheprovider`. Under `-B`, "Python won't try to write
`.pyc` files on the import of source modules".

### The versions current on 2026-10-13

PyPI gives Ruff 0.17.0, mypy 2.4.0, pyright 1.1.414, pyrefly 1.3.2, ty 0.0.86,
pytest 9.1.1, uv 0.13.0, Poetry 2.5.1 and PDM 2.29.2.

## Conclusions

1. A tool runs through the declared environment as `uv run <tool>`, `poetry
run <tool>` or `pdm run <tool>`, because each documents running a command
   in the project's environment.
2. Ruff counts as configured by `.ruff.toml`, `ruff.toml` or `[tool.ruff]`, and
   `format` binds `ruff format --check`, which writes nothing.
3. A Ruff stage names a cache directory outside the tree with `--cache-dir`,
   because `--no-cache` disables reads alone and the default cache sits at the
   project root.
4. mypy counts as configured by any of its four files, and its stage passes
   `--cache-dir=/dev/null`, the documented way to write no cache on a Unix
   system, and names a path only where the `files` option is unset.
5. pyright counts as configured by `pyrightconfig.json` or `[tool.pyright]`,
   pyrefly by `pyrefly.toml` or `[tool.pyrefly]`, and ty by `ty.toml` or
   `[tool.ty]`, each run with no file named.
6. pytest counts as configured by any of its seven files, and the project runs
   doctests where that file's `addopts` holds `--doctest-modules` or
   `--doctest-glob`.
7. `test` runs pytest as `python -B -m pytest -p no:cacheprovider`, because
   both its cache and the interpreter's bytecode would otherwise land in the
   tree.
8. A pack's page names the versions above as the ones it is current as of.

## Sources

- [Poetry commands](https://python-poetry.org/docs/cli/), read 2026-10-13 -
  `poetry run` in the project's virtualenv.
- [PDM scripts](https://pdm-project.org/latest/usage/scripts/), read
  2026-10-13 - `pdm run` of a command that is no script.
- [Configuring Ruff](https://docs.astral.sh/ruff/configuration/), read
  2026-10-13 - the configuration files' precedence and the `--no-cache` and
  `--cache-dir` help.
- [Ruff settings](https://docs.astral.sh/ruff/settings/), read 2026-10-13 -
  the `.ruff_cache` default and `RUFF_CACHE_DIR`.
- [The Ruff formatter](https://docs.astral.sh/ruff/formatter/), read
  2026-10-13 - `ruff format --check` and its exit statuses.
- [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html),
  read 2026-10-13 - the four files, their order and the `files` option.
- [mypy command line](https://mypy.readthedocs.io/en/stable/command_line.html),
  read 2026-10-13 - `--cache-dir` and disabling cache writes.
- [pyright command line](https://raw.githubusercontent.com/microsoft/pyright/main/docs/command-line.md),
  read 2026-10-13 - the usage line, the override and the exit statuses.
- [Installing pyrefly](https://pyrefly.org/en/docs/installation/), read
  2026-10-13 - `pyrefly check` and its two configuration places.
- [ty](https://docs.astral.sh/ty/) and
  [ty configuration](https://docs.astral.sh/ty/configuration/), read
  2026-10-13 - `ty check` and its configuration files.
- [pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html),
  read 2026-10-13 - the seven files in order.
- [pytest doctests](https://docs.pytest.org/en/stable/how-to/doctest.html),
  read 2026-10-13 - `--doctest-modules` and `addopts`.
- [pytest cache](https://docs.pytest.org/en/stable/how-to/cache.html) and
  [pytest plugins](https://docs.pytest.org/en/stable/how-to/plugins.html), read
  2026-10-13 - the `cacheprovider` plugin and `-p no:NAME`.
- [Python command line](https://docs.python.org/3/using/cmdline.html), read
  2026-10-13 - `-B`.
- [PyPI](https://pypi.org/), read 2026-10-13 - the latest version of each
  package named above.
