---
id: RES-0058
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:init`

## Summary

Initialisation writes a profile and a constitution into a repository that has
neither, by reading what is already there. It reads before asking and asks only
what reading cannot answer, reports what it found inconsistent and picks
nothing, records the existing layout and imposes none, and writes nothing but
the two harness-owned files. It reports loudly which verbs do not resolve,
because that is the first thing the user will hit.

Writes a profile and a constitution into a repository that has neither, by
reading what is already there.

## Who has an equivalent

| Harness       | Command               | What it does                                                                                                                                                |
| ------------- | --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| spec-kit      | `specify init`        | A CLI, outside the agent: scaffolds `.specify/`, writes `init-options.json` including the numbering scheme, installs command templates for the chosen agent |
| cc-sdd        | `kiro-spec-init`      | Creates the spec directory and `brief.md` for one feature - an init per unit of work, not per repository                                                    |
| spec-workflow | `spec-steering-setup` | Writes `product.md`, `tech.md`, `structure.md` by reading the codebase                                                                                      |
| agent-os      | "discover standards"  | Extracts conventions **from the existing codebase**, asking nobody                                                                                          |

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## The design question

Two opposed answers exist in the survey.

Declare. spec-kit asks and writes what it is told. Predictable, and wrong by
default in a repository that already has conventions.

Discover. agent-os reads the codebase and writes down what it finds.
spec-workflow does the same for its steering documents. This is right far more
often, and it is the only approach compatible with the rule that a repository's
own conventions beat the harness's defaults.

Discovery has one failure mode: it records the _current_ state as if it were a
decision. A codebase with three different error-handling styles does not have
an error-handling convention, and writing one down because two files agree is
inventing a standard and attributing it to the project.

So: discover, and **report confidence**. What was found consistently is written;
what was found inconsistently is reported as inconsistent and left for a person.

## What it may write

Installation bounds this: nothing may change the repository's build, its
dependencies or its layout. So `init` writes only harness-owned files - the
profile and the constitution - and proposes everything else.

What it must **not** do: create a unit of work, run a gate, install a hook that
changes what other tools do, or touch `.gitignore`. spec-kit's `implement`
writes ignore files for detected technologies; that is a repository change made
by a command the user ran for a different reason.

## What it detects

- **Markers**, for every installed pack, to report which verbs will resolve. -
  **The task runner**, if any, and its declared tasks. - **The version control
  system** and the protected branch. - **Existing artifacts** - a `specs/`, a
  `docs/decisions/`, an `adr/` - so the declared layout matches what already
  exists. - **Existing templates** - `.github/ISSUE_TEMPLATE/`, a pull request
  template - which are recorded as the ones to use. - **The writing language**
  in use.

## The surface

`disable-model-invocation: true`. Writing configuration into a repository is
not something the model should decide to do mid-task.

Shell injection pays here: the detection is a fixed set of cheap commands, and
running them before the model sees the prompt turns a ten-turn survey into one.

## Conclusions

1. Read before asking; ask only what reading cannot answer. 2. Report what was
   found inconsistent, and pick none of the variants. 3. Write only the profile
   and the constitution. 4. Record the existing layout and templates, and
   impose none. 5. Report which verbs resolve and which do not - `init` that
   leaves a repository unable to run `test` should say so, loudly, because that
   is the first thing the user will hit. 6. Be re-runnable, and never overwrite
   a profile without saying what changed.

## Sources

All read 2026-09-20.

- [github/spec-kit](https://github.com/github/spec-kit) - `specify init`, the
  `init-options.json` numbering scheme, and per-agent template installation. -
  [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) - `kiro-spec-init`, which
  initialises per unit of work and never per repository. - [Pimzino/claude-code
  -spec-workflow](https://github.com/Pimzino/claude-code-spec-workflow) -
  `spec-steering-setup` and the three steering documents it writes by reading
  the codebase. -
  [buildermethods/agent-os](https://buildermethods.com/agent-os) - standards
  discovered from the codebase, which nobody declared. - [Slash
  commands](https://code.claude.com/docs/en/slash-commands) -
  `disable-model-invocation`, and shell injection for gathering context before
  the model reads the command.
