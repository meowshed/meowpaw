---
id: ADR-2400
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-1170,
    REQ-1172,
    REQ-1174,
    REQ-1176,
    REQ-1178,
    REQ-1180,
    REQ-1182,
    REQ-1184,
    REQ-1190,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2400. The native tool is the harness's helper, and each subcommand makes one determination

## Decision

The `meow` native tool that ADR-1110 put behind every unit's `bin/` is the
helper REQ-1170 asks for, and I add no second helper beside it. Each
subcommand makes one determination, such as `paw check coverage` or
`paw ready <step>`, and reports it without deciding what to do next
(REQ-1174, REQ-1182). A step that would otherwise count, diff, match or
resolve by reading files calls the subcommand that computes it (REQ-1172).

Every subcommand's output is a contract. It is line-oriented text with a
stated first word per line, the same today as in the next release unless
the change is marked breaking (REQ-1184). A step that cites a subcommand's
output as evidence cites the command, its exit status, its output and the
tree revision it ran at (REQ-1178). Where the output contradicts what the
step can see in the tree, the step says so and doesn't defer to the tool
(REQ-1180).

A subcommand makes work cheaper and never possible: each one states in its
help what a person would read to get the same answer, so the method still
runs by hand where the tool is missing (REQ-1176). Where the platform can run
a subcommand before the model reads, through a hook such as the
`SessionStart` one in `plugins/meow-flow/hooks/hooks.json`, the unit uses the
hook and doesn't spend a turn on it (REQ-1190).

Once this is accepted, the rules for a helper are stated for the one tool the
harness ships, and a test can hold each subcommand to them. What still
doesn't work: no subcommand offers a machine-readable format beyond its text
lines, and REQ-1188 is left open (see the last section).

## Why

RES-0023 found that a model reading files to count or diff spends turns and
gets the count wrong, and that a helper which decides as well as computes
takes the judgement away from the step that owns it. ADR-1110 already ships
one compiled tool to every unit, so a second helper language would add an
install step and a second contract to keep. RES-0019 and RES-0025 found that
tooling over the record pays only when the method still works without it.

## Alternatives

| Option                           | Better at                               | Why it lost                                                               |
| -------------------------------- | --------------------------------------- | ------------------------------------------------------------------------- |
| Do nothing                       | No work                                 | Nine requirements stay open, and no test holds a subcommand to one answer |
| A JSON mode for every subcommand | A program can parse every answer        | No consumer needs it yet, and two output forms double the contract        |
| Helpers as scripts per unit      | A unit's author can change one in place | It brings back the per-unit install step ADR-1110 removed                 |

## What it costs

Each subcommand needs a test that pins its output lines, and a change to a
line becomes a release decision. A subcommand that grows a second answer has
to be split, which costs a new name.

## What would reverse it

- A consumer outside the harness needs to parse a subcommand's answer and the
  text lines can't carry it, which would argue for a structured format.

## Consequences

The crate gains a test per subcommand that pins its first words. Each
subcommand's help names what a person would read in its place. The method's
step files say which subcommand computes which determination.

## How I will know it was realised

1. A test lists every `paw` subcommand and fails for one whose help doesn't
   name the manual equivalent (REQ-1176).
2. A test per subcommand pins its output lines, and changing one fails it
   (REQ-1184).
3. The step files cite a subcommand for each count, coverage, staleness and
   resolution they need, and a check finds no step that asks the model to
   count by reading (REQ-1172).

## What this does not settle

- REQ-1188, which asks for helpers in the language the platform installs
  dependencies for. ADR-1110 chose one compiled tool, so the two disagree and
  a later decision has to withdraw one of them.
- A structured output format.
