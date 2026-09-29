---
id: TSK-2574
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1264
closes: []
issue: 684
---

# Name the path pattern under the record root in each step's role

Each step's role under `plugins/meow-flow/skills/method/steps/`, except
review's, names where its artifact lands as a path pattern under the record
root `.meowpaw/profile.toml` resolves, with `project/` as the default. So a
model running a step knows where the file goes, which REQ-3203 asks of the
instructions. One task, one branch, one pull request, one review.

## Acceptance criteria

1. Given each role of research, requirements, design, spec, epic, cover,
   implement and verify, when it is read, then it names `[record] root` in
   `.meowpaw/profile.toml`, the default `project/`, and the path pattern of
   each record it writes: `research/RES-NNNN-<topic>.md`,
   `requirements/REQ-NNNN-<slug>.md`, `adrs/ADR-NNNN-<slug>.md`,
   `specs/SPC-NNNN-<topic>.md`, `epics/EPC-NNNN-<slug>.md` and
   `tasks/TSK-NNNN-<slug>.md` as its step writes them. Closed by:
   `MethodSkill.test_each_role_names_where_its_artifact_lands` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the roles of cover, implement and verify, when each is read, then it
   names the kept runs or the kept evidence and the evidence directory,
   `evidence_dir` under `[verbs]` or `evidence` under the record root. Closed
   by: `MethodSkill.test_each_role_names_where_its_artifact_lands`.
3. Given document's role, when it is read, then it names the pages at their
   own paths in the repository's documentation, outside the record root, and
   given review's, then it still writes nothing into the repository. Closed
   by: `MethodSkill.test_each_role_names_where_its_artifact_lands`.

## What to do

Rewrite the sentence "Its artifact lands in ..." in each step file's
`<role>` to name the path pattern under the record root, following
`meow-author:write`. Take each kind's directory and file pattern from
`plugins/meow-flow/lib/layout.toml` and the constitution's layout table.
Rewrite `LANDS` and the check that reads it in
`plugins/meow-flow/tests/test_record.py` to assert the record root, its
default and each pattern, and not ADR-1620's literal phrases. State the rule
in SPC-1090's section "The steps". Raise `meow-flow`'s patch version. Write
the check first, in a commit of its own, and see it fail.

## Depends on

Nothing. BUG-1264 is approved.

## Cover

- Checks: not yet
- Failing run: not yet
- Landed in: not yet
- Judgement: not yet

## Evidence

Not yet. Once done: the command, its exit status and its output, collected at
the revision that merges.

## Left alone

The steps' `<steps>` and `<rules>`, which already say what to write. A
command that prints where a new record of a kind lands, which would let a
role cite it in place of the pattern: the pattern is enough for the model,
and a new command is a capability, not a fix.
