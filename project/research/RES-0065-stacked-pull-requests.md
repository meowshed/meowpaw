---
id: RES-0065
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# Stacked pull requests

## Summary

When the tasks of one epic depend on each other, one task becomes one proposal
in a dependency-ordered series. That series carries three obligations a single
proposal does not: each states its base, the base is read back after any change
to it, and only the bottom merges first. The sharpest finding is that a check
against a previous base is not evidence - it is green, it is labelled passing,
and it ran against a tree that no longer exists.

Research for what happens when the tasks of one epic depend on each other. The
method already says a task is one branch, one pull request and one review, and
that a task names the tasks it depends on. Those two together produce a stack,
and nothing in the method says so or says what to do about it.

It covers where the practice came from and what the platform now provides. It
also covers the failure modes the documentation names, which nobody here
imagined, and what a harness has to do to work a stack without lying about its
state. It does not cover how an epic is decomposed, which is
[RES-0055-epic.md](RES-0055-epic.md), nor how work items are filed, which is
[RES-0022-forge.md](RES-0022-forge.md).

## The question

An epic decomposes into tasks with dependencies between them. Each task lands as
one pull request. A task whose dependency has not merged therefore has nowhere
to point except at its dependency's branch, and the result is a chain of pull
requests whose bases are each other.

The alternatives are worse, and the research names them first. Wait for each
dependency to merge before opening the next review, which serialises an epic
into as many review cycles as it has tasks. Or fold dependent tasks into one
pull request, which produces the large diff the decomposition existed to avoid.

So the question is not whether to stack. It is what the harness must do so that
a stack is not a source of confident false claims about what is reviewed,
merged or checked.

## Method

The published material on stacked proposals and the tools that manage them
was fetched and read on 2026-09-20, along with the platform's documentation on
how a base branch behaves when the branch below it merges.

Nothing was run. No stack was built and rebased to observe the staleness
described, so that finding rests on the documented behaviour of the platform,
and on no reproduction.

## Findings

### The practice is old, and the tooling is what changed

Google chains changes and has for years. Meta popularised the workflow by open
sourcing Phabricator in 2011, with Differential's stacked diffs following around 2016. Gerrit supports chains natively and is used this way at Amazon, Wikimedia,
Arm and Adevinta. Uber, Twitter and Rubrik each maintain implementations of
their own.

The stated cost is consistent across the sources and is not small: the workflow
is complicated, it demands rebasing skill, and it pays off at scale, where a
two-task change gains nothing. An engineer who does not want to acquire the git
skill does not adopt it, which is why the practice stayed inside companies that
could mandate it.

### The platform now does it, and documents where it breaks

GitHub moved stacked pull requests to public preview on 30 July 2026. The model
is the one everything else converged on. The first pull request targets the
default branch and each one above targets the branch below it. Each layer's
diff shows only what that layer adds, so several reviewers work different
layers at once.

Three mechanics matter to a harness:

- **Merging is bottom up.** A pull request in a stack merges only when it, and
  every pull request below it, meets every merge requirement.
- **Merging a lower layer rebases and retargets the rest.** When a mid-stack
  pull request merges, those above it retarget the stack's base branch
  automatically.
- **Branch protections and required checks still apply**, to every layer and not
  only to the bottom one.

The troubleshooting page is the more useful document, because it enumerates
nine failure modes, where the other page describes a happy path. Read as
obligations, they are what any harness working a stack has to survive:

| Failure                                        | What it does                                                                             |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Conflict during a cascading rebase             | Stops mid-rebase and lists the conflicted files                                          |
| Conflict during a sync                         | Leaves the branches **partially updated**                                                |
| A restructuring session refuses to start       | Requires a clean tree, no rebase in progress, no queued pull request, and linear history |
| A restructuring session is interrupted         | Leaves the stack in a state needing an explicit abort or continue                        |
| A pull request will not merge                  | Something below it does not meet its requirements                                        |
| A merge fails midway                           | Lower layers land, the failed one and everything above stay open                         |
| A pull request is ejected from the merge queue | Everything above it is ejected too                                                       |
| A mid-stack pull request is closed             | Everything above it becomes unmergeable                                                  |
| The stack crosses a fork                       | Unsupported, with no remedy                                                              |

Two of those - the partial update and the midway merge - are states in which
the tree and the tracker disagree while every individual page looks healthy.
They are why a harness reads a stack's state back and infers nothing from the
operation it just ran.

### Retargeting a base can leave a pull request unbuilt

A pull request's base can change without any workflow running. GitHub's own
reference states that a workflow runs on a `pull_request` event only for the
activity types `opened`, `synchronize` and `reopened` unless it says otherwise,
and a base change is not one of those three.

The consequence is exact and quiet: a retargeted pull request can show as
mergeable, carry the checks it passed against its **previous** base, and have
never been built against the base it now targets. That is an unearned green,
arrived at without anyone guessing a command.

### Both sides of a stack move, and a partial operation is the normal failure

`jj-stack` names the problem better than the platform documentation does.
Keeping local history and a remote stack aligned is hard because either side
changes independently, and an incomplete operation updates only part of the
stack.

Its model is the simplest one found, which is why it is recorded here. One
change becomes one pull request, and **the order of the local changes is the
order of the pull requests** - there is no second structure to keep in step.
The change identifier carries identity, and the branch carries none, so a
change that is rewritten, split or reordered keeps its pull request, its
reviews and its discussion. Where the remote was rebased by someone else, it
verifies the rebased stack by ancestry and file contents and rebuilds it
locally under the original identifiers, and it treats no rebuilt commit as new
work.

That last behaviour exists because the obvious implementation gets it wrong. A
platform-side rebase produces new commits and the metadata that identified the
change is gone, so a tool trusting commit identity opens a second pull request
for work already in review.

### Small layers are the point, and the evidence is about the reviewer

The argument for stacking is not that it is pleasant. It is that a reviewer's
effectiveness falls off with the size of what is in front of them. SmartBear's
code review research found defect density drops when reviewers go faster than
500 lines of code an hour, which is what a large diff forces.

A stack is how a decomposition that already exists reaches review as the small
pieces it was decomposed into, and nothing reassembles it into one diff because
the branch model could not express the dependency.

Claims of specific speedups circulate widely, and we could reproduce none of
them. An often-repeated figure about an analysis of 1.5 million pull requests
was absent from the article it is attributed to, so this document records it as
unverified and uses it nowhere.

## Conclusions

1. The method already implies stacks, so it must state them. One task, one pull
   request, plus declared dependencies between tasks, is a stack whether or not
   the harness has a word for it. 2. A dependent task's pull request targets
   its dependency's branch, and never the trunk, and the order of the stack is
   the dependency order the epic declared. Any other order is a second
   structure that will disagree with the first. 3. Independent tasks are not
   stacked. A task with no unmerged dependency targets the trunk, so that
   parallel work stays parallel and a stack is never deeper than the
   dependencies require. 4. Merging is bottom up, and the harness never merges
   anyway, so what it must do is report which layer is next and why the others
   cannot go yet. 5. A base is read back, never assumed. Retargeting is
   automatic on the platform and is still a claim until the tracker confirms
   it, exactly as a link is. 6. A green check against a previous base is not a
   green check. After any base change, the harness must confirm a run exists
   against the current base and report the check as not run where it does not. 7. A partial stack update is a state the harness reports, and no retry
   clears it. A conflict during a cascading rebase or a sync leaves some
   branches updated and some not, and the harness names that state and pushes
   through nothing. 8. A stack is never force-pushed without a lease, because
   the failure it prevents is overwriting a collaborator's rebase of the same
   stack. 9. A closed or ejected layer blocks everything above it, and the
   harness reports that blocking relation against the tasks, leaving nobody to
   discover it in the tracker. 10. Identity across a rewrite belongs to the
   task, and the commit carries none of it. A rewritten, split or reordered
   change keeps its pull request. Where the version control system carries a
   stable change identifier, the harness uses it; where it does not, the task's
   own identifier is what the mapping is keyed by. 11. A stack does not cross
   repositories. Where the work would, the harness says so and produces no
   chain that cannot merge. 12. The whole of it must be possible by hand. A
   stack is bases and links, both of which are ordinary commands, so the
   absence of stack tooling makes the work more expensive and never impossible. 13. The cost is real and the harness states it. Stacking demands rebasing
   skill and pays off on an epic with several dependent tasks, where a two-task
   change gains nothing, so a harness that stacks everything has added ceremony
   and no review capacity.

## Sources

All read 2026-09-20.

- [About stacked pull requests](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
  and [Managing stacked pull requests](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/managing-stacked-pull-requests)
  - the model, bottom-up merging, automatic rebase and retarget when a lower
    layer merges, branch protections applying to every layer, the same-repository
    limitation, and the operations for creating, restructuring, rebasing, pushing
    and syncing a stack.
- [Troubleshooting stacked pull requests](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-stacked-pull-requests)
  - the nine documented failure modes, including the partially updated sync, the
    merge that fails midway, merge-queue ejection propagating upward, and a closed
    mid-stack pull request blocking everything above it.
- [Stacked pull requests are now in public preview](https://github.blog/changelog/2026-07-30-stacked-pull-requests-are-now-in-public-preview/)
  - the date, the CLI extension, the stack map, parallel review of layers, and
    merge-queue support arriving separately.
- [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
  - that a `pull_request` workflow runs by default only on `opened`,
    `synchronize` and `reopened`, which is why a base change can leave a pull
    request unbuilt.
- [Announcing jj-stack](https://www.serpentine.com/posts/2026/announcing-jj-stack/)
  - one change to one pull request, local order as stack order, identity carried
    by the change identifier across rewrite, split and reorder, and verification
    of a remote rebase by ancestry and file contents.
- [Stacked diffs, and why you should know about them](https://newsletter.pragmaticengineer.com/p/stacked-diffs)
  - Google's chaining, Meta's Phabricator and Differential, Gerrit's native
    chains, the companies running each, and the stated cost in complexity and
    rebasing skill.
- [I switched to stacked PRs](https://dev.to/adioof/i-switched-to-stacked-prs-my-team-reviews-code-in-hours-not-days-429i)
  - SmartBear's finding that defect density drops above 500 lines of code an
    hour. Read also to check a widely repeated claim about an analysis of 1.5
    million pull requests, which this article does not contain; the claim is
    treated as unverified.
