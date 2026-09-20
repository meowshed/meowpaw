---
id: RES-0222
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0014, RES-0065
---

# The `branching` skill

## Summary

Work happens on short-lived branches off a single trunk, and the stated
problem with the alternative is merge conflict and a broken build. For a
harness the argument is sharper: an agent on a long-running branch accumulates
divergence it cannot see, and the review that would catch it arrives after the
divergence is expensive. Branch size is bounded by review effectiveness rather
than by a duration, and two agents never share a branch.

Research for one source-control convention: what branches exist, how long they
live, and what may be committed where.

Its siblings are
[RES-0221-conventional-commits.md](RES-0221-conventional-commits.md),
[RES-0223-pull-requests.md](RES-0223-pull-requests.md) and
[RES-0224-attribution.md](RES-0224-attribution.md).

## Method

The published model was fetched and read on 2026-09-20 for its definition
and for the stated problems with long-lived branches.

The size rule is not from that source: it comes from the inspection finding
recorded in this corpus's verification research, applied to branches rather
than to proposals.

The version-control constraint that two worktrees cannot hold one branch comes
from this corpus's tool research. Nothing was run.

## The model, and why nothing else is offered

Trunk-based development is _"a source-control branching model, where developers
collaborate on code in a single branch called 'trunk' and resist any pressure
to create other long-lived development branches."_

Temporary branches are permitted and are for one purpose: review and
integration checks, before merging back. The stated problem with the
alternative is direct - long-lived feature branches create _"merge hell"_ and
risk breaking the build.

For a harness this model is not a preference. An agent working on a
long-running branch accumulates divergence it cannot see, and the review that
would catch it arrives after the divergence is expensive.

## Never a direct commit to a protected branch

The rule is absolute in this method, and the reason is about evidence rather
than process: a change that never existed as a proposal was never reviewed, and
nothing in the history distinguishes it from one that was.

It applies to the harness with more force than to a person, because the harness
can produce a correct-looking change quickly and repeatedly.

## Branch names carry the identifier, and that is the durable link

Where a tracker is in use, the branch name carries the work item's identifier.
That is the link that survives a title edit, a description rewrite and a
squash - which is why it beats every other linking mechanism even where those
exist.

The name is otherwise short and descriptive. A name that encodes a date, an
author or a ticket system's internal number is carrying something the forge
already knows.

## Review capacity bounds a branch's lifetime

The published guidance gives no fixed duration, and a fixed duration is the
wrong instrument anyway. The binding constraint is that a person's review
effectiveness falls with the size of what is in front of them - a finding this
project already holds from the inspection literature.

So the rule that follows is about size: a branch is finished when it contains
one reviewable change, and a branch that has grown past that is split rather
than extended. That is the same constraint that produces stacked pull requests,
approached from the branch, where the stacked-pull-request research approaches
it from the proposal.

## Where several branches are in flight at once

A harness working in parallel has several branches simultaneously, which is
where the version control tool's constraints become design constraints.

git refuses to check out the same branch in two worktrees, so parallel work
creates a branch per worktree and shares none. Jujutsu's workspaces have an
explicit stale state instead. Either way, **two agents never share a branch**,
and the isolation holds at the branch level, where the directory level isolates
nothing, because worktrees share refs and objects.

## What it must refuse

A commit directly to a protected branch.

A branch that outlives its review, which is split instead.

A branch name that encodes what the forge already stores.

A merge that rewrites history somebody has already reviewed without saying so,
since a force-push over a reviewed branch removes the evidence of what was
reviewed.

## Conclusions

1. Work happens on short-lived branches off a single trunk, because long-lived
   branches accumulate divergence nobody sees until it is expensive. 2. A
   branch exists for review and integration checks, and it merges back, so
   nobody maintains it. 3. Never a direct commit to a protected branch, since a
   change that was never a proposal was never reviewed and the history cannot
   tell the difference. 4. A branch name carries the work item's identifier
   where a tracker is in use, because that link survives edits and squashes. 5.
   A branch name carries nothing the forge already stores. 6. Branch size is
   bounded by review effectiveness, so a branch that has grown past one
   reviewable change is split, and never extended. 7. Two agents never share a
   branch, and parallel work creates one branch per worktree. 8. A force-push
   over a reviewed branch is disclosed, because it removes the evidence of what
   was reviewed.

## Sources

All read 2026-09-20.

- [Trunk-based development](https://trunkbaseddevelopment.com/) - collaboration
  on a single trunk with resistance to long-lived development branches;
  short-lived branches for review and integration checks; feature flags and
  branch by abstraction at scale; and merge hell and build breakage as the
  stated problems with long-lived feature branches. -
  [RES-0065-stacked-pull-requests.md](RES-0065-stacked-pull-requests.md) - the
  size constraint approached from the proposal, where this document approaches
  it from the branch. - [RES-0131-git.md](RES-0131-git.md) - that git refuses
  the same branch in two worktrees and that worktrees share refs and objects. -
  [RES-0014-commits.md](RES-0014-commits.md) - the method's branching rules and
  the prohibition on direct commits to a protected branch.
