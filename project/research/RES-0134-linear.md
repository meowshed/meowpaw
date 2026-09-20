---
id: RES-0134
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0022, RES-0005
---

# Linear

## Summary

Supporting a tracker is no second forge to support. The tracker holds the work
item, the forge holds the code, and an integration the harness neither controls
nor duplicates automates the seam. Its limits are two-dimensional and
complexity runs out before requests, which inverts how a pack should ask. And
choosing between a closing and a referencing word decides whether merging a
part of a series closes the whole item.

Research for one supported tool. Linear is the alternative projection: where a
repository tracks its work in Linear rather than on the forge, the harness
files against Linear's identifiers, its branch names and its magic words.

It covers what its interface is, how it authenticates, what its limits are, how
its integration with the forge links work to code, what the pack authors, and
what the skill has to contain.

It does not cover the method's rules for the projection, which are
[RES-0022-forge.md](RES-0022-forge.md).

## The question

Supporting a tracker is not supporting a second forge. The tracker holds the
work item; the forge holds the code. The interesting part is the seam between
them, which is automated by an integration the harness does not control and
must not duplicate.

## Method

We fetched and read the vendor documentation on 2026-09-20. The interface page
gave the query language, authentication and the recommended client. The
rate-limiting page gave both quotas and the four headers, and the integration
page the enumerated magic words and the default transitions.

The magic words are taken as enumerated lists rather than summarised, because
which group a word belongs to changes what merging does.

Nothing was queried against a live workspace, so every limit is quoted rather
than observed.

## Findings

### The interface is GraphQL and only GraphQL

Linear's API is GraphQL at `https://api.linear.app/graphql`, described as _"the
same API we use internally for developing our applications"_, with
introspection enabled so the whole schema can be queried.

No REST fallback exists. So a pack either speaks GraphQL or uses the
TypeScript SDK, which Linear recommends and which exposes the schema as models
and mutations.

Introspection is the useful property for a pack that must not guess: the schema
is discoverable at run time, which is the same advantage `gh`'s field discovery
gives and is stronger.

### Authentication has two forms and they have different limits

A **personal API key** goes in the `Authorization` header and is the simple
choice for a personal script. **OAuth2** is what Linear recommends for an
application other people use, with the token passed as `Authorization: Bearer
<token>`.

The distinction is not only about who owns the credential; the quotas differ,
which is the next finding.

### The limits are two-dimensional, which is unlike the forge

|                 | Requests an hour | Complexity points an hour |
| --------------- | ---------------- | ------------------------- |
| API key         | 2,500            | 3,000,000                 |
| OAuth app       | 5,000 per user   | 2,000,000                 |
| Unauthenticated | 600              | 100,000                   |

A single query may cost at most 10,000 complexity points.

Four headers report the state: `X-RateLimit-Requests-Remaining` and
`X-RateLimit-Requests-Reset`, and `X-RateLimit-Complexity-Remaining` and
`X-RateLimit-Complexity-Reset`. Both resets are in UTC epoch **milliseconds**
where the forge uses seconds, which is exactly the kind of detail a shared
retry helper gets wrong.

The second dimension is the one that matters to how a pack asks questions. A
GraphQL query that walks deeply - every issue with every comment with every
author - can be cheap in requests and expensive in complexity, and it is the
complexity budget that runs out first. The documentation's own warning points
the same way: do not poll each issue individually, because the application may
be rate limited.

So the shape of a well-behaved pack here is the opposite of a REST pack: fewer,
wider queries that fetch what is needed in one round trip, kept under the
per-query ceiling.

### The seam to the forge is automated, and the harness must not duplicate it

Linear's GitHub integration links pull requests to issues and moves their
status. The linking happens three ways: a branch name copied from Linear that
contains the issue identifier, the identifier appearing in the pull request
title, and magic words in the title or description.

The magic words are enumerated, and the distinction between the three groups is
the part a pack has to respect:

- **Closing**: close, closes, closed, closing, fix, fixes, fixed, fixing,
  resolve, resolves, resolved, resolving, complete, completes, completed,
  completing, implement, implements, implemented, implementing. The issue moves
  to done on merge.
- **Non-closing**: ref, refs, references, part of, contributes to, toward,
  towards. The issue is linked without the final status change.
- **Relation**: relates to, related to. Marked related only.

By default a linked issue moves to in-progress when the pull request opens, and
to done when it merges. Teams configure status changes per event - draft, open,
review requested, ready to merge, merged - and per target branch, so a merge to
one branch means one status and a merge to another means a different one.

Three consequences.

The word choice is a decision with an effect. Writing "fixes" where "part of"
belongs chooses whether merging closes the issue. A pack using closing words by
default closes issues the work only partly addressed, which is the failure mode
of a stacked series, where each part references the same issue and only the
last one finishes it.

The harness must not also set the status. If the integration moves the
issue on merge and the harness moves it too, the two race, and the audit trail
shows a change nobody made deliberately. The pack states the link and lets the
integration act.

A team's configuration is not knowable from the words. Whether merging to
this branch means done depends on settings the pack cannot see from the pull
request, so a report says what link was made rather than what status will
result.

### Identifiers are the tracker's, and they are stable

An issue is `ENG-123` - team prefix and number - which is what appears in
branch names, in magic words and in conversation. That is the identifier the
harness cites, and it is stable in a way a forge issue number in a moved
repository is not.

### What the pack authors

Issues, comments and status transitions through GraphQL mutations, and the
branch name and pull request text that carry the link.

It does not author workflow configuration - which status each event maps to -
because that is the team's process rather than the work.

The rule against attribution applies here exactly as it does on the forge:
nothing the harness files in Linear says it was generated.

### What a reviewer needs that no command reports

Whether the magic word matches the intent: closing when the work is finished,
referencing when it is a part.

Whether an issue was moved by the integration or by the harness, since the
result looks the same and only one is reproducible.

Whether the branch name carries the identifier, because that is the link that
survives a title edit.

Whether a query the pack runs is cheap in requests and expensive in complexity.

### What the skill has to contain

In the body, in this order:

1. The seam rule. The integration moves status; the harness states the
   link and does not also move it.
2. Magic words, with the three groups and the consequence of choosing from
   the wrong one.
3. Query shape. Fewer, wider GraphQL queries under the per-query ceiling,
   never per-issue polling.
4. Limits. Both dimensions, the four headers, and that the resets are in
   milliseconds.
5. What must never happen. Using a closing word for a partial change.
   Setting a status the integration will also set. Polling issues
   individually. Reading the API key. Adding attribution.

In supporting files: the magic word lists; the limit table and headers; the
identifier format; the recommended query patterns; and the dated facts with
what to re-check, because quotas and integrations change.

## Conclusions

1. The interface is GraphQL only, so a pack speaks GraphQL or uses the
   recommended SDK, and there is no REST fallback to drop to.
2. The schema is discovered by introspection rather than assumed, which
   removes guessing about field names.
3. Both limit dimensions are tracked: requests an hour and complexity
   points an hour, with a 10,000-point ceiling on a single query.
4. The reset headers are in milliseconds, unlike the forge's seconds, and a
   shared retry helper accounts for the difference.
5. Queries are few and wide rather than many and narrow, because complexity
   is the budget that runs out first and the documentation warns against
   polling issues individually.
6. The authentication form is recorded, since an API key and an OAuth token
   have different quotas.
7. The harness states the link and lets the integration move the status,
   because doing both races and produces an audit trail nobody authored.
8. A closing magic word is used only when merging finishes the work, and a
   part of a series references rather than closes.
9. The three groups of magic words are used deliberately, since closing,
   non-closing and relation are different commitments.
10. A report says which link was made, not which status will result,
    because the mapping from event to status is team configuration the pack
    cannot see.
11. The identifier cited is the tracker's - the team prefix and number -
    which is what branch names and magic words carry.
12. The branch name is the durable link, surviving an edit to the pull
    request title.
13. Workflow configuration is not authored by the pack, because it is the
    team's process rather than the work.
14. The API key is never read, printed or forwarded, and nothing filed
    carries attribution.
15. The skill body carries the seam rule, magic words, query shape, limits,
    and the prohibitions, in that order.

## Sources

All read 2026-09-20.

- [Linear GraphQL API](https://linear.app/developers/graphql) - the API as
  GraphQL at `https://api.linear.app/graphql`, described as the same API Linear
  uses internally, with introspection enabled; personal API keys in the
  `Authorization` header and OAuth2 bearer tokens as the two authentication
  methods, with OAuth recommended for applications other people use; the
  TypeScript SDK as the recommended client; and the warning against polling
  each issue individually.
- [Linear rate limiting](https://linear.app/developers/rate-limiting) - 2,500
  requests an hour for an API key, 5,000 per user for an OAuth app and 600
  unauthenticated; 3,000,000 complexity points an hour for an API key,
  2,000,000 for an OAuth app and 100,000 unauthenticated; a 10,000-point
  maximum for a single query; and the headers
  `X-RateLimit-Requests-Remaining`, `X-RateLimit-Requests-Reset`,
  `X-RateLimit-Complexity-Remaining` and `X-RateLimit-Complexity-Reset` with
  resets in UTC epoch milliseconds.
- [Linear's GitHub integration](https://linear.app/docs/github) - linking by
  branch name copied from Linear, by identifier in the pull request title and
  by magic words; the enumerated closing, non-closing and relation magic words;
  the default transitions to in-progress on open and done on merge; and
  per-event and per-branch configuration of which status each event produces.
