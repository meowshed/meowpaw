---
id: RES-0103
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Python

## Summary

Four of the five verbs now have an obvious answer. The fifth has four credible
ones that disagree about what an error is, so a guessed type checker attributes
its findings to the project. Underneath all five sits a question no other
language here has: which interpreter is running. The linter absorbed a security
scanner but leaves those rules off by default, and it classifies its own fixes
as safe or unsafe - a classification the harness does not overrule.

Research for one supported language. A toolchain is a set of tools, so this
covers which tools make up Python's and the one verb the ecosystem has not
converged on. It also covers how an environment decides what a command means,
what the pack authors, and what the skill has to contain.

It does not cover what every toolchain document shares, which is
[RES-0006-toolchains.md](RES-0006-toolchains.md), nor what a skill costs, which
is [RES-0005-skill-format.md](RES-0005-skill-format.md).

## The question

Four of the five verbs in Python now have an obvious answer, which was not true
three years ago. The fifth has four credible answers, two of them new and one
still in beta, and choosing wrongly produces a wall of findings that are not
defects.

Underneath all five sits a question no other language here has: which
interpreter is running, and whether the command being run is the project's or
the machine's.

## Method

The vendor documentation was fetched and read on 2026-09-20: the environment
tool's pages on running commands and on project layout, and the linter's own
page for its rule sources, default rule set and fix-safety model.

The comparison of the four type checkers came from an independent handbook and
from no vendor, because the vendors' speed claims disagree with it. We quote
the handbook's instruction to treat vendor claims as upper bounds in full.

Two searches were used to find current practice and the wider tool inventory,
and those results are marked as secondary. Nothing was installed or run.

## Findings

### The marker is `pyproject.toml`, and it is also where every tool is configured

`pyproject.toml` marks the project, declares the dependencies and the build
backend, and carries a `[tool.*]` table for each tool. The formatter, the
linter, the type checker, the test runner and the coverage settings all state
themselves in that one file.

`uv.lock` sits beside it. It is _"a universal lockfile that captures the exact
resolved package versions for your project across all Python environments"_,
cross-platform by design, which _"should be checked into version control"_ and
which nobody edits by hand. `.python-version` pins the interpreter. `.venv` is
the project environment, created by `uv run` or `uv sync`, and is not
committed.

The older markers - `setup.py`, `setup.cfg`, `requirements.txt` - still exist
in real repositories and mean the project predates the convention. They are a
finding about the repository rather than a second way to configure it.

### The environment is the hard part, and it is upstream of every verb

A Python command is meaningless without knowing which interpreter runs it. The
same `pytest` invocation passes in an activated virtual environment and fails
in a shell that never activated one, and neither result is about the code.

`uv` documents the guarantee that removes the question: _"When using `run`, uv
will ensure that the project environment is up-to-date before running the given
command."_ That makes `uv run <tool>` the invocation that depends on nothing
the shell did first.

The documentation does not spell out the locking-against-syncing sequence, so
the guarantee is the one quoted and nothing more. It is enough for the decision
at hand: prefer `uv run`, because the alternative is a verb whose result
depends on shell state nobody recorded.

### The toolchain, tool by tool

Nothing here ships with the interpreter, which is the structural difference
from Rust and Go. Every row is something a project installed.

| Role                   | Tool                                                 | What only it answers                                                                     |
| ---------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Environment, packaging | `uv`                                                 | Which interpreter, which versions, reproducibly                                          |
| Build backend          | `hatchling`, `setuptools`, `uv_build`, `poetry-core` | What the package becomes                                                                 |
| Format                 | `ruff format`                                        | The canonical form                                                                       |
| Lint                   | `ruff check`                                         | Pyflakes, pycodestyle, isort, pyupgrade, bandit and dozens of flake8 plugins in one pass |
| Typecheck              | `mypy`, `pyright`, `pyrefly`, `ty`                   | Whether the annotations are consistent - and they disagree                               |
| Test                   | `pytest`                                             | The tests, fixtures, parametrisation                                                     |
| Test, parallel         | `pytest-xdist`                                       | The same run across cores                                                                |
| Test, ordering         | `pytest-randomly`                                    | Whether the suite depends on test order                                                  |
| Property tests         | `hypothesis`                                         | Inputs nobody wrote down, shrunk to the smallest failure                                 |
| Coverage               | `coverage.py`, `pytest-cov`                          | Which lines and branches ran                                                             |
| Mutation               | `mutmut`, `cosmic-ray`                               | Whether the assertions would notice a change                                             |
| Matrix                 | `nox`, `tox`                                         | Whether it works on the other supported interpreters                                     |
| Vulnerabilities        | `pip-audit`                                          | Dependencies against the advisory databases                                              |
| Unused dependencies    | `deptry`                                             | Declared but unused, and used but undeclared                                             |
| Dead code              | `vulture`                                            | Definitions nothing references                                                           |
| Architecture           | `import-linter`, `tach`                              | Whether an import crossed a boundary the project forbids                                 |
| Hooks                  | `pre-commit`, `prek`                                 | The same checks before the commit exists                                                 |
| Docs                   | `mkdocs`, `sphinx`, `pdoc`                           | The published documentation                                                              |

Two rows deserve their placement rather than a mention. `import-linter` and
`tach` are the only tools in this document that check structure rather than
code, which makes them the Python answer to the architecture question, and
almost no project has one. And `nox` and `tox` answer the question the other
verbs cannot ask: a suite that passes on the developer's interpreter says
nothing about the versions the package claims to support.

### Formatting and linting converged, and the linter absorbed a security scanner

`ruff format` and `ruff check` cover both verbs, configured under `[tool.ruff]`
in the file that marks the project. Ruff describes itself as _"a drop-in
replacement for Flake8 (plus dozens of plugins), isort, pydocstyle, pyupgrade,
autoflake, and more"_. Its rule sources carry their original prefixes: `F` for
Pyflakes, `E` for pycodestyle, `S` for bandit's security rules.

Two properties decide how a pack uses it.

The default rule set is small. Correctness, suspicious, complexity,
performance and style are on; security, formatting, pedantic and restriction
are off. So a clean `ruff check` on a default configuration has not run the
security rules, and reporting it as a security pass would be wrong.

Fixes have a safety model. The two definitions are quoted as written:

> Safe fixes ... preserve runtime behavior and will only remove comments when
> deleting entire statements or expressions.
>
> Unsafe fixes ... could lead to a change in runtime behavior, the removal of
> comments, or both.

Only safe fixes apply by default, and unsafe ones need `--unsafe-fixes`.

That model is the one a pack must not override. A harness that passes
`--unsafe-fixes` to make a `fmt` verb quieter is applying changes the tool
itself declined to call safe, inside a step the reader believes is mechanical.

### The type checker has four candidates and no default

| Tool    | Written in | Configuration                          | State                                       |
| ------- | ---------- | -------------------------------------- | ------------------------------------------- |
| mypy    | Python     | `[tool.mypy]`, `mypy.ini`, `setup.cfg` | the longest-running, most widely referenced |
| pyright | TypeScript | `[tool.pyright]`, `pyrightconfig.json` | the incumbent with the editor integration   |
| pyrefly | Rust       | `[tool.pyrefly]`, `pyrefly.toml`       | 1.0.0 in May 2026                           |
| ty      | Rust       | `[tool.ty]`, `ty.toml`                 | beta, filling out typing-spec support       |

The speed claims are large and the honest form is a range. Independent
measurement puts ty at 9x faster than mypy on one codebase and 2x on another,
and pyrefly at 5 to 8 times across both. The same source says vendor claims
should be _"treated as plausible upper bounds rather than floors."_ The
two-orders-of-magnitude figures that circulate are vendor figures.

Speed is not what decides the pack's behaviour. The four disagree about what an
error is. The same code is clean under one and produces hundreds of findings
under another, because they implement different parts of the typing
specification to different depths and differ on inference in unannotated code.

So a pack that picks produces findings that are an artifact of the pick. Each
costs a reader time and none is a defect the project agreed to care about.

### An unresolved verb is a better report than a guessed one

Saying a verb is unresolved sounds like a failure and is not. It is a true
statement about the project - nothing here declares a type checker - and it is
actionable in a way that a wall of findings is not.

That generalises past Python, and this is where it is sharpest, because Python
is the language where guessing is most tempting and most expensive.

### Supply-chain checking has no reachability analysis, which changes the gate

`pip-audit` audits local environments, requirements files, dependency trees and
lockfiles, drawing on the Python Packaging Advisory Database through the PyPI
API by default and on OSV as an alternative. It emits columns, JSON, Markdown
and both CycloneDX forms, so it can produce a software bill of materials as
well as a finding list. It has a `--fix` mode that upgrades vulnerable
dependencies in place.

What it does not have is Go's reachability analysis. A finding means the
vulnerable version is present, not that the vulnerable function is reachable.
That is a materially noisier signal, and a pack that treats it as a blocking
gate without a suppression mechanism has built the check that gets disabled.

`--fix` deserves the same caution as any automatic remediation: an upgrade is a
dependency change, and a dependency change belongs in a reviewed commit rather
than inside a verification step.

### Evidence from a test run

`pytest --junitxml=<path>` produces the citable artifact; `pytest-cov` or
`coverage.py` produces the coverage report, and branch coverage is a setting
rather than a default. Running under `nox` or `tox` produces one result per
interpreter, and a harness that records only the last one has recorded the
least interesting.

### What the pack authors

`pyproject.toml` - dependencies, `[tool.ruff]`, the type checker's table, the
pytest and coverage configuration - and the lockfile through `uv` rather than
by hand, since the documentation is explicit that it is not edited manually.

Also `.python-version`, a `noxfile.py` or `tox.ini` for the matrix, and a
`.pre-commit-config.yaml` where the project uses hooks.

A pack that adds a dependency by editing `pyproject.toml` and not the lockfile
has left the project in a state where `uv run` and a fresh install disagree.

### What a reviewer needs that no command reports

Whether the typing is checked or decorative: annotations no configured checker
reads look like a typed codebase and are comments.

Import-time side effects, which make the order of imports part of the
program's meaning.

Mutable default arguments, the defect that survives every review that is
reading for something else.

Fixture scope in pytest, where a wrongly scoped fixture makes tests pass in one
order and fail in another - which is what `pytest-randomly` exists to surface
and almost nobody installs.

Whether the package imports from a clean environment, which is where packaging
defects live and where no test in the repository looks.

Which interpreter versions the package claims, and whether anything ran on
them.

### What the skill has to contain

In the body, in this order:

1. Detection. `pyproject.toml`, `uv.lock`, `.python-version`, and what an
   older marker means.
2. The environment rule, first among the verbs. Commands run through `uv
run` where `uv` is present; otherwise the report states which interpreter
   was used.
3. Verb resolution, with `typecheck` resolved from configuration and never
   guessed, and the unresolved report described as an outcome rather than a
   failure.
4. What to read before reporting a pass. Whether the security rules were
   enabled in ruff's configuration; whether coverage measured branches; whether
   the run covered one interpreter or the claimed set.
5. What must never happen. Passing `--unsafe-fixes`. Guessing a type
   checker. Running `pip-audit --fix` inside a verification step. Editing the
   lockfile by hand. Reporting a default `ruff check` as a security pass.

In supporting files: the tool inventory; templates for `pyproject.toml`
sections, a `noxfile.py`, a pre-commit configuration; the evidence recipe with
`--junitxml` and branch coverage; the reviewer's knowledge; and the dated facts

- the four type checkers and their maturity, ruff's default rule set, the
  measured speed ranges - with what to re-check.

## Conclusions

1. A Python project is marked by `pyproject.toml`, which also carries the
   configuration of every tool the verbs resolve to.
2. `uv.lock` is read as the project's resolved state and is never edited by
   hand, because the tool that owns it says so and a hand edit desynchronises
   it from `uv run`.
3. An older marker is reported rather than supported as an alternative. A
   project with `setup.py` and no `pyproject.toml` is a finding about the
   repository.
4. Commands run through `uv run` where `uv` is present, because the
   documented guarantee is that the environment is up to date, and the
   alternative depends on shell state nothing recorded.
5. Where `uv` is absent, the report names the interpreter that ran, since a
   result without it is not attributable.
6. `fmt` and `lint` resolve to `ruff`, and the pack does not offer a
   choice.
7. A default `ruff check` is not a security pass, because the security
   rules are off by default, and the pack reports which rule groups were
   enabled.
8. Unsafe fixes are never applied by the harness. The tool classifies them
   as changing runtime behaviour, and a mechanical step is not where that
   belongs.
9. `typecheck` is resolved from the project's configuration and never
   guessed, because the four candidates disagree about what is an error and a
   guessed checker attributes its own findings to the project.
10. A verb with no configured tool is reported as unresolved, which is a
    true and actionable statement rather than a failure.
11. The maturity of a candidate is part of the record, because a checker in
    beta and a checker at 1.0 are different risks to recommend.
12. A speed claim from a vendor is recorded as a vendor claim, with the
    independent range beside it.
13. `pip-audit` findings are reported without reachability, so the pack
    states that a finding means presence rather than reachability, and a
    blocking gate needs a suppression mechanism or it will be disabled.
14. `--fix` is not run inside a verification step, because an upgrade is a
    dependency change and belongs in a reviewed commit.
15. Test evidence is `--junitxml`, and coverage measures branches rather
    than lines alone, because line coverage is the weaker claim.
16. A matrix run records every interpreter's result, since recording only
    the last one discards what the matrix was for.
17. A dependency added by the pack updates the lockfile through `uv`, or
    the project is left in a state where a fresh install disagrees with the
    developer's environment.
18. Structural checking is named as available and usually absent.
    `import-linter` and `tach` are the Python answer to boundary enforcement,
    and a project without one has no mechanical architecture check.
19. The reviewer's knowledge is recorded with the pack: decorative typing,
    import-time side effects, mutable defaults, fixture scope and test-order
    dependence, the clean import, and the claimed interpreter versions.
20. The skill body carries detection, the environment rule, verb resolution,
    what to read before reporting a pass, and the prohibitions, in that
    order.

## Sources

All read 2026-09-20.

- [uv, running commands in projects](https://docs.astral.sh/uv/concepts/projects/run/)
  - the guarantee that `uv run` brings the project environment up to date
    before running the command, and the absence of any statement about the
    locking sequence.
- [uv, project structure and files](https://docs.astral.sh/uv/concepts/projects/layout/)
  - `uv.lock` as a cross-platform universal lockfile that should be checked
    into version control and is not edited by hand; `.venv` as the project
    environment created by `uv run` or `uv sync` and excluded from version
    control.
- [The ruff linter](https://docs.astral.sh/ruff/linter/) - ruff as a drop-in
  replacement for Flake8 and dozens of plugins, isort, pydocstyle, pyupgrade
  and autoflake; the rule-source prefixes; the default rule set of correctness,
  suspicious, complexity, performance and style with security, formatting,
  pedantic and restriction disabled; and the safe against unsafe fix model with
  its definitions and the `--unsafe-fixes` opt-in.
- [How do mypy, pyright and ty compare?](https://pydevtools.com/handbook/explanation/how-do-mypy-pyright-and-ty-compare/)
  - the four candidates with their implementation languages, configuration
    files and tables; ty in beta with its typing-spec coverage tracked publicly;
    pyrefly at 1.0.0 in May 2026; mypy as the longest-running; the measured 9x
    and 2x for ty and 5 to 8 times for pyrefly; and the instruction to treat
    vendor claims as plausible upper bounds rather than floors.
- [Does Ruff support type checking?](https://pydevtools.com/handbook/explanation/does-ruff-support-type-checking/)
  - that ruff covers formatting and linting and not type checking, so the fifth
    verb needs a separate tool whatever the project chooses.
- [pip-audit](https://github.com/pypa/pip-audit) - auditing local environments,
  requirements files, dependency trees and lockfiles; the Python Packaging
  Advisory Database through the PyPI API by default with OSV as an alternative;
  the five output formats including both CycloneDX forms; and the `--fix` mode
  that upgrades vulnerable dependencies.
- [mypy vs Pyright vs Pyrefly, choosing a Python type checker in 2026](https://codegym.cc/groups/posts/python-type-checkers-mypy-pyright-pyrefly)
  and [My entire Python development setup in 2026](https://medium.com/the-pythonworld/my-entire-python-development-setup-in-2026-every-tool-listed-4f41561e82e6)
  - the practical selection advice and the wider tool inventory including
    `deptry`, `vulture`, `nox` against `tox`, `pytest-randomly`, `hypothesis` and
    branch coverage. Recorded as secondary sources.
