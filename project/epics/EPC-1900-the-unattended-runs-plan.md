---
id: EPC-1900
artifact: epic
status: approved
revised: 2026-09-28
realises: ADR-2000
checked-at:
---

# An unattended run is planned from an authority the repository declares

Realises exactly one authorising record, ADR-2000. The epic is complete when
`meow-unattended plan` reads a repository's `[unattended]` table, refuses
every state ADR-2000 refuses, prints the command that would start the run
with its posture and each unit named, and writes the snapshot that holds the
run's authority, as SPC-1200 states. It starts nothing.

## Acceptance criteria

Taken from ADR-2000, from its list of how I will know it was realised, before
the tasks below were written:

1. Fixture repositories with no `[unattended]` table, and with a table lacking
   each required key in turn, each give `unresolved` naming what's missing and
   exit status 3. A table naming `bypassPermissions`, a gate outside the list,
   a folder of units, a URL, and `merge_protected = true` without `merge` in
   `gates` is each refused the same way.
2. A fixture declaring `dontAsk` prints `--permission-mode dontAsk`, and the
   printed command line holds `--bare`, `--permission-prompts none`,
   `--disallowed-tools AskUserQuestion`, `--max-budget-usd` with the declared
   value, and exactly one `--plugin-dir` for each of three declared units.
3. A fixture repository with a `.mcp.json` server and a hook in
   `.claude/settings.json` gets a command line and snapshot naming neither,
   and one with an `env` block gets `unresolved` naming the file and its keys.
4. The snapshot denies `Edit` on `.meowpaw/**`, `.claude/**` and the folder
   that holds it. Changing the profile after `plan` leaves the snapshot's
   content and its hash unchanged.
5. With `merge_protected` absent, the snapshot holds the three push rules for
   the declared trunk. With it `true`, it holds none.
6. With `amend_approved` absent, a fixture record of two approved and one
   draft requirement and one approved and one draft decision gives exactly
   three deny rules on record files, one for each approved file. With it
   `true`, it gives none. A fixture profile with no `[record]` gets output
   saying there is no record to protect.
7. With `MEOWPAW_STATE=off`, `plan` writes no file and says so, and
   `plan --purge` removes every snapshot of the work tree.
8. `plan`'s output states each of the four limits of the deny rules, that the
   command needs `ANTHROPIC_API_KEY`, and that a record approved later needs a
   new plan.
9. Each check above counts what it matched, and a count of zero where one was
   expected fails it.
10. Every requirement ADR-2000 addresses, REQ-2388 and REQ-2392, lands in
    exactly one closed task.

Criterion 4 reads "the folder that holds it" where an earlier draft of
ADR-2000 read "its own path". I changed both while ADR-2000 was a draft,
because the snapshot's file name is the hash of its content, and content
can't hold a rule naming its own hash.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-3300 add `meow-unattended` with `plan`, which reads the
      `[unattended]` table, prints the command line with its posture, and
      writes the snapshot with its deny rules, in `plugins/meow-unattended/`
      and a feature `unattended` in `crates/meow`
      closes: REQ-2388
      evidence: 13 checks seen failing at the cover commit f9e8b4e, and
      passing unchanged in #662.

- [ ] T-002 TSK-3310 make `plan` load each unit by name: refuse a URL, a
      folder of units and a project `env` block, and name each unit with its
      version in the output and the snapshot
      closes: REQ-2392
      depends: TSK-3300, because it extends the program, the table reader and
      the snapshot that task adds

Neither task can run in parallel with the other, because TSK-3310 changes the
code TSK-3300 writes.

## Coverage

ADR-2000 addresses two requirements, and each lands in one task. REQ-2388
lands in TSK-3300, because the declared posture reaches the run through what
that task builds: the table, the `--permission-mode` and `--max-budget-usd`
flags, and the snapshot passed as `--settings`. REQ-2392 lands in TSK-3310,
because a unit is loaded by name only once `plan` refuses every entry that
would load by discovery or from an address that can change, and the checks
that show it are that task's.

The criteria split between the tasks as follows. TSK-3300 closes criteria 1
except the URL and folder cases, 2 except the `--plugin-dir` count, and 4 to 8. TSK-3310 closes the URL and folder cases of 1, the `--plugin-dir` count of
2, and 3. Criterion 9 binds every check in both tasks, and criterion 10 is
this epic's own.

The smallest set that tests the decision is both tasks, because REQ-2388 and
REQ-2392 are the only requirements it addresses and each rests on one of
them. Before either task is finished, one thing can be measured:
`meow-unattended` doesn't exist, so every check in both tasks fails, which is
what the cover step keeps as each task's failing run.

## Not covered

- REQ-2372, REQ-2376, REQ-2390 and REQ-2406, which ADR-2000 postpones because
  their checks need a started run. The decision that starts a run closes them
  with the evidence ADR-2000 names.
- Starting, repeating and stopping a run, crossing a declared gate, the
  sandbox and the credential removal, which ADR-2000 names as not settled.
- The user-facing pages outside the unit, `docs/README.md`'s list of units
  among them, which the document step updates once both tasks are done, from
  ADR-2000's consequences.
