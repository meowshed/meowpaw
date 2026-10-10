---
id: RES-0344
artifact: research
status: approved
revised: 2026-10-10
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# No common word for a named, runnable obligation is free here, and `stage` collides least

## Summary

The repository calls `format`, `lint`, `check`, `test` and `build` verbs, and the
owner dislikes the word. Of the words other tools use for a named, runnable
unit, `task`, `check`, `command` and `target` each name something else in this
repository, so renaming to one of them swaps one ambiguity for a larger one.
`stage` is used twice in living and shipped text and names nothing else; its
cost is that CI tools use it for a sequence that gates the next group, which
these five obligations are not.

The document covers the word, not the five names, which an approved
requirement fixes.

## The question

What should the repository call the five named verification obligations that a
profile binds to commands, so a reader who has never met the harness reads the
word without a gloss?

The assumption behind the question is that a different word would read better.
It might not: the word is in about 2,970 places, 1,385 of them in living and
shipped text, and a rename costs a deprecation window for the profile key
(the repository's rule that a deprecation spans two releases). Doing nothing is therefore an option, and the owner's objection to
the word is the only evidence against it.

## Method

I read the first-party documentation of five tools for the word each uses for a
named unit a project runs, on 2026-10-10. I counted the candidate words in
living and shipped text with `git grep -ihoP "\bword s?\b"`, excluding
`project/research`, `project/adrs`, `project/tasks`, `project/requirements` and
`project/bugs`, because those records are frozen and keep the word they were
written with. I read ADR-1070, ADR-1410 and `.meowpaw/profile.toml` for how
the five are declared. I did not survey the harness's readers, so "reads
better" is the owner's judgement and not a measurement.

## Findings

### Other tools use five different words, and none is a free one here

mise calls it a task: "A task is a named command or script that runs with your
project's tools and environment variables." npm calls it a script, and treats
`test` and `start` among others as lifecycle scripts. just calls it a recipe:
"Commands, called recipes, are stored in a file called `justfile`". GNU make
calls the name a rule is invoked by a target. GitLab CI calls a group of jobs a
stage, and its stages run in sequence: "Jobs in the next stage run after the
jobs from the previous stage complete successfully."

### The common words are already taken in this repository

Counted on 2026-10-10 in living and shipped text, excluding the frozen
records:

| Word    | Occurrences | Files | What it already means here                                                                           |
| ------- | ----------- | ----- | ---------------------------------------------------------------------------------------------------- |
| task    | 3,045       | 235   | A task record, and a mise task a stage binds to                                                      |
| check   | 2,298       | 366   | A gate check such as `style` or `kernel`, which a stage's command runs, and the stage `check` itself |
| command | 1,207       | 237   | What a stage resolves to                                                                             |
| step    | 1,461       | 191   | A step of the method                                                                                 |
| target  | 490         | 143   | A platform target such as `aarch64-apple-darwin`                                                     |
| verb    | 1,385       | 166   | The current word                                                                                     |
| stage   | 2           | 2     | Prose only, in `project/vision.md` and a pattern file                                                |
| recipe  | 1           | 1     | Prose only                                                                                           |
| slot    | 0           | 0     |                                                                                                      |

The `check` row is the one that looks like the obvious answer, because the unit
that runs the five is `meow-checks`. It is taken: the commit that composed the
gate described it as composing "the gate from the checks the verbs run", so a
verb already contains checks, and calling the verb a check would make a check
contain checks.

### The five are independent, and only `format` has an order

`meow-checks run format lint check test build` ran every one of the five when
`lint` failed and reported each result, so a failed one gates nothing. The one
order the method asks for is `format` first, because a formatter that rewrites
files leaves every earlier result stale (meow-checks skill, rule V4).

### Renaming the profile key is a migration

`[verbs]` is read by `crates/meow/src/verbs.rs`, `profile.rs` and `markdown.rs`
and declared in every repository's `.meowpaw/profile.toml`. The repository's
records require a deprecation to span two releases, and ADR-1410 did the same for `fmt` and
`typecheck` by reading the old names for one release.

## Comparison

| Option      | Better at                                                              | Why it falls short                                                       |
| ----------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Keep `verb` | No migration, and 1,385 uses stay true                                 | The owner dislikes it, and nothing else argues for it                    |
| `stage`     | Names nothing else here; CI developers know it; `format` first fits it | CI stages gate the next one, and these five don't                        |
| `task`      | The word mise and Task use, and the profile binds to mise tasks        | 3,045 uses, and a task record is the method's unit of work               |
| `check`     | The unit is `meow-checks`                                              | A stage contains checks, and `check` is one of the five                  |
| `recipe`    | Free here; just's word for a named runnable                            | Reads as a joke to most readers, and just's recipe is the command itself |
| `slot`      | Free here; it says a repository fills it                               | Reads as an implementation detail, and no tool in the survey uses it     |

## The case against `stage`

A reader from GitLab or Azure Pipelines reads "stage" as a sequence in which a
failure stops the next. A repository that binds `test` to a command that needs
`build` first would be told by the word that the harness orders them, and it
doesn't. The definition has to say it in the same sentence that introduces the
word: the five are independent, `format` goes first, and a failure in one stops
no other. If a reader still takes it as a gate, `slot` is the fallback, and the
loss is that it names the mechanism and not the purpose.

## Conclusions

1. The five named verification obligations are called stages in living and
   shipped text, and the definition says they are independent, so the sense a
   CI tool gives the word doesn't reach them (Findings: other tools; the five
   are independent).
2. A profile declares them under `[stages]`, and `[verbs]` stays readable for
   the two-release deprecation window the records set, so no repository's profile stops
   working on the day the word changes (Findings: renaming the profile key).
3. A frozen record keeps the word it was written with, as the records that say
   "forge" do, and the rename reaches living and shipped text only (Findings:
   the counts exclude frozen records).

## Sources

- [mise tasks](https://mise.jdx.dev/tasks/), read 2026-10-10 - mise's definition of a task.
- [npm scripts](https://docs.npmjs.com/cli/v10/using-npm/scripts), read 2026-10-10 - npm's script and lifecycle script.
- [just manual](https://just.systems/man/en/), read 2026-10-10 - just's recipe.
- [GNU make rule introduction](https://www.gnu.org/software/make/manual/html_node/Rule-Introduction.html), read 2026-10-10 - make's target.
- [GitLab CI `stages`](https://docs.gitlab.com/ci/yaml/#stages), read 2026-10-10 - what a stage is and how stages run.
- `project/adrs/ADR-1070-the-five-verbs-resolve-from-the-profile.md`, `project/adrs/ADR-1410-the-verbs-are-format-lint-check-test-and-build.md` and `.meowpaw/profile.toml` as of pull request 872, read 2026-10-10 - how the five are declared.
