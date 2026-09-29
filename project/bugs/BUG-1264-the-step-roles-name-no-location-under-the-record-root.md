---
id: BUG-1264
artifact: bug
status: approved
severity: minor
violates: REQ-3203
enters: design
found: 2026-09-29
revised: 2026-09-29
issue: 684
---

# The method's step roles name a kind of file where REQ-3203 asks for a location under the record root

The roles in `plugins/meow-flow/skills/method/steps/` name each step's artifact
as a kind of file, such as "a decision record's file", and never as a
location or a path pattern under the record root `.meowpaw/profile.toml`
resolves. REQ-3203 asks for the location, so a model running a step learns
what to write but not where it lands.

## Reproduction

`main` after #680, with `meow-flow` 0.39.1.

1. Read the `<role>` of each file under
   `plugins/meow-flow/skills/method/steps/`.
2. Search the ten files for `[record] root`, for `project/` and for a path
   pattern such as `adrs/ADR-NNNN-<slug>.md`.

## What the system does

Each role names a kind: "a research record's file", "one requirement record's
file for each obligation", "a decision record's file", "the specification's
file", "the epic's file and each task's file", "the check files, the kept
failing run, and the task file's `## Cover`", "the changed files, the kept
runs, and the task file's `## Evidence`", "each user-facing page it changed",
and "the epic's file, its verification and the evidence it cites". No step
file names the record root or a directory under it. Verify names "the
evidence it cites" where REQ-3203 names "the kept evidence".
`MethodSkill.test_each_role_names_where_its_artifact_lands` in
`plugins/meow-flow/tests/test_record.py` checks these phrases, taken from
ADR-1620's table, so it passes on a role that names no location.

## What it should do, and why

Each role except review's names where its artifact lands as a path pattern
under the record root: `[record] root` in `.meowpaw/profile.toml`, or
`project/` where the profile declares none, the default the templates and
`paw` use. A record-writing step names its kind's directory and file pattern
from the layout `meow-flow` ships, such as `adrs/ADR-NNNN-<slug>.md`.
Implement and cover name the task's file under the record root and the kept
runs under the evidence directory, `evidence_dir` under `[verbs]` or
`evidence` under the record root. Verify names the epic's file and the kept
evidence its verification cites. Document names the pages at their own paths
in the repository's documentation, because a user-facing page doesn't live
under the record root, which is the one step where REQ-3203's wording can't
apply as written.

REQ-3203 asks for the location because a step whose output the next step
can't find by path can't be approved, cited or checked by it.

## Triage

It enters at design, because REQ-3203 is right and ADR-1620 chose "the
kind's name and not a path" against its wording. ADR-1620 is approved and
frozen, so this record states the corrected rule, and SPC-1090's section "The
steps" carries it. Minor, because the model can still find a kind's
directory through `paw template` and the templates, so no artifact is lost;
the instructions just don't say where.

## Closed by

`MethodSkill.test_each_role_names_where_its_artifact_lands` in
`plugins/meow-flow/tests/test_record.py`, rewritten to read each role for the
record root, its default and the path pattern of each artifact, and verify's
for the kept evidence.

## Tasks

- [x] T-001 TSK-2574 name the path pattern under the record root in each step's
      role, in `plugins/meow-flow/skills/method/steps/`
      evidence: 1 check seen failing first on 38 phrases, and every
      `meow-flow` fixture passing, in #696.
