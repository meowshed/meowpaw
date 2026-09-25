---
id: EPC-1040
artifact: epic
status: approved
revised: 2026-09-24
realises: ADR-1070
checked-at: "#115"
---

# The five verbs, resolved from the profile

Realises exactly one authorising record, ADR-1070. The epic is complete when
`meow-verbs` resolves the five verbs from a repository's profile, reports each
as resolved or as unresolved and of which kind without running anything, runs
a verb recording its command, exit status and whole output, and never reports
an unresolved verb as passed, and when this repository uses it for its own
verbs.

## Acceptance criteria

Taken from ADR-1070, from its list of how I will know it was realised, before
the tasks below were written:

1. In a repository with no profile, `meow-verbs status` reports all five verbs
   unresolved as "no profile", and `meow-verbs run lint` reports lint
   unresolved and exits with a status that is not success.
2. With a profile that can't be parsed, all five verbs report "profile
   unparseable", and nothing runs.
3. With a profile declaring `lint` as a command that fails, `run lint` reports
   the exact command, its exit status and its whole output, with the failing
   lines in the report.
4. A key the unit doesn't recognise is reported, and every declared verb still
   resolves.
5. With the interpreter missing, every verb reports unresolved, and nothing
   reports passed.
6. This repository's `meow-verbs status` shows `fmt`, `lint` and `test`
   resolved from its profile, and `typecheck` and `build` undeclared.
7. Every requirement ADR-1070 addresses lands in exactly one closed task, and
   the checks over the record report nothing outstanding.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass.

## Tasks

- [x] T-001 TSK-1280 `plugins/meow-verbs/`: the manifest, the launcher and the
      program's `status` and `run`, each failure path in SPC-1040 a fixture
      closes: REQ-0130, REQ-0131, REQ-0134, REQ-0135, REQ-0136, REQ-0144,
      REQ-0150, REQ-0154, REQ-0156
      evidence: twelve fixtures, each seen failing against a stub and passing
      against the program, in #110. TSK-1280 carries the runs.

- [x] T-002 TSK-1290 the skill, the documentation page, the budget, the
      marketplace entry and this repository's own profile
      closes: REQ-0158
      evidence: this repository's verbs resolving and passing through the
      program, and a session calling it in place of a command, in #111.
      depends: TSK-1280 - the skill calls the program, and the profile is read
      by it

## Verified

Checked at revision `b242111`, with evidence gathered there and not carried
over from the tasks, because evidence gathered before a change doesn't survive
it. Every criterion is met:

| Criterion                                                    | Evidence at `b242111`                                                                               |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| 1. No profile: all unresolved; `run lint` fails              | `test_no_profile_leaves_every_verb_unresolved`, `test_run_without_a_profile_runs_nothing_and_fails` |
| 2. Unparseable profile: all unresolved, nothing runs         | `test_an_unparseable_profile_resolves_nothing_and_runs_nothing`                                     |
| 3. A failing `lint`: command, status and whole output        | `test_a_failing_verb_reports_its_command_status_and_whole_output`                                   |
| 4. An unknown key is reported, the rest resolve              | `test_an_unknown_key_is_reported_and_the_rest_still_resolve`                                        |
| 5. No interpreter: all unresolved, nothing passed            | `test_no_interpreter_leaves_every_verb_unresolved`                                                  |
| 6. This repository: `fmt`, `lint`, `test` resolved           | `meow-verbs status`: the three resolved from `.meowpaw/profile.toml`, two undeclared                |
| 7. Every requirement in one closed task, nothing outstanding | `tools/check_coverage.py`: EPC-1040 10 of 10, 0 coverage failures                                   |

All twelve fixtures ran with `python3 -m unittest discover -s
plugins/meow-verbs/tests`, which reported `OK`, and `meow-verbs run fmt lint
test` reported `summary: fmt passed, lint passed, test passed` and exited 0.

## Coverage

ADR-1070 addresses ten requirements. Each lands in exactly one task above, and
`tools/check_coverage.py` compares the decision's `addresses` against the
union of the tasks' `closes`.

T-001 alone is the smallest subset that tests the decision: with it closed, a
repository that declares its verbs gets the honest report ADR-1070 promises.
T-002 puts it in front of the model and uses it here.

## Not covered

Nothing ADR-1070 addresses is left out. What ADR-1070 leaves to later
decisions, runner binding, packs, subsets and evidence, is outside this epic.
