---
id: ADR-2850
artifact: adr
status: approved
revised: 2026-10-10
addresses: [REQ-4200, REQ-4202, REQ-4204]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2850. The five verification obligations are called stages

## Decision

I call `format`, `lint`, `check`, `test` and `build` stages, in place of verbs
(REQ-4200). A stage is a named obligation that a repository binds to a command
and that a unit's detection may supply, and the stages are independent: a
failure in one stops no other, and only `format` goes first, because a
formatter that rewrites files leaves every earlier result stale.

A profile declares them under a `[stages]` table (REQ-4202). A `[verbs]` table
keeps resolving, and every report that reads it names `[stages]` as the table
to use, until the second release after the one that adds `[stages]` (REQ-4204,
REQ-3004). That second release removes the read of `[verbs]`.

The names of the five stay as REQ-2908 fixes them, and so do the command-line
arguments of `meow-checks run`. Living and shipped text says "stage" once the
tasks of EPC-2760 have landed. A frozen record keeps "verb", as the records
that say "forge" do.

Once this is accepted, a profile can use either table and every shipped page
reads "stage". What still doesn't change is the Rust module and directory
names that contain "verbs", because no reader of the harness meets them.

## Why

RES-0344 found that no word from the tools the harness sits beside is free
here. `task`, `check`, `command` and `target` each name something else in
living and shipped text, between 490 and 3,045 times, and a stage already
contains checks, so renaming to `check` would make a check contain checks.
`stage` appears twice and names nothing else, and it is the word a developer
from a continuous integration tool already has for "a named piece of the
pipeline", with `format` first fitting its order.

The profile table has to be renamed with the word, because a page that says
"stage" over a file that says `[verbs]` is two vocabularies in one sentence.
REQ-3004 already sets the cost: two releases of reading the old table.

## Alternatives

| Option               | Better at                                    | Why it lost                                                                    |
| -------------------- | -------------------------------------------- | ------------------------------------------------------------------------------ |
| Do nothing           | No migration, and 1,385 uses stay true       | The owner dislikes the word, and nothing in RES-0344 argues for it             |
| `task`               | The word mise and Task use                   | 3,045 uses, and a task record is the method's unit of work                     |
| `check`              | The unit is `meow-checks`                    | A stage contains checks, and `check` is one of the five                        |
| `slot`               | Free here, and it says a repository fills it | No tool in the survey uses it, and it names the mechanism and not the purpose  |
| Rename the word only | No profile migration                         | A profile that says `[verbs]` under pages that say "stage" is two vocabularies |

## What it costs

About 135 living and shipped files change, one profile table gains a second
name, and the harness reads both for two releases. A reader who comes from
GitLab CI reads "stage" as a sequence, and the definition in every page that
introduces the word has to say they are independent. If that reading persists,
the answer is `slot`, and a second rename.

## What would reverse it

- A reader study or a run of questions showing that readers take "stage" as a
  gating sequence in spite of the definition. While no such evidence exists,
  the owner's preference decides between two words that cost the same.

## Consequences

REQ-4200, REQ-4202 and REQ-4204 are added and nothing is withdrawn, because
REQ-0130, REQ-0131, REQ-0134 and REQ-2908 keep their obligations and only
their word changes. SPC-1040 gains a section that states the term. EPC-2760
carries three tasks: the profile reads `[stages]`, living and shipped text says
"stage", and a check fails on "verb" in living and shipped text.

## How I will know it was realised

1. A profile with a `[stages]` table resolves the five, and a profile with a
   `[verbs]` table resolves them and reports `[stages]` as the table to use
   (REQ-4202, REQ-4204).
2. A check fails, naming the file and the line, on "verb" or "verbs" in a
   living or shipped file outside an allow-list (REQ-4200).

## What this does not settle

- The Rust modules and directories named for "verbs", and the `mise` task
  names ADR-1410 left to each repository.
- Which release removes `[verbs]`: it is the second release after the one that
  adds `[stages]`, and the release notes of that first release name it.
