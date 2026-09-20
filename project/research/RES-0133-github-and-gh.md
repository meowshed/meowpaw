---
id: RES-0133
artifact: research
status: approved
revised: 2026-09-20
elaborates: RES-0022, RES-0005
---

# GitHub and gh

## Summary

This is the only tool in the survey with a quota, a network dependency and a
remote party, so it fails slowly and partially for reasons outside the
repository. The quota has two layers, and the secondary one that an epic hits
is content creation: eighty a minute and five hundred an hour, which a large
plan's issues run into part-way through. A check's state is three-valued, and
pending is neither of its neighbours.

Research for one supported tool. `gh` is how the harness reaches the forge:
issues, pull requests, checks, releases and the API underneath all of them.
That makes it the only tool in this survey with a quota, a network dependency
and a side that is somebody else's server.

It covers what marks a GitHub repository, which of gh's outputs may be parsed,
what the API's limits are and what they mean for an autonomous run, what the
pack authors, and what the skill has to contain.

It does not cover the method's rules for the forge, which are
[RES-0022-forge.md](RES-0022-forge.md), nor stacked pull requests, which are
[RES-0065-stacked-pull-requests.md](RES-0065-stacked-pull-requests.md).

## The question

Every other tool here fails locally and immediately. This one fails slowly,
partially, and for reasons outside the repository: a quota, a permission, a
check still running.

So the question is what a pack must do so that a forge failure is reported as a
forge failure rather than as a defect in the work.

## Method

The tool's manual and the platform's rate-limit documentation were fetched
and read on 2026-09-20: the formatting page for the machine-readable flags and
the field-discovery mechanism, the interface page for pagination's condition
and the field-typing flags, and the limits page for both layers of quota and
the headers that report them.

The numbers are quoted from the documentation rather than observed; no quota
was exhausted to confirm the behaviour at the limit.

Nothing was filed or fetched against a live repository for this document.

## Findings

### gh has a real machine-readable interface, and it is per command rather than global

Three flags compose. `--json` takes a comma-separated list of fields;
`--jq` filters with jq syntax without jq installed; `--template` formats with
Go template syntax plus helpers.

The discovery mechanism removes the guesswork: omitting the argument to
`--json` prints the fields that command supports. So a pack never has to guess
a field name, and a field that disappears in a later release produces an error
naming it rather than a silently absent value.

Not every command supports `--json`, which makes the fallback `gh api` rather
than parsing human output.

### `gh api` is the general interface, and its pagination has a condition

`gh api` makes an authenticated request to either the REST or the GraphQL API
and prints the response, substituting `{owner}`, `{repo}` and `{branch}`.

`--paginate` follows pages, and for GraphQL it works only if _"the original
query accepts an `$endCursor: String` variable and ... fetches the `pageInfo{
hasNextPage, endCursor }` set of fields."_ A GraphQL query written without those
silently returns one page, which looks like a short answer rather than a
truncated one.

`--field` performs type conversion - recognising `true`, `false`, `null`,
integers, placeholders and `@file` references - while `--raw-field` treats
everything as a string. A pack sending a value that happens to look like a
number or a boolean has to know which it is using, because the conversion is
not always what was meant.

`--cache <duration>` caches responses, which is the first line of defence
against a quota.

### The quota is the constraint an autonomous run hits, and it has two layers

Primary limits. An authenticated user, an OAuth app or a GitHub App with a
personal token gets 5,000 requests an hour, rising to 15,000 on Enterprise
Cloud. A GitHub App installation token starts at 5,000 and scales to 12,500 by
repository and user count. `GITHUB_TOKEN` inside Actions gets **1,000 requests
an hour per repository**, which is the smallest and the one a workflow hits
first.

Secondary limits, which are the ones that surprise:

- No more than 100 concurrent requests.
- No more than 900 points a minute on REST, 2,000 on GraphQL, where a read
  costs 1 point and a write typically costs 5.
- No more than 80 content-creating requests a minute and 500 an hour.

The headers report the state: `x-ratelimit-remaining`, `x-ratelimit-reset` as a
UTC epoch second, and `retry-after` in seconds for a secondary limit.

Three consequences for this harness, and they are the reason this section is
the longest.

The content-creation limit is the one an epic hits. Filing a plan's tasks
as issues is content creation, and 80 a minute with 500 an hour is a real
ceiling for a large plan. A pack that files issues in a tight loop will be
throttled part-way through, leaving some tasks filed and some not.

A write costs five times a read, so the cheap way to be safe - re-reading
state after every write - is not cheap.

`retry-after` is an instruction, not a suggestion. A harness that retries
before it elapses is making the limit worse, and an autonomous loop that does
so can exhaust an hour's quota in minutes.

So the rule is: read the headers, honour `retry-after`, cache reads, batch
writes, and report a partial completion as partial rather than retrying it into
a worse state.

### A check's state is not a check's result, and the distinction has three values

A pull request's checks are pending, passing or failing, and the first is not a
failure. A harness that reads a rollup while a workflow is still queued and
reports it as red has reported a lie; one that reports it as green has reported
a different lie.

So a forge status is read as three-valued, and _pending_ is a state the harness
waits in or reports, never one it collapses into either neighbour.

### Authentication is ambient and its scope is invisible

`gh` authenticates from its own stored credentials or from `GH_TOKEN` in the
environment. What the token can do is not discoverable from the command being
run: a token without `workflow` scope fails only when a workflow file is
touched, and a fine-grained token missing a permission fails only on the
endpoint that needs it.

That makes a permission failure look like an arbitrary failure at an arbitrary
moment. A pack that reports the endpoint and the missing scope turns an
unhelpful error into an actionable one.

The harness must not read the token's value, for the same reason it does not
read any other secret material. Knowing that authentication exists is enough.

### What the pack authors

Issues, pull requests, reviews, releases and labels - the forge objects the
method uses - and the workflow files under `.github/workflows` where the
project asks for them.

It does not author repository settings, branch protection or required checks
unasked: those are the repository's governance, and changing them is a
different kind of act from filing a pull request.

Every one of those objects is subject to the rule against attribution: nothing
the harness files carries a co-author trailer or a generated-by line.

### What a reviewer needs that no command reports

Whether a green check ran against the merge result or the branch tip, which
differ once the base moves.

Whether a required check is actually required, or is merely present.

Whether an auto-merge will fire on a stale approval.

Whether an issue the harness filed is the issue the plan meant, since a filing
loop that was throttled half-way leaves a plausible-looking partial set.

### What the skill has to contain

In the body, in this order:

1. The three-valued status rule. Pending is not a failure and is not a
   pass.
2. Quota. The primary limits by token kind, the three secondary limits,
   the headers, and that `retry-after` is honoured.
3. Machine-readable output. `--json` with discovered fields, `--jq`,
   `gh api` for what `--json` does not cover, and the GraphQL pagination
   condition.
4. Partial completion. A throttled batch is reported as partial with what
   succeeded named, never retried blindly.
5. What must never happen. Parsing human-readable output. Reading the
   token. Changing repository settings unasked. Adding attribution to anything
   filed. Retrying before `retry-after` elapses.

In supporting files: the rate limit table; the check-status vocabulary; the
`--json` field discovery method; the GraphQL pagination requirement; and the
dated facts with what to re-check, because quotas change.

## Conclusions

1. Machine-readable output uses `--json` with fields discovered by omitting
   the argument, so no field name is guessed and a removed field errors by
   name.
2. Human-readable output is never parsed, and where `--json` is
   unsupported the pack uses `gh api` instead.
3. A GraphQL query used with `--paginate` declares `$endCursor` and fetches
   `pageInfo`, or it returns one page and looks like a complete short answer.
4. `--field` and `--raw-field` are chosen deliberately, because type
   conversion changes what the API receives.
5. Reads are cached, through `--cache` or the pack's own store, because a
   quota is the binding constraint on an autonomous run.
6. The rate limit headers are read on every response:
   `x-ratelimit-remaining`, `x-ratelimit-reset` and `retry-after`.
7. `retry-after` is honoured exactly, since retrying earlier worsens the
   limit and an autonomous loop can exhaust an hour's quota in minutes.
8. Content creation is budgeted separately at 80 a minute and 500 an hour,
   which is what filing a large plan's tasks as issues runs into.
9. A write costs about five times a read, so re-reading state after every
   write is not a cheap safety measure.
10. The `GITHUB_TOKEN` limit inside Actions is 1,000 an hour per
    repository, the smallest of the primary limits, and is assumed when
    running in a workflow.
11. A forge status is three-valued, and pending is never collapsed into
    passing or failing.
12. A partial completion is reported as partial with what succeeded named,
    because a throttled filing loop leaves a plausible-looking incomplete set.
13. A permission failure is reported with the endpoint and the missing
    scope, since token scope is invisible until the call that needs it.
14. The token's value is never read, printed or forwarded.
15. Repository settings, branch protection and required checks are not
    changed unasked, because they are governance rather than work.
16. Nothing filed carries attribution - no co-author trailer and no
    generated-by line - on an issue, pull request, review, release or tag.
17. The skill body carries the three-valued status rule, quota,
    machine-readable output, partial completion, and the prohibitions, in
    that order.

## Sources

All read 2026-09-20.

- [gh formatting](https://cli.github.com/manual/gh_help_formatting) - `--json`
  taking a comma-separated field list, `--jq` filtering with jq syntax and
  `--template` with Go template syntax; and that omitting the argument to
  `--json` prints the fields a command supports.
- [gh api](https://cli.github.com/manual/gh_api) - authenticated requests to
  the REST and GraphQL APIs with `{owner}`, `{repo}` and `{branch}`
  substitution; `--paginate` requiring a GraphQL query that accepts
  `$endCursor: String` and fetches `pageInfo{ hasNextPage, endCursor }`;
  `--method`; `--field` with type conversion for booleans, null, integers,
  placeholders and `@file` against `--raw-field` treating values as strings;
  and `--cache` with a duration.
- [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
  - 5,000 requests an hour for authenticated users and 15,000 on Enterprise
    Cloud; GitHub App installation tokens from 5,000 scaling to 12,500; 1,000 an
    hour per repository for `GITHUB_TOKEN` in Actions; the secondary limits of
    100 concurrent requests, 900 points a minute on REST and 2,000 on GraphQL
    with reads at 1 point and writes typically at 5, and 80 content-creating
    requests a minute with 500 an hour; and the `x-ratelimit-remaining`,
    `x-ratelimit-reset` and `retry-after` headers.
