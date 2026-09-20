---
id: RES-0157
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0029, RES-0060
---

# `/meow:grill`

## Summary

A red-team pass over a draft, run before implementation, where a missing edge
case costs a paragraph, and after implementation it costs a rewrite. It
produces findings against the artifact and never a rewrite of it, holding the
same read-only discipline as verification. Its hardest rule is that nothing
found is a valid result: a reviewer that must meet a quota will produce one,
and findings on a correct artifact train the reader to discount the review.

A red-team pass over a draft, aimed at the edge cases and failure paths nobody
wrote down, run before implementation. One of five practice commands; its
siblings are listed in [RES-0060-practice.md](RES-0060-practice.md).

## Who has an equivalent

harness4claude's `grill-me`, which is adversarial specification review. Nothing
else in the survey has a step whose purpose is to attack an artifact before it
is built from.

## Method

The surveyed harnesses' own command templates and the internal repositories'
commands were read on 2026-09-20 for what a comparable command does, and the
platform's command documentation was fetched for the frontmatter fields the
surface depends on.

Nothing was run. Nobody implemented or tested a command here, so every
statement about behaviour is a design claim measured against comparable
commands, and none of it is an observation.

## Why it is the highest value per token in the practice set

A missing edge case costs a paragraph at this point and a rewrite later. That
ratio is the entire argument, and it is why this command runs against a draft
and never against an implementation.

It is also the step with the least competition for attention: a specification
that reads well feels finished, and every other step in the chain asks whether
it is correct, where this one asks whether it is complete.

## What it produces

It produces **findings against the artifact**, not a rewrite of it. That is the
same read-only discipline verification has, and for the same reason: a reviewer
that edits has destroyed the thing it was reviewing and nobody can see what it
objected to.

A finding names the case, says what the artifact currently implies about it,
and says why that is wrong or unspecified. A finding that says only _consider
error handling_ has moved the work to somebody else and done none of it.

## The shape of the attack

The productive questions are about what the artifact does not say:

- **What happens when this is called twice**, or concurrently, or after it
  already failed.
- **What happens when the input is empty**, enormous, or from the wrong
  version.
- **Which failure states exist that the artifact does not name**, and what a
  reader is meant to do in each.
- **What is assumed about ordering** that nothing guarantees.
- **What the artifact would look like if the opposite decision had been taken**
  - the question that surfaces an assumption nobody stated.

The last one is the same mechanism as challenging assumptions before exploring
alternatives, applied after the fact.

## What it must refuse

To rewrite the artifact.

To manufacture findings. An adversarial pass that must produce a quota will
produce one, and a reviewer that returns findings on a correct artifact is
worse than useless, because it trains the reader to discount it. _Nothing
found_ is a valid and expected result.

To object to what the artifact says in favour of what the reviewer would have
written. A preference presented as a finding is the failure mode that makes
red-teaming unwelcome.

## Conclusions

1. It runs before implementation, because a missing edge case costs a paragraph
   before and a rewrite after. 2. It produces findings against the artifact and
   never a rewrite of it, holding the same read-only discipline as
   verification. 3. A finding names the case, what the artifact implies about
   it, and why that is wrong or unspecified, and it points at no topic. 4.
   Nothing found is a valid result, and no quota of findings is expected,
   because a reviewer that manufactures findings trains its reader to discount
   it. 5. A preference is not a finding, and an objection in favour of what the
   reviewer would have written is refused. 6. The questions are about what the
   artifact does not say: repetition, concurrency, failure after failure, empty
   and enormous input, unnamed failure states, assumed ordering, and the
   unstated assumption the opposite decision would expose.

## Sources

All read 2026-09-20.

- [Lharden/harness4claude](https://github.com/Lharden/harness4claude) -
  `grill-me` as adversarial specification review before implementation.
- [RES-0029-research-technique.md](RES-0029-research-technique.md) - the
  adversarial pass, and the rule against manufacturing findings.
- [RES-0030-review.md](RES-0030-review.md) - the read-only discipline a
  reviewing step holds.
