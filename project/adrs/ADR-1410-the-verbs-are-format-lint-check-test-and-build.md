---
id: ADR-1410
artifact: adr
status: approved
revised: 2026-09-27
addresses: [REQ-2908]
supersedes: []
---

# 1410. The verbs are `format`, `lint`, `check`, `test` and `build`, and the old names are read one release

## Decision

The five verbs are `format`, `lint`, `check`, `test` and `build` (REQ-2908).
`format` replaces `fmt` and `check` replaces `typecheck`, and each keeps its
meaning: `format` formats, and `check` runs the static checks a compiler or a
type checker makes without producing anything (REQ-0130). A repository
declares them under `[verbs]` in `.meowpaw/profile.toml` by the new names, and
`meow-verbs run` and `meow-verbs status` name them so.

For one release, `meow-verbs` 0.3.0, the program still reads `fmt` and
`typecheck`. A profile key under an old name resolves the new verb, and
`status` notes that the key is renamed and that 0.4.0 stops reading it. A verb
named the old way on the command line runs the new one with the same notice.
Where a profile declares a verb under both names, the new name wins and the
notice names the key it ignored. `meow-verbs` 0.4.0 reads the new names alone.

After this decision a person declares and runs the verbs by the new names,
and a profile written for the old ones keeps resolving for one release while
saying what to change. What still doesn't work: after 0.4.0 a profile still
using `fmt` or `typecheck` reports those verbs as undeclared.

## Why

I decided the names on 2026-09-27, and REQ-2908 records it. `typecheck` names a
mechanism most languages lack, so a repository with no type checker reads it
as a verb that doesn't apply, where `check` names what every compiled or
checked language does before it builds. `format` is the word a person uses,
and `fmt` is a tool's abbreviation of it.

The profile is the repository's own declaration, and the constitution holds
that a convention the harness changes is announced before it is removed
(REQ-3004), so a profile written last week can't stop resolving without a
word. Reading both names for one release, with a notice naming the key to
rename, turns the change into one edit the person makes when they see it.

The strongest objection: `check` is also the name of `paw check` and
`meow-licence check`, so a reader can mistake the verb for either. The verb is
always written as a verb of `meow-verbs`, under `[verbs]` or after
`meow-verbs run`, and a page that could be misread says "the `check` verb".

## Alternatives

| Option                                    | Better at                                         | Why it lost                                                               |
| ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------- |
| Do nothing                                | No profile changes                                | I decided the names                                                       |
| Rename, reading the old names one release | A profile keeps resolving and says what to change | Chosen                                                                    |
| Rename with no transition                 | One set of names from the first day               | Every profile using `fmt` or `typecheck` stops resolving without a notice |
| `types` or `analyse` for `typecheck`      | Neither collides with another command's `check`   | I chose `check`; `types` reads oddly where there is no type checker       |

## What it costs

Every profile, page and specification naming a verb changes once, and every
repository using the harness renames two keys within one release. The program
carries the old names until 0.4.0.

## What would reverse it

- Repositories confusing the `check` verb with `paw check` or
  `meow-licence check`, shown by a profile declaring a record or licence check
  under `[verbs] check` where it means type checking, in two repositories.

## Consequences

- `meow-verbs` 0.3.0 names the new verbs, reads the old two with a notice,
  and 0.4.0 stops reading them.
- This repository's profile, the unit's skill and page, the tutorial, the
  introduction, the vision, the templates and SPC-1040 name the new verbs.
- ADR-1070 is amended: the verbs keep their meanings under the new names.

## How I will know it was realised

1. `meow-verbs status` lists `format`, `lint`, `check`, `test` and `build`,
   and `meow-verbs run format` runs the command declared under `format`.
2. A fixture shows a profile declaring `fmt` resolving `format` with a notice
   naming 0.4.0, and `meow-verbs run typecheck` running `check` with the same
   notice.
3. No shipped file, page or specification names `fmt` or `typecheck` as a
   verb, apart from the program's reading of the old names and its fixtures.
4. REQ-2908 lands in exactly one closed task.

## What this does not settle

- The task that stops reading the old names in 0.4.0, which is written when
  0.3.0 is released.
- The names of this repository's own `mise` tasks, such as `fmt-check`, which
  are the repository's and not the harness's.
