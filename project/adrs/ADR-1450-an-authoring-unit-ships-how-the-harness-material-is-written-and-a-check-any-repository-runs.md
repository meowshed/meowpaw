---
id: ADR-1450
artifact: adr
status: done
revised: 2026-09-27
addresses:
  [
    REQ-1110,
    REQ-1111,
    REQ-1112,
    REQ-1114,
    REQ-1116,
    REQ-1118,
    REQ-1120,
    REQ-1122,
    REQ-1124,
    REQ-1126,
    REQ-1128,
    REQ-1142,
    REQ-1672,
    REQ-1678,
    REQ-2680,
    REQ-2682,
    REQ-2684,
    REQ-2686,
    REQ-2688,
    REQ-2690,
    REQ-2692,
    REQ-2706,
    REQ-2708,
  ]
supersedes: []
---

# 1450. An authoring unit ships how the harness's own material is written, and a check any repository runs

## Decision

A new unit, `meow-author`, ships the capability for writing the harness's own
kind of material: skills and their supporting files, agent definitions,
output styles, and the prompts inside hooks (REQ-1672). It carries a skill
and a program, and a repository uses both on its own material, held to the
same rules, without that material becoming part of the harness (REQ-1678).

The skill, `meow-author:write`, loads before any of that material is written or
changed. Its rules carry everything SPC-1030 states about this material,
including what the program also checks:

- every unit carries front matter saying what it is for and when to load it
  (REQ-1110), and the harness has one kind of loadable unit, the skill, with a command being a skill only a person invokes, so a plugin ships no
  `commands/` directory (REQ-1111);
- the prompt uses the tag vocabulary SPC-1030 fixes, uses tags where it mixes
  kinds of content and not as decoration, and puts every obligation in a
  `<rules>` list item led by an identifier (REQ-1112, REQ-1114, REQ-1116,
  REQ-1118, REQ-1120, REQ-1128);
- a procedure states where it stops, and a judgement shows its failing case
  beside the corrected one (REQ-1122, REQ-1126);
- the core names each supporting file and when to read it, and addresses it
  through the platform's directory variable (REQ-1124, REQ-1142, REQ-2688);
- a skill with side effects is invoked only by a person, and knowledge only
  by the model; a skill for one language or directory declares its paths; a long
  read ending in a short answer runs in a forked context; material injected
  at load time is cheap, certain and runs no verb (REQ-2680, REQ-2682,
  REQ-2684, REQ-2686);
- every command is namespaced, the unit proposes the permissions it needs and
  leaves the repository to declare them, a script says whether it is run or
  read, and instructions use the vocabulary of the work they govern
  (REQ-2690, REQ-2692, REQ-2706, REQ-2708).

The program, `meow-author check [path...]`, is the `author` subcommand of
`meow`, the native tool ADR-1110 decides. With no path it reads every unit
under `plugins/`, and given a directory such as `.claude/`, it reads a
repository's own skills and agents. It fails, naming the file and the line, on:

- a Markdown heading, a tag outside the vocabulary, a tag opened inside
  another, a tag never closed or text outside every tag, as
  `tools/check_prompts.py` does today
  (REQ-1112, REQ-1114, REQ-1120, REQ-1128);
- a skill or agent with no `description` in its front matter (REQ-1110);
- a plugin shipping a `commands/` directory (REQ-1111);
- a file in a skill's directory that its `SKILL.md` never names (REQ-1124,
  REQ-1142);
- a path into the unit written without the directory variable (REQ-2688);
- a skill's core or an agent with a procedure and no step naming where it
  stops (REQ-1122).

The `prompts` task in this repository's `mise.toml`, which the `lint` verb
and `mise run all` run, calls `meow-author check` in place of
`tools/check_prompts.py`, which goes.

After this decision a repository writing its own skills gets the rules in front
of the model and a check that holds their form, and this repository's prompts
are checked by the shipped program. What still doesn't work: eleven rules rest
on the model and on review. Whether a skill has side effects, applies to one
directory, needs a fork, injects something cheap and certain, proposes its
permissions, says how a script is used or uses the work's vocabulary, whether
tags carry mixed content or decorate, and whether a judgement shows its failing
case, each needs a reader (REQ-1116, REQ-1118, REQ-1126, REQ-2680, REQ-2682,
REQ-2684, REQ-2686, REQ-2692, REQ-2706, REQ-2708). Namespacing needs no check,
because the platform prefixes every plugin skill with its plugin's name
(REQ-2690).

## Why

REQ-1672 asks the harness to ship what it uses to write itself, and today the
check lives in `tools/`, where no other repository gets it. A repository that
writes its own skills has the same problem this one had: a tag the next
author invents differently and a supporting file nothing names (RES-0004 on the
harness's own material, RES-0005 and RES-0201 on how a unit divides and
addresses it, RES-0202 on how it is worded). ADR-1110
puts every unit's program in the one native tool, so the check becomes its
`author` subcommand.

Ten of the rules are facts in a file a program can read, so the program holds
them (REQ-1172). The skill carries all of them in front of the model while it
writes, as ADR-1050 decided for the writing standard, so the ten are both
written right and checked.

The strongest objection: a program that reads any directory of skills will
report a repository's own conventions as findings. It reads `plugins/` or the
paths the repository gives it, and the vocabulary it holds is the one SPC-1030
states, which a repository adopts by running the check.

## Alternatives

| Option                                 | Better at        | Why it lost                                                                           |
| -------------------------------------- | ---------------- | ------------------------------------------------------------------------------------- |
| Do nothing                             | No unit to ship  | Only this repository gets the check, against REQ-1672                                 |
| Ship the Python scripts in a unit      | No port          | Every unit's program is the one native tool (ADR-1110), which needs nothing installed |
| Add the authoring rules to `meow-flow` | No new unit      | A repository writing skills with no record would install the method to get them       |
| The skill alone, no program            | Nothing to build | The form is mechanical, and a skill checks only the file the model has open           |

## What it costs

A new unit with a skill description in context on every turn where it is
installed, and a subcommand in the native tool. `meow-code:change`,
`meow-code:debug` and `meow-scm:commit` gain a stated stopping point, and this
repository's gate runs the shipped program.

## What would reverse it

I would reverse this if two repositories using the unit disabled its check
within a week of adopting it, because that would show the vocabulary is this
repository's taste and not a shared standard.

## Consequences

- `plugins/meow-author/` ships the skill, the launcher, a page and a budget.
- The native tool gains an `author` subcommand, and `tools/check_prompts.py`
  goes.
- SPC-1030 states the shipped check and the new rules.

## How I will know it was realised

1. `meow-author check` passes on this repository's units, and fixtures show
   it failing on each condition this decision lists.
2. `meow-author check .claude` runs on a repository's own skills, shown by a
   fixture holding a skill outside any unit.
3. The skill's rules carry each requirement ADR-1450 addresses, traced in the
   task's evidence, and the check passes on the skill.
4. The skill's description loads it before a skill is written in at least
   four of five sessions on each of Sonnet 5 and Opus 5.5, and on no more than
   one of five near misses that change code, as ADR-1050 measured.
5. Every requirement ADR-1450 addresses lands in exactly one closed task.

## What this does not settle

- The context cost of loadable material and how it loads, which a later
  decision on context cost settles.
- Measuring a prompt change, which SPC-1020 states.
