---
id: RES-0277
artifact: research
status: approved
revised: 2026-09-26
elaborates: RES-0037, RES-0154, RES-0265
---

# Converting a repository from its documents and its forge history

## Summary

A repository's issues and pull requests hold what its code can't: what people
asked for, and which option they took and which they rejected. Reading all of
it is cheap. This repository's whole history, 345 issues and pull requests with
their comments, took 6 requests against a limit of 5,000 an hour. So
onboarding can recover, as drafts, the obligations and decisions that people
stated there, each citing the issue or comment it came from. It still
recovers none from code alone.

Once a person approves the onboarding report, the old documents it placed can
go. A migrated, superseded or discarded document is removed in a change of its
own, which carries a count before and after. A document cited as a source
stays.

This extends RES-0037 and RES-0154, which found that code shows what a system
does and never what it must do. Neither looked at a forge's history.

## Method

I read GitHub's REST reference on 2026-09-26: listing a repository's issues,
listing its pull requests, listing issue comments and review comments, and the
rate limits. I also read the `gh api` manual the same day. Then I read this
repository's whole history through `gh api`, with `--paginate --slurp`, and
counted the pages, the items and the requests the rate limit reported. Last,
I compared what its issues and pull requests state with what its code and its
record state.

## Findings

### One listing reads every issue and pull request

GitHub lists a repository's issues at `GET /repos/{owner}/{repo}/issues` with
`state=all`, up to 100 a page. The comments reference says "Every pull request
is an issue, but not every issue is a pull request", and the issues reference
says "You can identify pull requests by the `pull_request` key". The pull request listing gives `merged_at`, which is null
for a pull request that was closed without merging. Conversation comments on
issues and pull requests come from one listing,
`GET /repos/{owner}/{repo}/issues/comments`. Review comments, the ones on the
diff, come from `GET /repos/{owner}/{repo}/pulls/comments`, and the reference
says these "are different from commit comments and issue comments in a pull
request".

This repository read in full on 2026-09-26:

| Listing                  | Pages | Items                               |
| ------------------------ | ----- | ----------------------------------- |
| Issues and pull requests | 4     | 345, of which 181 are pull requests |
| Conversation comments    | 1     | 16                                  |
| Review comments          | 1     | 0                                   |

The core limit went from 4,997 to 4,991 remaining out of 5,000 over those
reads: 6 requests for the whole history.

### What the limits require

An authenticated caller gets 5,000 requests an hour, and an unauthenticated
one gets 60. Every response reports the limit, what remains, what was used and
when the window resets, in `x-ratelimit-limit`, `x-ratelimit-remaining`,
`x-ratelimit-used` and `x-ratelimit-reset`. A secondary limit returns
`retry-after`, and the reference says not to retry "until after that many
seconds has elapsed". It also warns that continuing while limited "may result
in the banning of your integration". A read costs 1 point against 900 points a
minute. `gh api --paginate` requests pages "until there are no more pages of
results", `--slurp` joins them into one array, and `--cache` keeps a response
for a stated duration.

### What the history states that the code doesn't

An issue that asks for a behaviour states an obligation in somebody's words. A
pull request discussion that weighs options, and the one that merges, records a
decision and the alternative it rejected. A pull request closed with
`merged_at` null records a rejected approach. None of this is visible in code,
which shows only the option that won. So these are statements a person made,
which is the line RES-0037 draws between a specification recovered from what
exists and a requirement nobody stated.

Each statement has an address that doesn't move: an issue number, a pull
request number, or a comment URL. A draft can cite that address as its source.
The person who approves the draft affirms it, which RES-0154 found is the only
thing that makes a requirement.

### Old documents and old records

RES-0037 found that nothing is deleted until it is placed. Once a person
approves the report, each placed document is either removed or kept:

- **Migrated, superseded or discarded:** its content now lives in a named
  artifact, or has a recorded reason to go, so keeping it leaves two sources
  of truth.
- **Cited as a source:** it stays, because the citation points at it.

RES-0265 found that a bulk change needs a count before and after, because a
lost file fails no check. It also found that the mechanical part of a change
belongs apart from the editorial part, so the removal is its own change.

A repository that already keeps records in a format of its own, such as a
folder of decision records or a task list, holds the strongest evidence of
its decisions. Each of those records migrates to the artifact kind that holds
it.

### Where the forge knowledge lives

The method names no language or tool, so knowledge of one forge belongs in a
pack. Onboarding reads the history through a forge pack where one is
installed. Where none is, it reports the history as unread and names the pack
that would read it.

## Conclusions

1. A forge's whole history is cheap to read: this repository's took 6
   requests of 5,000.
2. Issues and pull requests state obligations and decisions that code doesn't,
   and each statement has an address a draft can cite.
3. Recovered obligations and decisions are drafts citing their statement, and
   the person who approves one affirms it. Nothing is recovered from code
   alone.
4. A pull request closed without merging records a rejected alternative.
5. Reading must use the forge's structured output, page to the end, and
   honour the reported limits and `retry-after` exactly.
6. After approval, each migrated, superseded or discarded document is removed
   in a change of its own, with a count before and after. A cited document
   stays.
7. A record the repository kept in its own format migrates to the matching
   artifact kind.
8. Forge knowledge lives in a pack. Onboarding without one reports the
   history as unread and names the pack.

## Sources

- [List repository issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues),
  read 2026-09-26: the listing, its page size, and pull requests identified
  by the `pull_request` key.
- [List pull requests](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests),
  read 2026-09-26: the `state` values and `merged_at`.
- [List issue comments for a repository](https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#list-issue-comments-for-a-repository),
  read 2026-09-26: one listing for comments on issues and pull requests.
- [Pull request review comments](https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28),
  read 2026-09-26: review comments on the diff, listed per repository.
- [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28),
  read 2026-09-26: the primary and secondary limits, the headers, and
  `retry-after`.
- [gh api](https://cli.github.com/manual/gh_api), read 2026-09-26:
  `--paginate`, `--slurp` and `--cache`.
- The GitHub API, 2026-09-26: the whole history of `meowshed/meowpaw`, read
  through `gh api` with the rate limit before and after.
