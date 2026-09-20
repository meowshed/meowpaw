---
id: RES-0156
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0029, RES-0060
---

# `/meow:options`

## Summary

Laying out alternatives has one failure mode to design against: the straw-man
survey, which looks like diligence and functions as manufactured consent. The
countermeasures are built into how the survey is written, where exhortation
changes nothing. Each option is stated in its advocate's terms and names what
it is genuinely better at. Doing nothing is always present, and the
recommendation carries the condition that would flip it.

Lays out alternatives with trade-offs and a recommendation. One of five
practice commands; its siblings are listed in
[RES-0060-practice.md](RES-0060-practice.md).

## Who has an equivalent

harness4claude's `discuss`, which captures decisions as Locked, Deferred and
Discretion. That three-way classification is the part this command takes. Not
every outcome of a comparison is a decision, and recording which of the three a
result is stops a deferred question from being read later as settled.

## Method

We read the surveyed harnesses' own command templates and the internal
repositories' commands on 2026-09-20 for what a comparable command does. We
fetched the platform's command documentation for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## The failure to design against is the straw-man survey

Three options, two of them plainly weak, and the recommendation the model
wanted at the start. It has the shape of diligence and the function of
manufacturing consent, and it is what a comparison produces by default when the
comparer already has a preference.

The countermeasures are built into how the survey is written, where exhortation
changes nothing:

Each option is stated in the terms its advocate would use. A summary
written by someone who has already rejected an option is not the option.

Each option names what it is genuinely better at. This is the load-bearing
one, because it is falsifiable: a reader who knows the domain can contradict
it.

An option that is better at nothing is deleted, and never listed. Listing it is
padding the comparison to make the recommendation look chosen.

Doing nothing is always present and evaluated. It is the option with the
lowest cost and the one a comparison written to justify work never includes.

The recommendation carries the condition that would flip it. Without that
it is a preference; with it, it is a claim evidence can later contradict.

## Why an option's own advocate matters more here than elsewhere

The method already has an adversarial pass in the research step and a review
step afterwards. This command is different because the artifact _is_ the
comparison: there is no other content for a reviewer to check the
recommendation against.

So the honesty is built into how the survey is produced, because a review
catches none of it. That is why the rules above describe how each option is
written, and say nothing about what a reviewer should look for.

## The three outcomes

Adopting harness4claude's classification, a comparison ends in one of three
states and says which:

| Outcome    | Means                                                            |
| ---------- | ---------------------------------------------------------------- |
| Decided    | One option chosen, with the flipping condition recorded          |
| Deferred   | The comparison stands; the choice waits on something named       |
| Discretion | Any of the options is acceptable, and whoever implements chooses |

The third is underused and valuable: saying _this does not matter_ is a real
result, and recording it stops the same comparison being made again in six
months.

The second has a requirement attached: a deferral names what it waits on, or it
is an abandonment with better manners.

## What it must refuse

To produce a comparison with fewer than three options, since two options are a
preference with a foil.

To recommend without a flipping condition.

To write a decision record. This command informs a decision; recording one is
[RES-0158-decide-command.md](RES-0158-decide-command.md).

## Conclusions

1. Each option is stated in the terms its advocate would use, because a summary
   written by its opponent is not the option. 2. Each option names what it is
   genuinely better at, which is falsifiable by a reader who knows the domain. 3. An option that is better at nothing is deleted, since listing it pads the
   comparison to make the recommendation look chosen. 4. Doing nothing is
   always an option and is evaluated. 5. The recommendation carries the
   condition that would flip it, or it is a preference. 6. The outcome is
   classified as decided, deferred or discretion, and a deferral names what it
   waits on. 7. Discretion is a real result and is recorded, so the comparison
   is not repeated. 8. The command informs a decision and does not record one.

## Sources

All read 2026-09-20.

- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
  `discuss` capturing outcomes as Locked, Deferred and Discretion. -
  [RES-0029-research-technique.md](RES-0029-research-technique.md) - the
  adversarial pass and what makes a comparison settle something.
