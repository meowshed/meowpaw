---
id: ADR-1520
artifact: adr
status: approved
revised: 2026-09-27
addresses: [REQ-0140, REQ-0142]
supersedes: []
---

# 1520. A verb runs over part of the work only through a form the repository declares

## Decision

A repository may declare, for any verb, the command that runs it over part of
the work, with a `{targets}` placeholder where the part goes:

```toml
[verbs]
lint = "./scripts/lint"

[verbs.test]
command = "./scripts/test"
subset = "./scripts/test {targets}"
```

A verb's value is either a string, the command for the whole work, or a
table with `command` and an optional `subset`, so every profile written today
keeps its meaning.

`meow-verbs run <verb>... -- <target>...` runs each named verb over the
targets, such as a test name, a file or a directory (REQ-0140). The program
quotes each target for the shell and puts them, separated by spaces, where
`{targets}` stands, so a target holding a space or a shell character reaches
the tool as one argument and is never read as shell syntax. The program
replaces every `{targets}` in the form and nothing else, so an author who puts
the placeholder inside quotes gets the quoted targets inside those quotes, and
writes the form accordingly. A `--` naming no
target is a usage error, because it could mean either the whole work or
nothing, and the program guesses neither. A `subset` without `{targets}` is a
`malformed declaration`, the kind that already names a value the program can't
use, because it would run the whole work under the part's name.

Where a verb declares no `subset`, `run` with targets reports that verb as
unresolved of the kind `no subset form` and doesn't run it (REQ-0142). Each
other named verb runs over the targets as usual, as `run` already treats an
unresolved verb beside resolved ones, and the program exits 1 where one
failed and 3 where none failed and one was unresolved. It never
runs the whole command in its place, because a whole run reported under a
subset's name tells the reader something narrower passed than did, and a
whole run nobody asked for can take far longer than the part.

A record from a subset run carries its targets, and `meow-verbs evidence` never
counts it as current for the whole verb, as ADR-1480 decided: `evidence test`
reads the latest record run without targets, and prints the latest subset
record beside it as `subset only`. `status` shows each verb's subset form, or
that it has none, so the model can see which verbs run over a part before it
asks.

The `verify` skill runs a subset through `run <verb> -- <targets>`. Where the
program reports `no subset form`, the skill says so and asks the person
whether to declare the form or run the whole verb, and runs the whole verb only
when the person says to, reporting it as the whole verb. It never runs a
tool's own command in its place.

After this decision the model can run one test or one file through the
repository's own declaration, and a verb that can't run over a part says so.
What still doesn't work: the program doesn't check that a declared form really
narrows the run, and it has no way to know which targets a tool accepts.

## Why

REQ-0140 asks for a verb over a part of the work where the underlying tool
supports one, and REQ-0142 asks the harness to say so where it doesn't, never
running the whole and calling it the part. Only the repository knows how its
tool takes a part, just as only it knows the whole command, which is why
ADR-1070 resolves a verb from the profile alone and REQ-0158 forbids guessing a
command. A declared form carries that rule over to a part of the work.

A placeholder, and not arguments appended at the end, lets a form put the
targets anywhere a tool needs them, such as before a flag that must come last.

The strongest objection: every repository has to declare a second command for
every verb it wants to run over a part. It does, once, and the alternative is
the harness guessing a tool's argument syntax, which is the failure REQ-0158
exists to stop.

## Alternatives

| Option                                      | Better at                           | Why it lost                                                                                                             |
| ------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                  | No change                           | The model runs a tool's own command to test one file, outside the verbs, and REQ-0140 and REQ-0142 stay unmet           |
| Append the targets to the whole command     | Needs no second declaration         | Works only for a tool that takes targets last, and runs the whole work for one that ignores them while reporting a part |
| Let a language pack supply the subset form  | No declaration for common tools     | Packs don't exist yet, and a pack's guess still has to be overridable by the repository, which this form already is     |
| Run the whole verb when no form is declared | The person gets a result either way | A whole run reported as the part is what REQ-0142 forbids                                                               |

## What it costs

`meow-verbs` gains a table form for a verb, a `--` on `run`, and one more kind
of unresolved verb. A repository that wants a part run declares one more line
per verb, which its maintainers write. Until a repository declares a form, the
model can no longer run a tool's own command over one test: it stops and asks
the person, every time, which that person pays for in interruptions, and which
lands on every repository on the day this ships. The ledger carries each
record's targets, and a record written before this decision, which has none,
reads as a whole run, which it was.

## What would reverse it

I would drop the declared form if repositories didn't declare it and people
kept being asked instead of a part being run, counted over the next ten
repositories to adopt the harness, because then the rule only moves the
guessing to the person. Separately, I would let a language pack supply a
default form, overridable by the profile, once packs exist.

## Consequences

- `meow-verbs` reads a verb's table form, runs `run <verb> -- <targets>`
  through `subset`, reports `no subset form` otherwise, and records targets.
- `meow-verbs evidence` ignores subset records for the whole verb, and
  `status` shows each subset form.
- The `verify` skill runs a part through the program and never around it.
- SPC-1040 states the form, the kind and the evidence rule.

## How I will know it was realised

1. Fixtures show a declared subset form run with two targets, quoted, in place
   of `{targets}`; a verb with no subset form reported as `no subset form`,
   with nothing run and exit 3; a string value still resolving as before; and
   `--` with no target refused; a `subset` without `{targets}` reported as a
   malformed declaration; a run naming a verb with a form and one without
   running the first, reporting the second and exiting 3; and `status` showing
   each verb's subset form or its absence.
2. A fixture shows `evidence test` ignoring a later subset record, printing it
   as `subset only`, and reporting the whole run's record.
3. The `verify` skill carries the subset rule, traced in the task's evidence,
   and `meow-author check` passes on it.
4. Every requirement ADR-1520 addresses lands in exactly one closed task.

## What this does not settle

- A subset form a language pack supplies.
- Checking that a declared form narrows the run.
- Asking `evidence` about one set of targets; a subset result is cited as
  `evidence` prints it beside the whole verb's, with its targets.
