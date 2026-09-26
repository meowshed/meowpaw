---
id: EPC-1050
artifact: epic
status: approved
revised: 2026-09-26
realises: ADR-1080
checked-at: "#130"
---

# The commit convention, checked before a message is used

Realises exactly one authorising record, ADR-1080. The epic is complete when
`meow-scm` checks a commit message against the convention a repository
declares and against the attribution ban, reports an undeclared convention as
undeclared, and this repository uses it in place of its temporary `commits`
skill.

## Acceptance criteria

Taken from ADR-1080, from its list of how I will know it was realised, before
the tasks below were written:

1. `check-message` passes a message in this repository's convention, and fails
   a message with an undeclared type, a subject over the limit, a subject
   ending in a full stop and a missing sign-off, naming each.
2. It fails a message carrying a co-author trailer naming a model, or a
   "Generated with" footer, with or without a declared convention.
3. With no `[commits]` table, it applies the attribution ban, reports the
   convention as undeclared, and passes nothing as meeting a convention.
4. With the interpreter missing, it reports that it couldn't check, and exits
   non-zero.
5. Run over this repository's last ten commits on `main`, it reports each one
   that breaks the declared convention and passes the rest.
6. `.claude/skills/commits/` is gone, and a session asked to write a commit
   message loads `meow-scm:commit` and runs the check.
7. Every requirement ADR-1080 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1300 `plugins/meow-scm/`: the manifest, the launcher and the
      program's `convention` and `check-message`, each check in SPC-1050 a
      fixture
      closes: REQ-1290, REQ-1294, REQ-1295, REQ-1302, REQ-1308, REQ-1310,
      REQ-1314, REQ-1318
      evidence: fourteen fixtures, each seen failing against a stub and passing
      against the program, in #126. TSK-1300 carries the runs.

- [x] T-002 TSK-1310 the skill, the documentation page, the budget, the
      marketplace entry, this repository's `[commits]` table, and retiring the
      temporary `commits` skill
      closes: REQ-1304, REQ-2816
      evidence: the check failing the one over-long subject in the last ten
      commits, and a session running it before using a message, in #127.
      depends: TSK-1300 - the skill runs the program, and the convention it
      declares is read by it

## Verified

Checked under issue 130 at revision `af5c65c`, with evidence gathered there
and not carried over from the tasks. Every criterion is met:

| Criterion                                                                 | Evidence at `af5c65c`                                                                                      |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1. A message in the convention passes; each break is named                | `test_a_message_in_the_convention_passes`, `test_each_break_is_named`                                      |
| 2. Attribution fails, with or without a convention                        | `test_attribution_fails_with_a_convention`, `test_attribution_fails_without_a_convention`                  |
| 3. No `[commits]` table: the ban alone, the convention undeclared         | `test_no_commits_table_leaves_the_convention_undeclared`                                                   |
| 4. No interpreter: unchecked, non-zero                                    | `test_no_interpreter_leaves_the_message_unchecked`                                                         |
| 5. The last ten commits: each break reported, the rest passed             | `check-message` failed only `e51ac8a` (#119, a 78-character subject) and passed the other nine             |
| 6. The temporary skill gone; a session loads the skill and runs the check | `.claude/skills/commits/` absent; the session TSK-1310 records, which ran `convention` and `check-message` |
| 7. Every requirement in one closed task, nothing outstanding              | `tools/check_coverage.py`: EPC-1050 10 of 10, 0 coverage failures                                          |

All fourteen fixtures ran with `python3 -m unittest discover -s
plugins/meow-scm/tests`, which reported `OK`. This repository's `test` verb
didn't run them until this check, so a break in the commit check wouldn't have
failed `test`; `.meowpaw/profile.toml` now runs them beside `meow-verbs`'s.

## Coverage

ADR-1080 addresses ten requirements. Each lands in exactly one task above,
and `tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

T-001 alone is the smallest subset that tests the decision: with it closed, a
message can be checked against a declared convention and the attribution ban.
T-002 puts it in front of the model and retires the skill it replaces.

## Not covered

Nothing ADR-1080 addresses is left out. Signing, branches, working trees and
the hook that would enforce the check, which ADR-1080 leaves to a pack, are
outside this epic.
