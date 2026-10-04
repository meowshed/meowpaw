---
id: TSK-1880
artifact: task
status: done
revised: 2026-09-26
epic: EPC-1270
closes:
  [
    REQ-0010,
    REQ-0016,
    REQ-0018,
    REQ-0022,
    REQ-0024,
    REQ-0026,
    REQ-0028,
    REQ-0030,
  ]
issue: 339
---

# Record the evidence for the adoption rules that already hold

Record the evidence for the adoption rules that already hold, as ADR-1270 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given each requirement this task closes, when its evidence is gathered at the current revision, then the task records a command and its output, or the file and line, that shows it holds. Closed by: the evidence table.

## What to do

Gather, at the current revision, the evidence that each requirement this task closes holds, and record it.

## Depends on

Nothing. ADR-1270 is approved.

## Evidence

Gathered at the revision this task's change lands on. Every requirement held
already, and nothing changed but this record.

| Requirement | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| REQ-0010    | A unit installs into Claude Code's own plugin directory under the person's home, and changes no build, dependency or layout of the repository. TSK-1830 accounts for every file the native tool writes: none outside fixtures but `index --write`, which a person asks for; the only other files the harness writes into a repository are `/meow-method:init`'s profile and a missing `CLAUDE.md`, which a person starts. |
| REQ-0016    | The profile template names no language, build tool or package manager, which `test_the_profile_template_names_no_language` holds; `CLAUDE.md`'s principle that the method names no language holds every prompt; and a verb the profile doesn't declare is reported unresolved, never guessed, so a repository in a language the harness doesn't know loses only its undeclared verbs.                                     |
| REQ-0018    | Every artifact is Markdown with YAML front matter, and every configuration file is TOML; TSK-1690 found no directive or custom syntax in the record, and ADR-1210's reading of a record needs no program.                                                                                                                                                                                                                 |
| REQ-0022    | A repository overrides the verbs, the commit convention, the trunk, the signature policy and the record's root in `.meowpaw/profile.toml`; any template in `.meowpaw/templates/`; and the writing standard with `.meowpaw/prose/`, as step 1 of the `writing` skill says.                                                                                                                                                 |
| REQ-0024    | Each override above is a file in the repository, and no step edits an installed unit's file.                                                                                                                                                                                                                                                                                                                              |
| REQ-0026    | `meow-method template <kind>` prints the repository's own template where one exists, which `test_template_prefers_the_repository_own` holds, and `/meow-method:init` records the layout and templates it finds and imposes none, rule N4.                                                                                                                                                                                 |
| REQ-0028    | With no record, the session hook prints nothing: `status --waiting` in a repository with none printed 0 bytes, and `test_a_repository_with_no_record_prints_nothing` holds it.                                                                                                                                                                                                                                            |
| REQ-0030    | Only `meow-method`'s part of the native tool reads the record, in crates/meow/src/main.rs crates/meow/src/record.rs, behind the `record` feature; `meow-verbs`, `meow-scm`, `meow-git`, `meow-prose` and `meow-core` read no `[record]` and work in a repository that keeps none.                                                                                                                                         |

```text
$ python3 -m unittest plugins/meow-method/tests/test_record.py -k prefers_the_repository_own -k no_record_prints_nothing -k profile_template_names_no_language
Ran 3 tests in 0.344s
OK
```

## Left alone

A doctor that reports every unit's capabilities at once, which ADR-1270
leaves.
