---
id: EPC-1590
artifact: epic
status: approved
revised: 2026-09-29
realises: ADR-1600
checked-at: "#597"
---

# The prose gate is a program, and it blocks only on a span it found in the command

Realises exactly one authorising record, ADR-1600. The epic is complete when
the prose gate runs as a program with no model and blocks only on a span it
quoted from the command. It carries no task of its own: the fix landed as
TSK-2470, which BUG-1230 carries, in #600, before any epic realised the
decision. So `paw status` reported ADR-1600 as waiting for an epic although
its work had merged. This epic records that realisation and adds no
implementation; its verification checks REQ-3182 again, as criterion 5 says.

## Acceptance criteria

Taken from ADR-1600, from its list of how I will know it was realised:

1. The four texts BUG-1230 records pass the gate, each as a fixture, and a
   text with an idiom, one with a bold-only line and one hiding behind
   `--body-file` are each blocked with a span found verbatim in the command.
2. `hooks/hooks.json` holds no hook of type `prompt`.
3. Every fixture runs the unit's launcher, so the gate a repository installs is
   what the fixtures check.
4. REQ-1756, REQ-3183, REQ-3187 and REQ-2076 are each closed by a task, named
   under Not covered.
5. REQ-3182 is verified against the program gate: a fixture shows a text held
   before it is published for each command the gate reads, a commit message
   through `-m`, and an issue, a pull request and a release body through
   `--body`, `--body-file`, `--notes` and `--notes-file`. The squash message a
   merge writes isn't read, so REQ-3182 is met in part, and the verification
   says so.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

None. TSK-2470 realised the decision, and it stays BUG-1230's task, because a
task names one authorising record and a defect may carry its own (REQ-0354).
Its evidence, in pull request #600: 19 fixtures seen failing first in the
commit that held them alone, and passing after.

## Verified

I checked this under #597 on `main` after #696, gathering the evidence there
and carrying none over from TSK-2470. `meow-verbs evidence --keep format lint
check test build` exits 0 on this change's own tree, each result kept in
`project/evidence/`, as the pull request cites. The 19 fixtures in
`plugins/meow-prose-gate/tests/test_gate.py` run 19, OK, through the unit's
launcher and its `aarch64-apple-darwin` binary. Criteria 1 to 4 are met, and
criterion 5 is met in part:

| Criterion                                                                         | Evidence on `main` after #696                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. BUG-1230's four texts pass, and an idiom, a bold-only line and a file are held | The four `FalseBlocksFromBug1230` fixtures pass, and the six `TruePositives` fixtures each assert exit 2 and a span found verbatim in the command, `body.md` for `--body-file` among them                                                                                                                                       |
| 2. `hooks/hooks.json` holds no hook of type `prompt`                              | `TheHook.test_no_hook_is_a_prompt` passes, and it fails on a file holding one `prompt` hook, because it compares the set of types with `{"command"}`                                                                                                                                                                            |
| 3. Every fixture runs the unit's launcher                                         | Each fixture calls `gate()`, which runs `bin/meow-prose-gate`, or copies that launcher, as `test_a_launcher_with_no_binary_lets_the_publish_through` does; the `test` verb runs the file through `unittest discover`                                                                                                            |
| 4. REQ-1756, REQ-3183, REQ-3187 and REQ-2076 are each closed by a task            | `paw show` derives REQ-1756, REQ-3183 and REQ-3187 as closed by TSK-2470, and REQ-2076 by TSK-2150, verified under #464                                                                                                                                                                                                         |
| 5. REQ-3182 against the program gate, with a fixture for each command it reads    | Met in part. Fixtures hold a text in `git commit` through `-m` and `-F`, and in `gh pr create` and `gh issue create` through `--body` and `--body-file`. No fixture runs a `gh release` command, `--notes` or `--notes-file`, or `gh pr edit`, `gh pr comment`, `gh pr review`, `gh issue edit` or `gh issue comment`: BUG-1265 |

For criterion 5 I also fed the launcher a hook event for each of the ten
commands `hooks/hooks.json` routes, with `low-hanging fruit` in `-m`, `--body`
or `--notes`, and each exited 2 with a P1 finding. `--body-file` on
`gh pr edit` and `gh issue comment`, and `--notes-file` on `gh release create`
and `gh release edit`, each exited 2 with a P3 finding quoting the path. The
same idiom in `gh pr merge 5 --squash --subject Cache --body "..."` exited 0,
because the hook doesn't route `gh pr merge`. So the program holds every
command it reads, and the gap is the regression check BUG-1265 records, whose
task TSK-2575 adds it.

REQ-3182 is met in part against the program gate for two reasons. The squash
message a merge writes from `--subject` and `--body` is published unchecked,
as ADR-1600 accepts, and seven of the ten gated commands and both release
arguments have no fixture until TSK-2575 lands. I close the epic with
BUG-1265 open, as V14 of the verify step allows for a recorded defect:
criterion 5 itself says REQ-3182 is met in part, the program holds each form
today, and the missing fixtures guard against a regression, not a present
failure.

`paw show` still derives REQ-3182 as verified, from TSK-1140 under #118, and
REQ-3183 and REQ-3187 as closed and not yet verified, because TSK-2470 belongs
to BUG-1230 and the derivation reads a task's verification from its own
authorising record. Both disagree with this section: REQ-3182 is met in part,
and REQ-3183 and REQ-3187 are met, by the fixtures under criteria 1 and 5. The
record can't say either today, which the review step should weigh.

### Documentation

`plugins/meow-prose-gate/README.md` describes the three rules, the commands
the gate reads and the launcher's report on a machine with no binary, and the
`test` verb checked the pages. The page lists the commands without
`gh pr merge`, but it doesn't say that the squash message a merge writes goes
unchecked. That is a gap in the page, not in a criterion, and I leave it to
the review step.

### Postponements

ADR-1600 postpones no requirement.

## Coverage

ADR-1600 addresses five requirements, and this epic carries no task, because
the work landed before the epic existed. Each is named under Not covered with
the task that closed it.

The smallest set of tasks that tests the decision is TSK-2470 alone.

## Not covered

- REQ-1756, REQ-3183 and REQ-3187 are closed by TSK-2470, which BUG-1230
  carries and which landed in #600.
- REQ-2076 was closed and verified before ADR-1600, by TSK-2150 in EPC-1400.
  It is static, and the decision to use a program meets it by that choice.
- REQ-3182 was closed and verified before ADR-1600, by TSK-1140 in EPC-1010,
  but that evidence measured the prompt hook ADR-1600 removed. No task closes
  it against the program gate, so the epic's verification checks it again, as
  criterion 5 says, and it is met in part.
- What ADR-1600 leaves unsettled stays unsettled here, including: the squash
  message a merge writes from its `--subject` and `--body`; an inflected idiom
  such as `circling back`; a message passed through a variable; a match across
  a quote boundary; a bold fragment followed by text; whether other rules join
  the gate; and how `tools/measure_gate.py` and SPC-1020 apply now.
- A limit the decision accepts, not an open question: on a machine with no
  binary, the launcher reports that nothing was checked and lets the command
  run.

## Open review findings

- A reason for the marking rule's "never in a later pass", and for the `[P]`
  rule. Left: both are the template's text, and CLAUDE.md states the reason in
  the principle artifacts_stay_current.
