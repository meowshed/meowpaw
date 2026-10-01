---
id: BUG-1390
artifact: bug
status: draft
severity: minor
violates: REQ-1240
enters: spec
found: 2026-10-01
revised: 2026-10-01
issue:
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# SPC-1201 leaves five failure states of a run unnamed

SPC-1201's "Failure paths" names no state for five things `meow-loop` 0.7.0
does when a run starts or reads the record. A person who meets one of them
can't look its line up, and an implementer has no stated behaviour to build
to.

## Reproduction

`meow-loop` 0.7.0 at the commit that merges TSK-3410. Read SPC-1201's
"Failure paths" and its paragraph on failures after start, then compare them
with `ready` and `evaluate` in `crates/meow/src/runloop.rs`. Of the five
states, the first is checked by `Step.test_spec_run_over_no_requirement_never_finishes`,
and the other four need a broken profile, layout or git, which no check sets
up.

## What the system does

- An input of the wrong kind for its step, such as a requirement given to
  `epic`, passes start, because the readiness test `paw ready` applies checks
  that an input is approved and not its kind. The step's test then never
  holds, and the run spends its ceiling and budget.
- A failed `git check-ignore` refuses the start as
  `unresolved: can't check whether record root <path> is ignored by git: <error>`,
  a line the table doesn't list.
- A profile that can't be read refuses the start as
  `unresolved: the profile can't be read: <reason>`, a line the table doesn't
  list.
- A layout that can't be read refuses the start as
  `unresolved: <layout path>: <error>`, a line the table doesn't list.
- A layout that can't be read during a run stops it with exit status 3 and
  no ending, which the paragraph on failures after start doesn't name.

`--inputs` with no identifier in it, such as `" , "`, is reported as
`usage: --step <step> needs --inputs`, as if the flag were absent. The table
says only "`--inputs` absent", so it should say whether an empty list counts
as absent.

## What it should do, and why

SPC-1201 names each of these states with the line it prints and its exit
status, because REQ-1240 asks a design to name every failure state the system
can reach. An input of the wrong kind should be refused at start, with its
own line, because a run that can never finish spends money that tells the
person nothing.

## Triage

It enters at spec, because the requirement is right and the specification
leaves these states out; the refusal of a wrong-kind input then needs a task
of its own. Minor, because each state either prints a reason or ends at the
ceiling and budget the person set.

## Closed by

Not yet.
