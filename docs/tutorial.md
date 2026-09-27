---
reader: someone new to meowpaw, on macOS or Linux, who wants to see what it does before using it on real work
answers: how to get from an empty repository to a first check that Claude Code runs and reports honestly
kind: tutorial
describes: [meow-verbs@0.7.0]
---

# Your first verified change

In this tutorial you install one unit of `meowpaw`, `meow-verbs`, into a new
repository, declare the one check that repository has, and watch Claude Code
run it and report the checks you never declared as unresolved. It takes about
ten minutes. You need macOS or Linux, Claude Code installed and signed in,
`git` and a POSIX shell.

## 1. Make a repository with one check

Create an empty repository with a script that stands in for your test suite:

```bash
mkdir demo && cd demo
git init
mkdir scripts
printf '#!/bin/sh\necho "1 check passed"\n' > scripts/test
chmod +x scripts/test
./scripts/test
```

The last command prints `1 check passed`. The script exits 0, which is all a
check has to do for this tutorial.

## 2. Install the unit

Add the marketplace and install `meow-verbs` from it:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-verbs@meowpaw
```

The second command reports `meow-verbs` as installed. `meow-verbs` ships its
own program for macOS, Linux and Windows on arm64 and x86_64, so you install
nothing else.

## 3. Declare the check

Tell `meow-verbs` how this repository runs its tests. Create
`.meowpaw/profile.toml` with one line under `[verbs]`:

```bash
mkdir .meowpaw
printf '[verbs]\ntest = "./scripts/test"\n' > .meowpaw/profile.toml
cat .meowpaw/profile.toml
```

The last command prints the two lines you wrote. You declared `test` and
nothing else, so you can see how `meow-verbs` reports a check that doesn't
exist.

## 4. Ask Claude Code to test

Start Claude Code in the repository and ask it to run the tests:

```bash
claude "run the tests"
```

Claude Code loads the `meow-verbs:verify` skill before it runs anything, and
shows you what each verb resolves to:

```text
format     unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
lint       unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
check      unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
test       resolved    ./scripts/test   (from .meowpaw/profile.toml)
build      unresolved  undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml
```

If Claude Code asks for permission to run the program, allow it. Then it runs
your script through `meow-verbs` and reports the result with the command, its
exit status and its output:

```text
== test: `./scripts/test`
passed, exit status 0 after 0.1s

-- whole output of test:
1 check passed
-- end of test

summary: test passed
```

## 5. Ask for a check you never declared

Quit that session, and start a new one asking for a check the repository
doesn't have:

```bash
claude "lint the repository"
```

Claude Code shows the same table of what each verb resolves to, then reports
`lint` as unresolved and runs nothing in its place:

```text
== lint: unresolved (undeclared: the profile doesn't name it; declare it under [verbs] in .meowpaw/profile.toml), not run

summary: lint unresolved
```

`meow-verbs` exists for this moment. An agent asked to lint a repository with
no linter can guess a command, and a guessed command that exits 0 reads as a
pass. Here the report says nothing ran, and the program exits 3, which no
caller can mistake for success.

## What to do next

To add another check, add a line under `[verbs]`. Each unit's own page,
listed in the [introduction](README.md), says what else you can install and
what it costs you.
