---
id: TSK-4340
artifact: task
status: done
revised: 2026-10-03
epic: EPC-2330
closes: [REQ-1176, REQ-1184]
issue: 941
projected: 5367a2361dce
tracked: 47399efda53d
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Pin every other unit's subcommand output and name its manual equivalent

Every subcommand of `meow` outside `paw` states its kinds of output line and
what a person reads to get the same answer by hand, and a test holds each to
both, as SPC-1080 states. One task, one branch, one pull request, one review:
the tests first, then the change, its documentation and its marks.

## Acceptance criteria

1. Given the crate's parser for each feature other than `record`, when a test
   lists every subcommand and reads its help, then each help names what a
   person reads in its place, and a subcommand added with no such line fails
   the test (REQ-1176). Closed by: a crate test naming REQ-1176, seen failing
   first.
2. Given each subcommand's existing fixtures, when a test runs it, then each
   output line opens with a first word its help states, and a change to one
   fails the test (REQ-1184). Closed by: a crate test per subcommand naming
   REQ-1184.

## What to do

Cover every subcommand the crate's features parse outside `record`, taking
the list from the parser and never from this task, because a list written here
goes stale when a unit adds one. A hook's guard counts: its manual equivalent
is the command a person runs to make the same check.

Update each unit's README where it lists its subcommands.

## Depends on

- TSK-4330 (not blocking): both add the same kind of test, and either can write its form first.

## Evidence

The tests came first, in a commit of their own, where all three in
`crates/meow/tests/unit_help.rs` failed because no unit answered `--help`. A
review of the first implementation found nine subcommands the test never ran,
tables that stated words nothing prints and omitted words something does, and
`by hand:` lines the source contradicted, and the tests and tables were
corrected in the same pull request.

`every_subcommand_names_what_a_person_reads_in_its_place` closes criterion 1
(REQ-1176): it reads each unit's subcommands from `<binary> --help`, fails one
whose help has no `by hand:` or `lines:` line, and fails a subcommand whose
name the string literals of the unit's `main` carry and `--help` doesn't list,
so the list comes from the parser's source and not from this task.
`output_opens_with_stated_first_words`,
`a_hook_answers_with_the_keys_its_help_states` and
`the_tracker_commands_refuse_with_stated_first_words` close criterion 2
(REQ-1184): between them they run all 34 subcommands on a fixture repository,
and fail a line whose first word the help doesn't state, or a JSON object with
a key it doesn't state. Removing `sign-off` from `meow scm check-message`'s
`lines:` made the first fail. `a_json_answer_has_the_fields_the_help_states`
holds `meow verbs status --json` to its keys. The lines a stage's own command
printed, between `-- whole output of` and `-- end of`, are the command's and
are skipped.

Two pins are weaker than a literal word: `<text>` stands for a task's name in
the `status` lines of `meow mise` and `meow gotask`, and for the ending word
that the deprecated whole-run subcommand of `meow loop` prints. `--help` is
the first argument after a name and nowhere else, so a target or a command
that is the word `--help` reaches the subcommand. The test reaches only what
the fixture produces: a refusal for `meow github` and for the tools that
aren't installed, and no success path that needs the code host.

`cargo test --all-features`, `cargo clippy --all-features --all-targets
-- -D warnings` and `mise run all` passed, each with exit status 0.

## Left alone

`paw`, which TSK-4330 covers. The output of a hook that answers the platform
in JSON keeps the platform's form, and the test pins its fields.
