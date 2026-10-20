---
name: python
description: The stages a Python project binds, the environment it runs its tools through, and what a reviewer of its code checks. It MUST be loaded before binding a stage in, reporting the tools of, or reviewing code in a repository with a pyproject.toml. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a project configured through the pack's program, and you report
what it printed. The program binds each stage from the files the repository
commits and runs none of the tools it names, so its table is a proposal the
person accepts, never a result. A Python command means nothing until you know
which interpreter runs it, and four type checkers disagree about what an error
is, so you read the repository's choices and never make one.
</role>

<steps name="read the configuration">
1. Run `meow-python status` and show its output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report, for each `scope:` line, the environment tool, the pinned
   interpreter and the tool configurations it lists, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-python bind` for the root project,
   or `bind <directory>` for another, and show the table it prints, each
   comment included.
2. Give the table to the person to put in the profile file its first line
   names, and stop.
</steps>

<steps name="check the stages">
1. Run `meow-python check` and show each finding
   as it printed it.
2. Report a line starting `unresolved:` as unresolved, never as a pass, and
   stop.
</steps>

<steps name="review Python">
1. Run `meow-python status` for the environment
   and the configured tools.
2. Read `reviewing.md` before you review code, and hold the
   code to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the environment">
- M1. Run every tool through the declared environment tool (`uv run <tool>`,
  `poetry run <tool>` or `pdm run <tool>`), because the same `pytest` command
  passes in an activated virtual environment and fails in a shell that never
  activated one, and neither result is about the code.
- M2. Where no environment tool is declared, name the interpreter that ran in
  the report, because a result without one is not attributable.
- M3. Never edit a lockfile by hand, and add a dependency through the
  environment tool, because the tool that owns the lockfile desynchronises it
  from a fresh install when you edit `pyproject.toml` alone.
- M4. Treat a `setup.py`, `setup.cfg` or `requirements.txt` with no
  `pyproject.toml` as a finding about the repository, because it predates the
  convention and is no second way to configure the project.
</rules>

<rules name="the stages">
- M5. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M6. Resolve `check` from the project's configuration and never guess a
  type checker, because mypy, pyright, pyrefly and ty disagree about what an
  error is, and a guessed one attributes its own findings to the project. A
  stage printed unbound is an outcome and no failure.
- M7. Never pass `--unsafe-fixes` or `--fix` to Ruff in a verification
  stage, because Ruff itself declines to call an unsafe fix safe and a check
  that rewrites the tree can't be trusted about what it found.
- M8. Report a default `ruff check` as no security pass, because Ruff leaves
  its security rules off unless the configuration selects them.
- M9. Before you report a pass, read which rule groups the Ruff configuration
  selects, whether pytest's `addopts` runs doctests, and whether the run
  covered one interpreter or the set the package claims, because each changes
  what the word pass covers.
- M10. Write the profile only when the person asks, because the profile is the
  repository's declaration.
- M11. Name the versions the pack is current as of, Ruff 0.17.0, mypy 2.4.0,
  pyright 1.1.414, pyrefly 1.3.2, ty 0.0.86 and pytest 9.1.1 (RES-0363), and
  where the installed tool is newer, say an observation may be stale, because
  a tool that moved on can change what its output means.
</rules>

<rules name="what must never happen">
- M12. Never run `pip-audit --fix` in a verification step, because an upgrade
  is a dependency change and belongs in a reviewed commit.
- M13. Report a `pip-audit` finding as a vulnerable version's presence and
  never as its reachability, because the tool has no reachability analysis,
  and a blocking gate on presence needs a suppression mechanism or it gets
  switched off.
- M14. Record the result of every interpreter in a matrix run, because
  recording only the last one discards what the matrix was for.
</rules>
