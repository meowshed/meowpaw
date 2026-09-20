---
id: RES-0022
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0001
---

# The forge: issues, commits and pull requests

## Summary

The harness files its own issues and links them to branches, commits and pull
requests. One platform rule breaks the obvious implementation: the closing
keywords are interpreted only where the pull request targets the default
branch. So issues are created only after the epic is approved, the link is
verified after creation rather than assumed from the keyword, and an issue
cites requirement identifiers instead of paraphrasing them.

Research for `meow-gh` and the parts of `meow-scm` that reach a forge. The
harness files its own issues, links them to the branches and commits that
implement them, and closes them with the pull request that lands the work.

Two of the six internal harnesses already do this, which made it the
best-evidenced capability in the survey that the design had not specified when
this research was written. It is specified now, in section 15a of the
requirements.

## Method

We fetched and read the platform's own documentation on linking pull requests
to issues on 2026-09-20. The default-branch condition and the ten-link limit
came from there, and neither appears in the general guidance about keywords.

The internal repositories were read for how they currently file and link work.

Nothing was filed or linked as an experiment, so the default-branch condition
is taken from the documentation rather than reproduced here.

## What the internal harnesses already do

`meowctl`'s `/plan` decomposes an approved specification into GitHub issues
with explicit dependencies. Three details transfer whole:

- Each issue **cites the requirement identifiers it closes, verbatim**. "Do not
  paraphrase the requirement into the issue; cite it. The spec stays the single
  source."
- Each issue names the issues that must close first, **and why** - with the
  rule that "a dependency that is only about convenience is not a dependency;
  say so and let them proceed in parallel".
- **The plan is presented for approval before anything is created on GitHub.**
  Issues are created only after the plan is approved. Creating them first makes
  the forge the record of a plan nobody agreed to.

`vlie`'s `/work` consumes the other end. "Pick the highest-priority open issue
with no unimplemented dependencies", then branch and implement. Then "create or
update the PR with labels, milestone, and issue link", make the checks green or
report the exact blocker, and "do not merge without explicit user approval".

Between them that is the whole loop - plan to issues, issues to a branch,
branch to a pull request, pull request to a closed issue - and neither invented
anything the other needed.

## How the linking actually works, and where it breaks

The mechanics matter because three of them fail silently.

Closing keywords. `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`,
`resolve`, `resolves`, `resolved`, each followed by `#123`. They work in a pull
request description and in a commit message.

The default-branch trap. Keywords in a pull request description are
interpreted **only when the pull request targets the repository's default
branch**. Target any other branch and the keywords are ignored entirely: no
link is created, and merging closes nothing. A stacked pull request, a release
branch, a long-lived integration branch - all silently lose the link.

This is the single most important fact here, because the failure is invisible.
The text reads correctly, the pull request merges, and the issue stays open with
no indication that anything went wrong.

Sub-issues do not close by keyword. GitHub's sub-issue relationship is newer
than the keyword mechanism, and nothing wires the two together. A sub-issue is
linked through the pull request's Development sidebar, which the CLI exposes
through no first-class flag. A harness that files a hierarchy of issues and
relies on keywords will close the parents and leave the children open.

Manual linking is capped at ten issues per pull request, and requires write
permission.

The CLI has no `--add-issue`. `gh pr create` links by body text only;
adding a link afterwards is an open request on the CLI. So the body is the
mechanism, which makes the default-branch trap the operative constraint.

### What follows

The harness must **verify the link rather than assume it**. After opening a
pull request, read back what the forge thinks is linked. This is the same rule
as evidence generally: a keyword in a body is a claim, and the forge's view of
the link is the fact.

And where the target is not the default branch, or the issue is a sub-issue,
the harness must say the link could not be made by keyword rather than write
one that does nothing.

## Templates

A forge repository usually carries its own: `.github/ISSUE_TEMPLATE/` (one or
more forms, sometimes as YAML issue forms with typed fields), and
`.github/PULL_REQUEST_TEMPLATE.md`.

The repository's template wins. It encodes what that project's maintainers
decided they need, and it is what human contributors see. An agent filing
issues in a different form makes the tracker inconsistent, which is obvious to
everyone except the agent.

The harness supplies a template **only where the repository has none**. That
fallback earns its place, because a repository with no template gets issues in
whatever form the model felt like, which is the state most trackers are in.

This generalises past the forge and becomes a rule of its own: **a repository's
own conventions beat the harness's defaults, and the harness supplies a default
only where none exists.** The same already applies to the writing standard, the
artifact layout and the gate verbs.

## What an issue should carry

From `meowctl`'s rules plus what the linking mechanics require:

| Field                                         | Why                                          |
| --------------------------------------------- | -------------------------------------------- |
| The requirement identifiers it closes, cited  | The specification stays the single source    |
| Its dependencies, with the reason each is one | A convenience dependency is not a dependency |
| A review size - small, medium, large          | So the plan can be sequenced by cost         |
| The unit of work it belongs to                | So the tracker and the artifacts agree       |
| Labels and milestone                          | So the forge's own views work                |

And what it should **not** carry: a paraphrase of the requirement, a copy of the
design, or an implementation plan. Those exist in the repository, and a copy in
the tracker is a second source that drifts.

## A second tracker, and what it proves

Linear is the obvious second projection, and adding it is the test of whether
the claim is true - whether a tracker really is a mapping rather than an
integration.

It links three ways, which is two more than GitHub:

1. The issue identifier in the branch name. Linear hands out a branch name
   with every issue (`gitBranchName`), such as
   `user/eng-285-short-slug`. This is the mechanism it recommends, and it is
   the interesting one: the link is established by _cutting the branch_, before
   any pull request exists.
2. The identifier in the pull request title.
3. A magic word plus the identifier in the description - its word list is
   wider than GitHub's, adding `complete`/`completes`/`completed` and
   `implement`/`implements`/`implemented` to the usual close, fix and resolve
   families.

And the trap is different from GitHub's, in a way that makes the general rule
sharper. GitHub's keywords fail on a non-default target branch. **Linear's
closing behaviour depends on workspace settings** - the same description, in
the same repository, closes an issue or does not, according to configuration
the harness cannot see from the working tree.

That settles the design question. The harness cannot reason about whether a
link worked from the text it wrote; it has to ask the tracker. One tracker made that a good idea; two make it the only thing that
works.

The branch-name mechanism transfers to any tracker, because it is the earliest
possible moment to establish the link and it survives a pull request that is
opened badly. Where the profile names a tracker that supplies a branch name,
`meow-scm` uses it.

## Where the tracker sits relative to the artifacts

This is the question that decides whether the integration helps or hurts.

The plan is the source of truth for **what the tasks are**; the tracker is the
source of truth for **what is happening to them**. One is a reviewed artifact
under version control, the other is a live work queue. They are linked by
identifier, and neither derives from the other continuously. The plan creates
the issues once, after approval, and from then on the issue's state and the
task's mark are two facts verification compares.

The failure to avoid is a tracker that becomes a second plan. Issues edited
until they no longer match the tasks, new issues filed outside any plan, and a
plan nobody updates because "it is all in GitHub". `meowhub`'s numbered
directories and `meowctl`'s issues coexist precisely because the split is
maintained.

## Conclusions

1. Issues are created only after the epic is approved, never before.
2. One task, one issue, one branch, one pull request, linked by identifier
   in both directions.
3. An issue cites requirement identifiers; it never paraphrases them.
4. Dependencies are stated with reasons, and a convenience dependency is
   not one.
5. The repository's issue and pull request templates win; the harness
   supplies one only where none exists.
6. The link is verified after creation, not assumed from the keyword.
7. Where a keyword cannot work - a non-default target branch, a sub-issue -
   say so rather than writing one that silently does nothing.
8. The tracker is not a second plan. Verification compares the two and
   reports disagreement.
9. Nothing is merged, closed or released without explicit instruction.
10. Which tracker, if any, is the project's choice, declared in its profile
    - and a second tracker must cost a mapping, not an integration.

## Sources

- [Linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue),
  GitHub Docs, read 2026-09-20 - **the keywords are interpreted only when the
  pull request targets the default branch**, the Development sidebar, and the
  limit of ten manually linked issues.
- [Using keywords in issues and pull requests](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/using-keywords-in-issues-and-pull-requests)
  and [Closing an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/administering-issues/closing-an-issue),
  read 2026-09-20 - the nine closing keywords, and keyword closing from a commit
  message merged into the default branch.
- [Sub-issue cannot be closed via closing keywords](https://github.com/orgs/community/discussions/178149),
  GitHub community discussion, read 2026-09-20.
- [`gh pr create` manual](https://cli.github.com/manual/gh_pr_create) and
  [Add issue linking to PRs via `gh pr edit --add-issue`](https://github.com/cli/cli/issues/11405),
  read 2026-09-20 - linking is by body text; no first-class flag exists.
- `~/workspace/meowctl/.claude/commands/plan.md`, read 2026-09-20 - issues after
  approval, citing requirement identifiers verbatim, dependencies with reasons,
  and the convenience-dependency rule.
- [Linear GitHub integration](https://linear.app/integrations/github) and
  [Linear GitLab docs](https://linear.app/docs/gitlab), read 2026-09-20 - the
  three linking mechanisms, the `gitBranchName` handed out with each issue, the
  wider magic-word list, and that automatic closing depends on workspace
  settings.
- `~/workspace/vlie/.claude/commands/work.md`, read 2026-09-20 - selecting the
  highest-priority issue with no unimplemented dependencies, and opening a pull
  request with labels, milestone and issue link.
