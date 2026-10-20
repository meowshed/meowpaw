---
reader: someone installing or running meow-python on Pi
answers: what meow-python provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-python@0.1.0]
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

## Generated files

Commit the lockfile your environment tool writes (`uv.lock`, `poetry.lock` or
`pdm.lock`), because it is the resolved dependency set every collaborator and
every CI run installs from, and edit it through the tool and never by hand.
Ignore `.venv/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`,
`__pycache__/` and `*.egg-info/`, because the next run regenerates each.
