---
id: RES-0051
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# `/meow:amend`

## Summary

Work sometimes contradicts an approved artifact, and without a command for
it the contradiction is resolved by quietly rewording the artifact to match
what was built. The command states the contradiction with its identifier and
evidence, escalates when the cause lives in a higher artifact, checks the
oracle before blaming the artifact, reports the blast radius, and tombstones
and reallocates rather than rewording in place. It stops for approval as its
own reviewable change.

Proposes a change to an approved artifact after work contradicted it.

## Who has an equivalent

Only `meowctl`, as `/amend-spec`. Nobody else in the survey has a command for
this at all.

That absence is telling, because the situation it handles is universal:
implementation discovers the specification is wrong. Without a command, the
resolution is whatever happens in the moment - and what happens in the moment is
that the specification gets reworded to match what was built.

## Method

We fetched and read the surveyed harnesses' own command templates on
2026-09-20, because the mechanisms live in the templates and the readmes only
describe them, alongside the internal repositories' commands read from their
working trees.

The platform's documentation on commands was fetched for the frontmatter
fields the surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against what comparable
commands do.

## Why it exists

From `meowctl`'s skill: "The spec stops being trustworthy the first time that is
allowed, and an untrustworthy spec is worse than none because people still cite
it."

And the step people skip, named: "a requirement is quietly reworded to match
what was built, the reasoning behind the original is lost, and six months later
the same mistake is made again because the record of why it was a mistake is
gone."

The command exists so that rewording is **an event with a diff** rather than an
edit.

## What it does

`meowctl`'s six steps, which transplant unchanged:

1. State the contradiction precisely - the identifier, what it demands, what
   the implementation found, and why it cannot hold as written. "It was awkward"
   is not a contradiction.
2. Check the authority above it. If the requirement follows from a design
   decision, this is a design change and needs a bigger conversation. Say so and
   stop.
3. Check the oracle before blaming the artifact. Where there is something
   the requirement describes - an existing implementation, a format, a parity
   target - read it. Often the implementation is wrong, not the requirement.
4. Measure the blast radius - other requirements depending on this one,
   checks referencing it, code already merged against it, work in flight citing
   it.
5. Draft the replacement. Withdraw the old identifier, allocate a new one,
   leave a tombstone. Never reword in place.
6. Write the migration for anything already built: what changes, who does
   it, and whether it blocks the amendment or follows it.

Then stop. "Do not apply it and continue implementing in the same breath; the
approval is the point."

## The one thing to add

`meowctl`'s command is about specifications. Ours applies to any approved
artifact - requirements, design, plan - and the step-two check generalises: an
amendment to a lower artifact that follows from a higher one is a change to the
higher one, and the command says so and stops rather than papering over it.

## Conclusions

1. State the contradiction with the identifier and the evidence.
2. Escalate when the cause lives in a higher artifact.
3. Check the oracle before blaming the artifact.
4. Report the blast radius.
5. Tombstone and reallocate; never reword in place.
6. Write the migration.
7. Stop for approval as its own reviewable change.

## Sources

All read 2026-09-20.

- `~/workspace/meowctl/.claude/commands/amend-spec.md` - the six steps, the
  escalation when the cause is architectural, checking the oracle before blaming
  the specification, the blast radius, the tombstone-and-reallocate rule, the
  migration, and the instruction not to apply and continue in the same breath.
- `~/workspace/meowctl/.claude/skills/spec-driven/SKILL.md` - the divergence
  protocol and the failure it prevents.
- No other harness in the survey has an equivalent command; that absence is
  itself the finding.
