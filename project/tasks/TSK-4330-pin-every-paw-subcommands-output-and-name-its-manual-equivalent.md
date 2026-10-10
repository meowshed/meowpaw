---
id: TSK-4330
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2330
closes: [REQ-1170, REQ-1174, REQ-1176, REQ-1182, REQ-1184]
issue: 940
projected: 319e3d61141a
tracked: 942224fd588d
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin every `paw` subcommand's output and name its manual equivalent in its help

Every `paw` subcommand states its kinds of output line and what a person reads
to get the same answer by hand, and a test holds each to both, as SPC-1080
states under "Each subcommand makes one determination". One task, one branch,
one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given the `record` feature's parser, when a test lists every `paw`
   subcommand and reads its help, then each help names what a person reads in
   its place, and a subcommand added with no such line fails the test
   (REQ-1176). Closed by: a crate test naming REQ-1176, seen failing first.
2. Given a fixture record, when a test runs each `paw` subcommand on it, then
   each output line opens with a first word the subcommand's help states, and
   a change to one line's first word fails the test (REQ-1184). Closed by: a
   crate test per subcommand naming REQ-1184.
3. Given each subcommand's output on the fixture, when a reviewer reads it,
   then no subcommand prints a next action as its own determination, such as
   "run X next", beside its answer (REQ-1174, REQ-1182). Closed by: judgement
   in the pull request's review, because no pattern tells a determination
   from a decision.
4. Given `plugins/meow-flow/bin/paw`, when the gate runs, then it is the
   launcher for the shipped `meow` binary and no other helper sits beside it
   (REQ-1170). Closed by: the `test` verb's run.

## What to do

Add to each `paw` subcommand's help one line naming the files a person reads
for the same answer, such as "read each task's `closes:` and each epic's
marks" for `check coverage`. Add, where it is missing, the first word of each
kind of line the subcommand prints, so the test has a stated form to pin.

`paw status` names the next step of a decision today, as `next: spec, then
epic`. Leave it, and state in its help that the line reports what the record
says comes next, because it is the chain's derived state and not a choice the
tool makes. Where a reviewer reads another line as a decision, split it or
reword it, and record the change as breaking in the commit.

Update `plugins/meow-flow/README.md` where it lists the subcommands.

## Depends on

Nothing.

## Evidence

The tests came first, in the pull request's first commit, where three of the
four in `crates/meow/tests/record_help.rs` failed because `paw --help` named
nothing. `every_subcommand_names_what_a_person_reads_in_its_place` closes
criterion 1 (REQ-1176): it reads each subcommand from `paw --help` and fails
one whose help has no `by hand:` line. Subcommands now dispatch through one
table that carries the three help fields, so one can't be added without them.
`read_only_output_opens_with_stated_first_words`,
`findings_drafts_and_refusals_open_with_stated_first_words`,
`successful_changes_open_with_stated_first_words` and
`an_index_with_an_amendment_opens_with_stated_first_words` close criterion 2
(REQ-1184): they run twelve of the thirteen subcommands on a fixture record,
with a finding, a draft, a miss, a refusal and a written change, and fail a
line whose first word the help's `lines:` doesn't state. A placeholder in
`lines:` is checked against the layout's kinds and relation keys, or a path,
and only the paragraph under `paw show`'s heading is free text. Removing
`Decisions` from `paw status`'s `lines:` made the test fail, as intended.
`onboarding` is run only on its refusal, because its writing path needs an
approved onboarding report no fixture here builds.
`the_unit_ships_the_launcher_and_no_other_helper` closes criterion 4
(REQ-1170): it holds `bin/` to the launcher alone and finds the shipped
binary's name in it, and it held before the change.

`cargo test --all-features`, `cargo clippy --all-features --all-targets
-- -D warnings`, `cargo fmt --check` and `mise run all` passed, each with exit
status 0.

Criterion 3 rests on judgement, because the line between reporting the
record's next step and choosing one is a reading of the output.

## Left alone

The other units' subcommands, which TSK-4340 holds to the same rules, and the
method's step files, which TSK-4350 changes.
