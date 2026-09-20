---
id: RES-0124
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0121, RES-0005
---

# just

## Summary

just makes fewer promises than the other runners, and that turns out to be an
advantage. It has no freshness model, so a green result always came from work
that happened. Its trap is different - a recipe is a function with parameters,
and a verb bound to one may not be callable the way a verb is called. Its
enumeration is exact and its format carries an explicit disclaimer of
stability.

Research for one supported tool. just runs commands and builds nothing: it
tracks no file freshness and pretends to none. That makes it the simplest of
the four runners to read, and the one whose recipes are most likely to take
arguments.

It covers what marks a just project, how recipes are enumerated, which settings
and attributes change what an invocation means, what the pack authors, and what
the skill has to contain.

It does not cover the class of task runners, which is
[RES-0121-task-runners.md](RES-0121-task-runners.md).

## The question

just makes fewer promises than mise or Task: no caching, no freshness, no
dependency graph beyond ordering. That removes most of the reporting traps the
other two have and introduces a different one. A recipe is a function with
parameters, and a verb bound to one may not be callable the way a verb is
called.

## Method

We fetched and read the vendor manual on 2026-09-20. The dumping page gave the
machine-readable output and its stability disclaimer. The attributes page gave
the full list with the version each was introduced in, and the settings page
gave what changes a recipe's environment.

The attribute versions were taken from the manual's own table, and estimated
nowhere, because a pack has to know which of them a given installation has.

Nothing was installed or run.

## Findings

### The markers are three spellings, and a fallback that reaches upward

just reads `justfile`, `.justfile` or `Justfile`. A `set fallback` in the file
makes just _"Search for `justfile` in parent directory if the first recipe on
the command line is not found"_, which is how a monorepo avoids changing
directory.

That setting is the provenance question in this tool. With it on, a recipe the
pack invokes may be defined in a parent directory's justfile, and the pack
reports where the recipe came from, assuming nothing about it being local.

### Enumeration is exact, and the format carries no promise

`just --dump` writes a formatted justfile to standard output, and
`--dump-format json` _"print[s] a JSON representation of a `justfile`."_ That
is the exact enumeration a pack wants: recipes, parameters, dependencies and
documentation as data, scraped from no `--list` output.

The caveat is stated about the neighbouring feature: _"formatting is not
covered by any backwards compatibility guarantee and is subject to change from
time to time."_ The JSON dump is documented in the same place and carries no
separate promise. So a pack parses defensively and reports an unrecognised
shape as unresolved, crashing on nobody else's patch release.

### Recipes take arguments, which is the trap a verb walks into

Recipes accept command-line arguments including flags and options. A recipe
named `test` may require a parameter, and a verb invoking it bare fails for a
reason that is neither the tool nor the code.

The JSON dump carries the parameters, so a pack detects this, and discovers it
by no failure, and a pack that reads the dump has no excuse for getting it
wrong.

`[positional-arguments]` and `set positional-arguments` change how arguments
reach the recipe body, which matters when the pack is passing anything through.

### Attributes change the meaning of a recipe, and three of them change a report

| Attribute                         | What it does                                  | Since  |
| --------------------------------- | --------------------------------------------- | ------ |
| `[private]`                       | Makes a recipe, alias or variable private     | 1.10.0 |
| `[confirm]`                       | Requires confirmation before running          | 1.17.0 |
| `[no-cd]`                         | Does not change directory before running      | 1.9.0  |
| `[no-exit-message]`               | Suppresses the error message on failure       | 1.7.0  |
| `[script]`                        | Runs the recipe as a script                   | 1.33.0 |
| `[group]`, `[doc]`                | Grouping and documentation                    | 1.27.0 |
| `[linux]`, `[macos]`, `[windows]` | Enables the item on one platform              | 1.8.0  |
| `[positional-arguments]`          | Positional arguments for this recipe          | 1.29.0 |
| `[working-directory]`             | Sets the recipe's working directory           | 1.38.0 |
| `[extension]`                     | Sets a shebang recipe's script file extension | 1.32.0 |

Three matter to a harness.

`[confirm]` means the author wanted a person. A verb bound to such a recipe
is not run unattended, for the same reason mise's `confirm` field is not
overridden.

`[no-exit-message]` suppresses the message on failure. The exit status is still
correct, but the output a harness captures as evidence will not say what went
wrong, and the pack says that, presenting no empty failure.

`[private]` means the author did not intend the recipe to be called
directly. Binding a verb to a private recipe is using an implementation detail
as an interface.

The platform attributes mean an enumerated recipe may not exist on the machine
running the verb, which is a resolution failure with a clear cause.

### Settings change the environment, and one of them loads a file nobody mentioned

`set shell` chooses the shell for recipes and backticks. `set dotenv-load`
loads a `.env` file where one exists, and `set dotenv-filename` names a
different one. `set export` exports every variable as an environment variable,
and `set allow-duplicate-recipes` lets a later recipe override an earlier one.
`set ignore-comments`, `set tempdir`, `set working-directory` and `set
unstable` do what their names say.

`dotenv-load` is the one with a consequence beyond convenience. With it on, the
recipe's environment includes whatever is in `.env`, which is frequently where
credentials live. A harness capturing the environment of a run, or logging a
command line composed from variables, is capturing that too. The pack's rule is
the same as everywhere else in this method: do not read, print or forward the
contents.

`set allow-duplicate-recipes` means one name may map to several recipes in the
file, and the last one wins. A pack matching by name takes the same last-wins
rule, and never the first match.

### There is no freshness model, and that is a feature for a harness

just does not track sources and outputs. A recipe runs when it is called. So,
unlike mise and Task, a green result from just is always a result from work
that actually happened, and there is no skipped-as-fresh case to distinguish.

Its own guarantee is narrow and real: unknown recipes and circular dependencies
are reported before anything runs.

### The dependency on a shell is the portability question

just itself needs no runtime beyond a shell, and a system without `sh` needs a
different shell configured through `set shell`. `[script]` and shebang recipes
change the interpreter per recipe, so a recipe may be Python or Node.js where
the others use shell. A pack reading the body to guess what it does will guess
wrong.

### What the pack authors

The justfile: recipes, dependencies, parameters, `[doc]` comments and settings.

Adding a recipe is the cheapest authoring action in this survey, because the
format is small and the tool reports parse errors before running anything.

### What a reviewer needs that no command reports

Whether a recipe that looks like a verb is actually one, or whether it wraps
something with side effects the name does not suggest.

Whether `set export` is exposing variables to every recipe that did not ask for
them.

Whether `.env` is loaded and whether it is committed, which is a different
question from whether it exists.

Whether duplicate recipes are deliberate or a merge artifact.

### What the skill has to contain

In the body, in this order:

1. Detection and provenance. Three file names, and `set fallback` meaning a
   recipe may come from a parent directory.
2. Enumeration. `just --dump --dump-format json`, parsed defensively,
   with parameters read from it.
3. Invocation rules. A recipe with parameters is not called bare; a
   `[confirm]` recipe is not run unattended; a `[private]` recipe is not bound
   to a verb; a platform-gated recipe may not exist here.
4. Environment. `dotenv-load` and `set export`, and the rule against
   reading or forwarding what they contain.
5. What must never happen. Binding a verb to a private recipe. Running a
   `[confirm]` recipe unattended. Presenting a `[no-exit-message]` failure as
   an unexplained one. Assuming the first of two same-named recipes wins.

In supporting files: the attribute table with versions; the settings list;
the JSON dump shape with the stability caveat; and the dated facts with what to
re-check.

## Conclusions

1. A just project is marked by `justfile`, `.justfile` or `Justfile`. 2. `set
fallback` makes a recipe's location a question, so the pack reports which
   justfile a bound recipe came from. 3. Recipes are enumerated with `just
--dump --dump-format json`, which carries parameters and dependencies as
   data. 4. The dump is parsed defensively and an unrecognised shape is
   reported as unresolved, because the neighbouring formatting feature carries
   no backwards compatibility guarantee and the dump carries no separate one. 5. A recipe with parameters is not invoked bare, and the parameters are read
   from the dump, and discovered by no failure. 6. A `[confirm]` recipe is not
   run unattended, because its author asked for a person. 7. A `[private]`
   recipe is not bound to a verb, since binding one uses an implementation
   detail as an interface. 8. A `[no-exit-message]` failure is reported as
   having its message suppressed, so an empty failure is explained, and
   presented bare never. 9. A platform-gated recipe missing on this machine is
   a resolution failure with a named cause, and no missing verb. 10. Duplicate
   recipes resolve last-wins where `set allow-duplicate-recipes` is on, and a
   pack matches accordingly. 11. `dotenv-load` and `set export` are reported as
   environment sources, and their contents are never read, printed or
   forwarded. 12. A just result is never skipped-as-fresh, because the tool has
   no freshness model, which makes a green result here stronger than the same
   result from a caching runner. 13. A shebang or `[script]` recipe may be
   written in another language, so the body is not read to infer what the
   recipe does. 14. The skill body carries detection and provenance,
   enumeration, invocation rules, environment, and the prohibitions, in that
   order.

## Sources

All read 2026-09-20.

- [just, formatting and dumping justfiles](https://just.systems/man/en/formatting-and-dumping-justfiles.html)
  - `--dump` writing a formatted justfile to standard output, `--dump-format
json` printing a JSON representation, and the statement that formatting
    carries no backwards compatibility guarantee and is subject to change.
- [just attributes](https://just.systems/man/en/attributes.html) - `[private]`,
  `[confirm]`, `[no-cd]`, `[no-exit-message]`, `[script]`, `[group]`, `[doc]`,
  the three platform attributes, `[positional-arguments]`,
  `[working-directory]` and `[extension]`, each with the version that
  introduced it.
- [just settings](https://just.systems/man/en/settings.html) - `set shell`,
  `set dotenv-load` and `set dotenv-filename`, `set export`,
  `set positional-arguments`, `set allow-duplicate-recipes` letting a later
  recipe override an earlier one, `set fallback` searching a parent directory
  when the first recipe is not found, `set ignore-comments`, `set tempdir`,
  `set unstable` and `set working-directory`.
- [The just manual](https://just.systems/man/en/) - that unknown recipes and
  circular dependencies are reported before anything runs, that recipes accept
  command-line arguments including flags and options, and that a system without
  `sh` needs a different shell configured.
