---
id: BUG-1262
artifact: bug
status: approved
severity: major
violates: REQ-3207
enters: implement
found: 2026-09-29
revised: 2026-09-29
issue: 664
---

# `paw ready implement` accepts a Failing run that isn't kept as evidence

`paw ready implement` exits 0 on a Cover whose `Failing run` names any regular
file in the repository, such as `README.md` or a file git ignores. So the
implementation starts although no run was kept as evidence, which REQ-3207
asks of the cover step.

## Reproduction

`main` after #658, with `meow-flow` 0.36.0 built by `crates/meow/build-units`.

1. Take the fixture record in `plugins/meow-flow/tests/test_record.py`: an
   approved epic and an approved open task, TSK-0001, whose numbered criteria
   are the ones the `Cover` fixtures call `CRITERIA`, with the Cover they call
   `FILLED`, and `tests/test_a_task.py` present.
2. Set its `Failing run` line to `README.md`, with `README.md` present in the
   repository, and run `paw ready implement TSK-0001`.
3. Set it to `evidence/run.txt`, with that file present and `evidence/` listed
   in `.gitignore`, and run the same command.

## What the system does

Both runs exit 0 and print
`paw ready implement: ready; TSK-0001 approved and complete`. `unkept` in
`crates/meow/src/record.rs` asks only whether the path is a regular file
inside the repository, so a page, a source file and a file git will never
commit all pass as the kept run.

## What it should do, and why

`ready implement` should exit 1, naming the path on its own line, where the
path under `Failing run` lies outside the evidence directory or where git
ignores it. ADR-1550 places kept evidence in that directory, `evidence_dir`
under `[verbs]` in `.meowpaw/profile.toml`, or `evidence` under the record
root where the profile declares none, and it holds that a file git won't
commit isn't kept for anyone else. REQ-3207 asks that the run is kept as the
cover step's evidence, and a file elsewhere, or one no clone receives, isn't.

The gate still doesn't read the file's content. Requiring the header
`meow-verbs evidence` writes would leave a repository that adopted
`meow-flow` alone unable to fill a Cover, which ADR-1270 rules out, and
whether the run failed is REQ-3206's question, which ADR-1620 leaves open. So
a hand-written file placed in the evidence directory still passes.

## Triage

It enters at implement, because REQ-3207 is right and BUG-1260's rule, a
regular file inside the repository, reads "kept" more loosely than ADR-1550
defines it. Major, because the gate that holds REQ-3207 lets an implementation
start with no kept run, and nothing after it notices.

## Closed by

The reproduction as fixtures in the class `CoverRun` in
`plugins/meow-flow/tests/test_record.py`: a failing run outside the evidence
directory and one git ignores, each refused naming the path, and a failing run
under the directory `[verbs] evidence_dir` declares, accepted.

## Tasks

- [x] T-001 TSK-2572 refuse a Failing run outside the evidence directory or
      ignored by git, in `crates/meow/src/record.rs`
      evidence: 3 checks seen failing first, 196 `meow-flow` fixtures
      passing, in #666.
