---
id: RES-0018
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The development log

## Summary

One internal repository keeps a development log, and it is unlike what the
phrase usually means. Five entries over four months, each a claim-shaped title
with numeric evidence and the refuted hypotheses. It holds generalisable
insight and nothing else, because activity is in the history and decisions are
decision records. An entry is written when somebody learned something, and
never on a schedule, and its value is proportional to how often nothing is
written.

Research for a `dev-log` capability. `vlie` is the only one of the six internal
repositories that keeps one, it is unlike what the phrase usually means, and the
difference is the whole finding.

## Method

One internal log was read in full from its working tree on 2026-09-20 - 751
lines and five entries - which is a small sample and is why the observations
about entry frequency describe what this log does, and state no rule.

Published material on developer journals was fetched and read for the general
practice, and it turned out to describe a different artifact, which is itself
recorded as a finding.

Nothing was run. No claim here is measured; the numbers quoted are the ones the
log itself carries.

## What `vlie`'s log actually is

Its header, in full:

> Non-obvious architectural decisions. Scope changes and activity are in git
> history.

Seven hundred and fifty lines, entries dated but irregular: five in four
months, where a weekly log would hold sixteen. Each entry has a **title that
states a claim**, and never a date range:

- "The ItemTree firewall paid out twice in one day, in cash"
- "How to find a performance bottleneck (and how not to)"
- "the check-corpus harness, and three decisions worth recording"

And each entry has the same internal shape, arrived at without a template:

1. The claim, stated first. 2. The evidence, with numbers: "about 1%, and
   _faster_ on two of them", "bit-identical across five runs", "97 MB to 14,095
   MB". 3. The refuted hypotheses, named - three wrong diagnoses recorded
   alongside the right one, each with why it looked correct. 4. The pattern to
   carry, generalised beyond the case.

That fourth part is what distinguishes it from everything else in the
repository. One entry ends: "a firewall that stops invalidation from
propagating also makes conservative comparisons cheap downstream of it. Being
able to afford a pessimistic-but-correct `PartialEq` is a dividend of the
firewall, and no independent piece of luck."

That sentence is no decision, no requirement and no change. It has nowhere else
to live.

## What the usual advice says, and why it is the wrong artifact

The developer-journal literature describes something else entirely: update
"roughly hourly or about 5-6 times a day"; record daily goals, errors,
assumptions, code snippets; keep the unpolished details; compare what you meant
to do with what you did.

That is a **personal activity journal**, and it is a fine thing that does not
belong in a shared repository. Three reasons it fails as a project artifact:

- **It duplicates git.** "What I worked on today" is what the history is for,
  and the history is more accurate.
- **Nobody reads it.** An hourly log has a signal-to-noise ratio that makes
  retrieval worthless, which is the same abandonment failure
  [RES-0017-design-lenses.md](RES-0017-design-lenses.md) describes.
- **It is written for the author.** A project artifact is read by someone who
  was not there.

`vlie`'s header is a direct rejection of this: activity is in git, and the log
holds only what git cannot.

## Where it fits among the artifacts that already exist

The harness already has several places to write things down, and a new one has
to justify itself against all of them.

| Artifact            | Holds                                                             | Written when                                                 |
| ------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ |
| Commit message      | What changed, and why this change                                 | Per change                                                   |
| Plan task entry     | What closed a task, and its evidence                              | Per task                                                     |
| Decision record     | A project-wide decision, its alternatives, its reversal condition | When a decision is made                                      |
| Requirement         | An obligation                                                     | When behaviour is specified                                  |
| Design document     | Why the system is shaped this way                                 | Per unit of work                                             |
| Review report       | Findings and a verdict                                            | Per unit of work                                             |
| **Development log** | **A generalisable insight with the evidence that produced it**    | **When something turned out to be true that nobody decided** |

The gap is real and specific. A decision record answers "what did we choose and
why"; it has an author, a moment, and alternatives. The log entries above have
none of those - nobody chose that a firewall makes downstream comparisons
cheap. It was _discovered_, with numbers, and it changes how the next design is
approached.

The literature's summary - ADRs for architectural decisions, the decision log as
their index, commit history for implementation detail, changelogs for
user-facing changes - has no slot for a discovered generalisation either. That
is the slot.

## The strongest pattern in it: record the refuted hypotheses

One entry lists three wrong diagnoses before the right one, each with the
aggregate it came from and the measurement that killed it: "Each hypothesis was
the honest reading of its aggregate. Each was underdetermined, and looked
determined."

This is what blameless postmortem practice does for incidents, applied to
ordinary engineering. The SRE framing - assume everyone acted on the best
information available at the time, and dig past human error to systemic
contributors - is what makes it writable at all. Recording your own wrong turns
requires that being wrong is not the finding.

And it is the highest-value content, because a refuted hypothesis is the thing
most likely to be re-proposed. The right answer will be visible in the code; the
three wrong ones will not be visible anywhere.

## The predicted-number rule

From the same entry, and it becomes a rule of its own:

> Record the predicted number _before_ the fix, so that landing x2 reads as
> "worked as designed" rather than "half worked", and landing x15 reads as "the
> model is wrong, look again".

This is falsifiability applied to optimisation work. Without the prediction, any
outcome is rationalised after the fact and nothing is learned. With it, both a
hit and a miss are informative - and a large overshoot is a signal that the
model of the system is wrong, which is the more valuable of the two.

It pairs with a decision's reversal condition: both turn a judgement into
something evidence can contradict.

## Frequency, and the failure to avoid

Five entries in four months. The log is written **when something is learned**,
not on a schedule.

A scheduled log fills with ceremony, and ceremony is what stops anyone reading
it - the same mechanism as a mandatory commit body producing ceremonial
paragraphs ([RES-0014-commits.md](RES-0014-commits.md)), and the same as a template section that
must be filled producing invented content ([RES-0012-catalogues.md](RES-0012-catalogues.md)).

For an agent the risk is sharper, because a model asked to write a log entry
will always produce one. The obligation has to be conditional on there being
something to record, and "nothing was learned in this unit of work" has to be an
acceptable and common outcome.

## What it costs, and the honest objection

A log nobody reads is pure cost, and this one is 750 lines of dense prose that
no command loads. Two things keep it earning its place anyway:

- It is **retrieved and never loaded**: searched when a similar question
  arises, which is `meow-memory`'s job and exactly what an index is for
  ([RES-0026-memory.md](RES-0026-memory.md)). - Its entries are the raw
  material for everything else. A generalisation that recurs becomes a design
  principle; one that constrains behaviour becomes a requirement; one that
  settles a choice becomes a decision record. The log is where a thought lives
  before it has earned a stronger home.

The objection: this is the artifact most likely to decay into a diary. The
defences are the header (`vlie`'s one-line scope statement does real work), the
conditional obligation, and the requirement that an entry carry evidence - a
diary entry cannot.

## Conclusions

1. It holds generalisable insight with its evidence, and nothing else. Activity
   is in git; decisions are decision records. 2. An entry is written when
   something is learned, never on a schedule, and "nothing was learned" is a
   normal outcome. 3. The title states the claim, and never the date or the
   topic. 4. An entry carries numbers or a reproducible observation. Without
   evidence it is an opinion, and opinions belong in the design. 5. Refuted
   hypotheses are recorded, with why each looked right. 6. A prediction is
   recorded before the work that tests it. 7. The entry ends with the pattern
   to carry, generalised past the case. 8. Entries are immutable, like decision
   records - a later entry supersedes an earlier one and edits nothing. 9. It
   is retrieved on demand, and never loaded by default.

## Sources

- `~/workspace/vlie/docs/dev/dev-log.md`, read 2026-09-20 - 751 lines, five
  entries over four months; its scope line, the claim-shaped titles, the
  numeric evidence, the three refuted hypotheses, and the predicted-number rule.
- [Keep journals to become a better developer](https://dbader.org/blog/keep-journals-to-become-a-better-developer),
  [What is a developer log?](https://dailydevpost.com/blog/what-is-a-developer-log)
  and [What is a developer journal?](https://opensource.com/article/19/4/what-developer-journal),
  read 2026-09-20 - the personal-activity-journal advice this document rejects
  as the wrong artifact for a shared repository, including the hourly-update
  recommendation.
- [Postmortem culture: learning from failure](https://sre.google/sre-book/postmortem-culture/)
  and [Postmortem practices for incident management](https://sre.google/workbook/postmortem-culture/),
  Google SRE, read 2026-09-20 - blameless as "everyone acted on the best
  information available at the time", and digging past human error to systemic
  contributors.
- [SRE incident post-mortem best practices](https://incident.io/blog/sre-incident-postmortem-best-practices),
  read 2026-09-20 - contributing factors framed as systemic causes, and
  recording what went well.
- [Architectural Decision Records](https://adr.github.io/), read 2026-09-20 -
  for the boundary between a decision record and this artifact.
