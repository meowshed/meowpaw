---
id: TSK-2572
artifact: task
status: approved
revised: 2026-09-29
bug: BUG-1262
closes: []
issue: 664
---

# Refuse a Failing run that lies outside the evidence directory or that git ignores

`paw ready implement` refuses a Cover whose `Failing run` names a file outside
the evidence directory, or a file git ignores. So the gate lets an
implementation start only once its failing run is kept where ADR-1550 keeps
evidence, in a file every clone receives. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given an approved open task whose Cover is otherwise filled, when
   `Failing run` names `README.md`, a regular file at the repository's root,
   then `paw ready implement` exits 1 with a line naming that path under
   `Failing run`. Closed by:
   `CoverRun.test_a_failing_run_outside_the_evidence_directory_is_refused` in
   `plugins/meow-flow/tests/test_record.py`.
2. Given the same task, when `Failing run` names a file under the evidence
   directory that `.gitignore` ignores, then `paw ready implement` exits 1
   with a line naming that path and saying git ignores it. Closed by:
   `CoverRun.test_a_failing_run_git_ignores_is_refused` in
   `plugins/meow-flow/tests/test_record.py`.
3. Given a profile declaring `evidence_dir = "kept"` under `[verbs]`, when
   `Failing run` names `kept/run.txt`, then `paw ready implement` exits 0, and
   when it names `project/evidence/run.txt`, it exits 1 naming that path.
   Closed by:
   `CoverRun.test_the_profile_declares_the_evidence_directory` in
   `plugins/meow-flow/tests/test_record.py`.

## What to do

In `cover_gaps` in `crates/meow/src/record.rs`, test the path under
`Failing run` for lying under the evidence directory, resolved as
`crates/meow/src/verbs/ledger.rs` resolves it, `evidence_dir` under `[verbs]`
or `evidence` under the record root, and for not being ignored by git. Where
git can't answer, as outside a git work tree, don't refuse on that ground,
because ADR-1550 reports that case as unchecked and not as ignored. Name the
path in each refusal. State the rule in SPC-1090's section "The gate".

Move the fixtures' failing run from `evidence/` to `project/evidence/`, the
evidence directory of the fixture record, so the other Cover checks keep
exercising a Cover that passes. Raise `meow-flow`'s patch version. Write the
checks first, in a commit of their own, and see them fail.

## Depends on

Nothing. BUG-1262 is approved.

## Cover

- Checks: plugins/meow-flow/tests/test_record.py
- Failing run: project/evidence/ec12b7c3f9b6.txt
- Landed in: #666
- Judgement: none

## Evidence

`cover_gaps` in `crates/meow/src/record.rs` asks a new function,
`not_evidence`, about the path under `Failing run` once `unkept` accepts it as
a file in the repository. It refuses a run outside the evidence directory,
which `evidence_dir` reads from `[verbs] evidence_dir` or places at `evidence`
under the record root, and a run `git check-ignore` reports as ignored. The
fixtures' failing run moved from `evidence/` to `project/evidence/`,
including the `Dependencies` fixture #662 added, and
SPC-1090's section "The gate" states the rule. `meow-flow` goes to 0.39.1.

The three checks in the class `CoverRun` failed first: `meow-verbs run test`
exited 1 with `FAILED (failures=3)`, kept as
`project/evidence/ec12b7c3f9b6.txt`, in the commit that held the checks alone.
They pass now:

```text
$ python3 -m unittest test_record    # in plugins/meow-flow/tests
Ran 206 tests
OK                                   # exit 0
```

`meow-verbs evidence --keep format lint check test build` exits 0 on this
change's own tree, each result kept in `project/evidence/`, as the pull
request cites.

## Left alone

The file's content: the header `meow-verbs evidence` writes, because ADR-1270
lets a repository adopt `meow-flow` alone, and whether the run failed, which
ADR-1620 leaves to the decision on REQ-3206. A file git doesn't track yet, as
opposed to one it ignores, because the cover step may fill the Cover before
the change carrying the run is committed, and git will commit it with that
change.
