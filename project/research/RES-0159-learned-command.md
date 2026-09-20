---
id: RES-0159
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0018, RES-0060
---

# `/meow:learned`

## Summary

The development log records what turned out to be true without anybody
deciding it, which no other artifact in the method has a place for. Its unusual
design constraint is that the command must be easy not to run, because a model
asked what it learned will always produce something. It stays model-invocable
on an asymmetric argument: the model did the work and holds the numbers, and
someone who was not in the loop can ratify an insight but cannot recognise
one.

Writes a development log entry: a generalisable insight with the evidence that
produced it. One of five practice commands; its siblings are listed in
[RES-0060-practice.md](RES-0060-practice.md).

## Who has an equivalent

`vlie`'s development log is the precedent, and it is the only one in the survey
that records what turned out to be true without anybody deciding it.

That is the gap it fills. A decision record says what was chosen; a research
document says what was found before the work; neither has a place for _we
believed X, the numbers said Y, and here is why X looked right_.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The unusual design constraint: it must be easy not to run

A model asked to record what it learned will always produce something. That is
not a flaw in any particular model; it is what asking produces.

So the command's own instruction has to make **"nothing was learned in this
unit" a normal and frequent answer**, and an entry without evidence is not
written at all.

The consequence for the log is that its value is proportional to how often the
command declines. A log with an entry per task is a log nobody reads.

## Why it stays model-invocable, which was argued the other way first

The obvious safety move is `disable-model-invocation: true` - only a person may
record an insight. The argument against it is asymmetric and decides the
question.

The model is the party that did the work, followed the wrong hypotheses and
holds the numbers. A person who was not in the loop can **ratify** an insight
but cannot **recognise** one. Making the command user-only would mean the only
party who saw the evidence cannot record it.

The risk that argued for user-only is real, and it is answered where it belongs

- in the command's own instruction, above. Gating the command would be using a
  permission to fix a prompt.

## What an entry contains

- **The insight**, stated generally enough to apply to something else.
- **The evidence that produced it**, with numbers rather than impressions.
- **The hypotheses that were refuted, and why each looked right.** This is the
  part that makes the entry useful to someone who has the same wrong idea
  later, and it is the part omitted first.
- **The date**, because an insight about a tool has a shelf life.

It is immutable once written, for the same reason a decision record is: an
entry edited to match what was later believed is no longer evidence of what was
believed then.

## How it is read

Retrieved when a similar question arises, not loaded by default. A log loaded
into every session is a cost paid continuously for a benefit taken rarely,
which is the same argument that puts skill bodies behind progressive
disclosure.

## What it must refuse

To write on a schedule. The entry is written when something was learned, and a
periodic prompt produces entries about nothing.

To write an opinion. An entry without evidence is a note, and notes belong
elsewhere.

To write an insight that is true only of this repository, unless the entry says
so - the log is for the generalisable, and a repository-specific fact belongs
in the repository's own documentation.

## Conclusions

1. The log records what turned out to be true without anybody deciding it,
   which no other artifact in the method has a place for.
2. "Nothing was learned" is a normal and frequent outcome, and the
   command's instruction says so, because a model asked what it learned will
   always produce something.
3. An entry without evidence is not written.
4. The command stays available to the model, because the model did the work
   and holds the numbers, and a person who was not in the loop can ratify an
   insight but cannot recognise one.
5. The risk of over-recording is answered in the prompt rather than by a
   permission, since gating the command would be using a permission to fix a
   prompt.
6. An entry carries the refuted hypotheses and why each looked right, which
   is the part most useful later and the part omitted first.
7. An entry carries numbers rather than impressions, and a date, because an
   insight about a tool expires.
8. An entry is immutable once written, or it stops being evidence of what
   was believed at the time.
9. The log is retrieved when relevant rather than loaded by default.
10. Nothing is written on a schedule.

## Sources

All read 2026-09-20.

- `~/workspace/vlie/docs/dev/dev-log.md` - the development log this command
  writes into, entries carrying numbers, and the refuted-hypothesis rule.
- [RES-0018-dev-log.md](RES-0018-dev-log.md) - the judgement behind the log and
  what an entry owes.
- [Slash commands](https://code.claude.com/docs/en/slash-commands) -
  `disable-model-invocation` as the control considered and rejected for this
  command.
