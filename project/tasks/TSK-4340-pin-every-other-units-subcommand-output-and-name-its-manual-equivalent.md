---
id: TSK-4340
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2330
closes: [REQ-1176, REQ-1184]
issue:
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

Not yet.

## Left alone

`paw`, which TSK-4330 covers. The output of a hook that answers the platform
in JSON keeps the platform's form, and the test pins its fields.
