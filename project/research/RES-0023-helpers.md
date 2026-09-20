---
id: RES-0023
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Helpers: computing what a model would otherwise read

## Summary

A harness spends context on its own instructions and on the material the model
reads, and an executable helper can remove most of the second. The contract
that keeps helpers honest is narrow: a helper computes something mechanical and
never decides, its output is evidence and carries no authority, and its absence
is reported while the model falls back to reading. That last clause is what
makes a helper an optimisation that nothing depends on.

Research for the executable parts of a plugin. A harness spends context on two
things - its own instructions, and the material the model reads to answer a
question. The three tiers address the first. This addresses the second, and it
is the larger of the two.

## Method

The platform's plugin reference was fetched and read on 2026-09-20 for what a
shipped executable actually gets: the path it is placed on, how its
dependencies are installed, and the variable that locates its root.

Nothing was built or run. No helper was written and measured, so the claim that
computing beats reading is an argument from what the platform charges rather
than a measurement of a helper against its absence.

## The lever

A model asked "is every requirement covered by a check" can read the
requirements document and every test file, or it can run something that prints
twelve lines. The answer is identical and the cost differs by two orders of
magnitude.

Anything **mechanical** is in this category: set differences, coverage,
staleness, resolution, counting, matching identifiers, comparing two lists. None
of it needs judgement, and all of it is expensive to do by reading.

The only surveyed harness that says this out loud is
`claude-code-spec-workflow`, whose context commands - `get-steering-context`,
`get-spec-context`, `get-template-context` - exist to load once and distribute,
and which claims **60-80% fewer tokens** than loading the individual files. The
mechanism is unremarkable; that nobody else does it is the finding.

The memory research reaches the same place from another direction: the three-tier
retrieval pattern - index result, surrounding context, full document - is
reported at roughly a 10x saving against injecting whole documents
([RES-0026-memory.md](RES-0026-memory.md)).

## What the platform provides

From [RES-0004-platform.md](RES-0004-platform.md):

- **`bin/`** - executables placed on the Bash tool's `PATH` when the plugin is
  installed. - **Node dependency installation** - marketplace plugins have
  their dependencies installed from a lockfile: frozen resolution, no lifecycle
  scripts, a sixty-second timeout. - **Shell injection** - `` !`command` ``
  runs before the model sees the prompt and injects the output, so a command
  can _arrive_ with its answer and spend no turns computing it. -
  **`${CLAUDE_PLUGIN_ROOT}`** - how a helper is addressed.

Together these mean a helper is not "another thing to install". It ships with
the plugin, installs with it, and is addressable from a command's frontmatter.

## What belongs in a helper, and what does not

| Belongs                                                        | Does not                                    |
| -------------------------------------------------------------- | ------------------------------------------- |
| Verb resolution: which command runs for `test` here            | Deciding whether the result is acceptable   |
| Coverage: which identifiers are specified, referenced, neither | Judging whether a check would actually fail |
| Staleness: which evidence predates the current revision        | Deciding what to do about it                |
| Status rendering: the state files as a table                   | Deciding which gate matters                 |
| Plan extraction: tasks, marks, dependencies, what is ready     | Choosing the next task                      |
| Diff scoping: which files changed, in which scope              | Reviewing them                              |
| Index and link integrity                                       | Writing the missing entry                   |

The line is **determination against judgement**. A helper computes facts; the
model decides what they mean. A helper that starts deciding is a program
enforcing policy in a place nobody reviews policy.

## The constraint that keeps this honest

A helper may make work **cheaper**, never **possible**. This is the optionality rule's
rule for tool packs, applied one level in: the method has to complete when a
helper is absent or broken, by the model doing the reading instead.

Without that, the no-service rule erodes one convenience at a time, and the harness
becomes a program to install, upgrade and debug - which is the alternative the
design already rejected.

Two consequences:

- A helper's absence is **reported**, and nothing silently works around it.
  Same rule as the unresolved verb and the missing index. - A helper's output
  is **data the model checks**, and no instruction it obeys. A helper that
  prints "all requirements covered" is making a claim, and the claim is
  evidence in exactly the sense the method means: a command, its output and a
  revision.

## Which language

TypeScript, for the parts that ship inside a plugin. Three reasons, and none is
taste:

- The platform installs Node dependencies for marketplace plugins from a
  lockfile, so there is a supported installation path and no other language has
  one. - Types are the cheapest available guard on a helper whose output the
  model will trust; a helper that prints a malformed record is worse than one
  that fails. - `meow-typescript` exists, so the same five verbs cover the
  helper code as they cover anything else, and it is no unchecked corner.

This repository's own checks are a separate case and stay in Python. They run
in CI, where the standard library is free and a Node install is pure cost, and
they are not shipped to anyone. The two have different constraints and
therefore different answers - recording this so the inconsistency reads as a
decision somebody took.

## The failure mode

A helper that is _almost_ right is worse than none, because its output is
trusted without being read. The defences:

- Helpers are small and single-purpose - one determination each. - Output is
  structured and stable, so a change to it is a change to a contract. - A
  helper is covered by the same gate as everything else. - Where a helper's
  answer contradicts what the model can see, the model says so and defers to
  nothing. A confident wrong number is the harness's own characteristic
  failure, wearing a new costume.

## Conclusions

1. Compute anything mechanical; read only what needs judgement. 2. A helper may
   make work cheaper, never possible. Its absence is reported and the model
   falls back to reading. 3. A helper determines; it never decides. 4. Its
   output is evidence - a command, an output, a revision - and a reader can
   check it, because it carries no authority. 5. Shipped helpers are
   TypeScript, covered by the same verbs as any other code. 6. One
   determination per helper, with a stable structured output.

## Sources

- [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference),
  read 2026-09-20 - `bin/` on the Bash `PATH`, Node dependency installation from
  a lockfile with frozen resolution and no lifecycle scripts, and
  `${CLAUDE_PLUGIN_ROOT}`.
- [Slash commands](https://code.claude.com/docs/en/slash-commands), read
  2026-09-20 - shell injection with `` !`command` ``, its abort-on-non-zero
  behaviour, and `allowed-tools`.
- [Pimzino/claude-code-spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow)
  README, read 2026-09-20 - the context commands and their claimed 60-80% token
  reduction against loading files individually.
- [Specbound/sdd-harness](https://github.com/Specbound/sdd-harness) README, read
  2026-09-20 - the output-compressing proxy reported at 60-90% reduction on
  development commands, and the shell-command rewriter.
- [Context engineering AI](https://mem0.ai/blog/context-engineering-ai-agents-guide),
  read 2026-09-20 - the three-tier retrieval pattern and its ~10x saving.
