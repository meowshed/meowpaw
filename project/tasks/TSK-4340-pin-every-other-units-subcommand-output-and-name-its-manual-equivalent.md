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
`crates/meow/tests/unit_help.rs` failed because no unit answered `--help`.
`every_subcommand_names_what_a_person_reads_in_its_place` closes criterion 1
(REQ-1176): it reads each unit's subcommands from `meow <unit> --help`, fails
one whose help has no `by hand:` or `lines:` line, and fails a subcommand the
unit's usage line accepts and `--help` doesn't list, so the list comes from the
parser and not from this task. `output_opens_with_stated_first_words` closes
criterion 2 (REQ-1184): it runs 34 of the 35 subcommand forms on a fixture
repository, skips the lines a stage's own command printed, and fails a line
whose first word the help doesn't state; removing `summary:` from
`meow verbs run`'s `lines:` made it fail. `a_json_answer_has_the_fields_the_help_states`
holds the one JSON answer, `meow verbs status --json`, to the keys its help
states. The hook guards answer with an exit status and text on standard error,
and their standard output is empty on the fixture, so the test pins no JSON
field there. Placeholders in `lines:` are weaker than a literal word:
`<text>` accepts any word, and the units that print a tool's text, `author`,
`licence`, `mise`, `gotask`, `markdown` and `github`, state it.
`mise run all` passed with exit status 0.

## Left alone

`paw`, which TSK-4330 covers. The output of a hook that answers the platform
in JSON keeps the platform's form, and the test pins its fields.
