---
id: TSK-4920
artifact: task
status: approved
revised: 2026-10-03
epic: EPC-2525
closes: [REQ-1430, REQ-1432]
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# Fail a tool no step is named for

`meow-author check` fails an agent's tool, or a tool in a skill's
`allowed-tools`, whose unit's README names no step beside it, and every unit
this repository ships names the step for each tool it grants, as SPC-1030
states under "What a unit declares" and "The check". One task, one branch,
one pull request, one review: the tests first, then the change, its
documentation and its marks.

## Acceptance criteria

1. Given a fixture unit whose agent lists `Read, Grep` and whose README names
   a step beside `Read` only, when `meow-author check` runs, then it exits 1
   naming the unit, `Grep` and the agent (REQ-1432). Closed by: a crate test
   naming REQ-1432, seen failing first.
2. Given a fixture skill with `allowed-tools: Bash` and no step named for
   `Bash` in its unit's README, when the check runs, then it fails naming the
   skill (REQ-1430, REQ-1432). Closed by: a crate test.
3. Given this repository's `plugins/`, when the check runs in the gate, then
   it passes, because each README names the step for each tool its agents and
   skills grant (REQ-1430). Closed by: the gate's `lint` verb.

## What to do

Add the rule to the `author` feature of `crates/meow/`, reading the README's
permissions section, where REQ-2692 already has a unit propose its
permissions, for a line naming the tool and a step. Choose the line's form,
state it on `plugins/meow-author/README.md` and in
`plugins/meow-author/skills/write/`, and write it into every unit's README.
Remove a tool no step needs rather than inventing a step for it.

## Depends on

Nothing.

## Evidence

Not yet.

## Left alone

A repository's own agents and skills, which the check reads only when a
person passes their paths, and the platform's permission prompts, which the
repository declares.
