---
id: RES-0121
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0006, RES-0005
---

# Task runners

## Summary

Three of the four runners answer in machine-readable form, and none of the
three formats carries a stability promise. Every one of the four can resolve a
task defined outside the repository, so what a runner reports is what this
machine resolves, and never what this repository declares. Two have a trust
boundary that defends against exactly what a harness does by design. Two others
skip a task and report success, so a skipped task is never cited as evidence.

Research for one supported class of tool. A project with a runner has usually
already decided what its verbs mean, so reading that decision beats asking the
project to repeat it in a profile.

One document per runner. This one holds what is true across all four. How
reliably each answers what it contains, what a green result from a runner is
evidence of, and the two properties that decide more than any feature
comparison.

## The documents

| Runner  | Document                                   |
| ------- | ------------------------------------------ |
| mise    | [RES-0122-mise.md](RES-0122-mise.md)       |
| go-task | [RES-0123-go-task.md](RES-0123-go-task.md) |
| just    | [RES-0124-just.md](RES-0124-just.md)       |
| make    | [RES-0125-make.md](RES-0125-make.md)       |

## The question

Verb resolution has two sources: detect the language and infer the command, or
read what the project declared. The second is better whenever it exists,
because it is the project's own answer, where detection guesses and sometimes
happens to be right.

So the question is how reliably a runner can be asked what it declares, and
what has to be true before the answer may be believed.

## Method

This document holds what is true across the four runner documents, each of
which carries its own sources and read date, and states nothing about a runner
that is not stated there.

We reached the cross-cutting findings by comparing the four after they were
written, and no separate reading produced them. That is why several - the
provenance problem, the trust boundary, skipped-as-passed - appear in more than
one document and are stated here once.

## Findings

### Three of the four answer in machine-readable form

| Runner  | Marker                                   | Enumerate with                   |
| ------- | ---------------------------------------- | -------------------------------- |
| mise    | `mise.toml` and its variants             | `mise tasks ls --json`           |
| go-task | `Taskfile.yml` and seven other spellings | `task --list-all --json`         |
| just    | `justfile`, `.justfile`, `Justfile`      | `just --dump --dump-format json` |
| make    | `Makefile`, `GNUmakefile`                | nothing reliable                 |

Where a structured answer exists, resolution is exact, and no heuristic is
needed, and that property beats every other one these tools have.

None of the three formats carries a stability promise, and one states outright
that its formatting has no backwards compatibility guarantee. So a requirement
makes the parsing defensive, and no taste is involved: read the fields needed,
report an unrecognised shape as unresolved, and do not break on somebody else's
patch release.

### A declared task list is not the same claim as a repository's declaration

Every one of the four can resolve a task defined outside the repository.

mise merges configuration from parent directories to the filesystem root and
from the user's home, and its `[tasks]` sections _replace_, where merging would
keep both, so a higher-precedence file can supersede a project's task silently.
Task walks up the directory tree, can be run against a global Taskfile, and can
include a Taskfile fetched over HTTP or Git. just's `set fallback` searches a
parent directory when a recipe is not found. make's `include` can pull in a
makefile that is generated on the spot.

So what a runner reports is what _this machine, in this directory_ resolves
to. That is a different and weaker claim than _what this repository declares_,
and it does not reproduce on someone else's machine. A pack that conflates the
two is reporting a local accident as a project property.

### Two of the four have a trust boundary, and the harness is on the outside of it

mise requires a configuration to be trusted before it will parse and execute
it, because a configuration may execute code or affect the environment; without
trust it prompts, skips, or fails with an untrusted-config error. Task prompts
on the first run of a remote Taskfile, exits with code 104 when declined,
stores a checksum and warns when a remote file's contents change.

Both mechanisms exist to defend against the situation a harness walks into by
design: reading a repository somebody else wrote. So the rule is the same for
both, and it is a prohibition that nobody weighs. **The harness does not grant
trust.** It reports the state and the command, and the person decides. Granting
it authorises third-party code to run in the user's environment, and doing that
to tidy a report removes the protection entirely.

An untrusted state is also reported _distinctly_ from an empty one. A project
with no tasks and a project whose configuration was not trusted produce the
same silence and mean opposite things.

### A green result from a runner is not always evidence that work happened

This is the finding that bears hardest on the method, because it attacks the
evidence, where the others attack resolution.

mise skips a task when `sources` are older than `outputs`. Task skips a task
whose `status` command exits zero, and chooses between checksum and timestamp
freshness through `method`. Both report success.

So a `test` verb bound to such a task can pass without running a test, and
evidence citing it cites a previous run. The pack reports _skipped as fresh_
distinctly from _passed_, and a skipped task is not offered as evidence.

just has no freshness model at all, which makes a green result from just
strictly stronger than the same result from the other two. It is a small point,
stated here because it runs against the usual ranking of these tools.

make is worse than either: `-k` continues after failures so an exit status
summarises several, and a target without `.PHONY` silently stops running when a
file of its name appears.

### Reading a make project can execute code, which we verified

make updates the makefiles it reads, and the manual states that `-n` and `-q`
do not prevent it. Verified locally: a makefile including a generated makefile
ran the generating recipe under `make -pRrq` and under `make -n`, printing to
standard error and creating a file.

So enumeration in make is an action that changes things, and no inspection, and
a pack that enumerates has potentially run the repository's code and changed
the working tree. That is the strongest form of a pattern the other three show
in milder ways. It is why the class-level rule prefers a static read for
detection, and treats full enumeration as something a person consented to.

### A task may not be callable the way a verb is called

mise tasks may declare `usage` arguments and a `confirm` prompt. just recipes
take parameters and may carry `[confirm]`, `[private]` or a platform gate. Task
tasks may declare `requires` for variables and `ignore_error` for failures they
swallow.

Three rules generalise:

- **A task with required arguments is not invoked bare**, and the arguments are
  read from the enumeration, which discovering them by failure would not do. -
  **A task that asks for confirmation is not run unattended**, because its
  author asked for a person. - **A task marked private is not bound to a
  verb**, since that uses an implementation detail as an interface.

### Each runner carries something beyond its task list

mise carries tool versions and environment variables, installs a missing tool
before running a task, and records resolved versions in `mise.lock`. That makes
a mise pack the one that also answers _which toolchain does this project pin_ -
the question every language pack answers by detection, answered here by
declaration.

Task carries preconditions, platform restrictions, required variables and a
secret-masking flag whose documentation says it is not a substitute for secret
management.

just carries attributes and settings, including `dotenv-load`, which puts a
`.env` file's contents into the recipe's environment.

make carries nothing, which is why it is the hard one.

### A package manager's scripts are not a runner

`package.json`'s `scripts` and `cargo` aliases look like task lists and are
not. They belong to the language pack that already reads that file, because the
file belongs to the language and to no runner. Splitting it across two packs
means two things parse one file and disagree.

## Conclusions

1. A declared task beats a detected command. Where a runner declares what a
   verb means, that declaration resolves the verb and the language pack's
   inference is not consulted. 2. A runner is enumerated through its
   machine-readable output where it has one: `mise tasks ls --json`, `task
--list-all --json`, `just --dump --dump-format json`. 3. The enumeration
   format is parsed defensively and an unrecognised shape is reported as
   unresolved, because none of these formats carries a stability promise and
   one disclaims it. 4. A resolved task list is reported as resolved, and never
   as declared, since every runner can resolve a task defined outside the
   repository. 5. A task defined outside the repository is named as such,
   because a verb bound to it does not reproduce for anyone else. 6. The
   harness never grants trust - neither `mise trust` nor a remote Taskfile
   prompt - because that authorises third-party code to run in the user's
   environment. 7. An untrusted configuration is reported distinctly from an
   empty one, since the two look identical and mean opposite things. 8. A task
   skipped as fresh or as up to date is reported as skipped, never as passed,
   and is not cited as evidence. 9. Enumeration in make is treated as an
   action, because make updates the makefiles it reads and neither dry run nor
   question mode prevents it, which is documented and was verified. 10. A task
   with required arguments is invoked with them, read from the enumeration, and
   discovered by no failure. 11. A task that asks for confirmation is not run
   unattended, and a task marked private is not bound to a verb. 12. A mise
   pack reports the pinned toolchain to the harness, which the language packs
   otherwise have to detect. 13. make resolves only to an exactly named phony
   target, and reports unresolved otherwise, because enumerating make targets
   is an approximation and a near-miss name is the likeliest wrong answer. 14.
   A package manager's scripts belong to the language pack, and to no runner
   pack, so one file has one reader.

## Sources

All read 2026-09-20.

- The four runner documents listed above, each carrying its own sources and
  read date. This document states nothing about a runner that is not stated
  there.
