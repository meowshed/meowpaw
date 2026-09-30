---
id: RES-0312
artifact: research
status: approved
revised: 2026-09-30
elaborates: RES-0290
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# GitHub's `since` includes the second it names, a create returns the issue's own time, and repeated bad credentials lock out good ones

## Summary

Three things `meow-github` does after ADR-1810 rest on GitHub behaviour the
record hadn't read, and one of them is wrong. The read-back listing starts at
the `Date` of the run's first response. When that response is the first
create's own, the listing can start after the issue it has to find, because
`since` includes only issues updated at or after the second it names, and a
create returns the issue's own `updated_at`, which can be earlier than the
response's `Date`. A refusal line that names a permission drops GitHub's
message, although a 403 can have causes no permission header describes, such
as an organisation's single sign-on. A run that meets a 401 goes on sending
requests with the same credential, and GitHub documents that several rejected
requests in a short time make it reject the account's valid credentials too.
This note covers those three and doesn't cover the throttle or the budgets,
which RES-0290 read.

## The question

What should the read-back listing start from, what should a refusal line
carry, and what should a run do after its credential is rejected?

The question assumes the read-back listing is worth keeping. The alternative
is to read each created issue on its own, which TSK-2960 replaced because one
read per create costs a request each and the listing costs one per hundred
issues. The listing keeps that saving only if it finds every issue it has to,
so the assumption stands and the question is where it starts.

It also assumes a refusal is worth describing at all rather than passing
GitHub's answer through. The harness already names the endpoint and the
missing permission, because a credential's scope is invisible until a call
needs it, so the permission stays, and the question is what goes beside it.

## Method

I read GitHub's REST documentation for listing repository issues, creating an
issue, authenticating, and troubleshooting, on 2026-09-30. I read
`crates/meow/src/github.rs`, `crates/meow/src/github/request.rs` and
`crates/meow/src/github/project.rs` on `main` at `b172dbbb`. I ran four read
requests with `gh` 2.101.0 against `meowshed/meowpaw` on 2026-09-30, and one
request with a token that isn't valid. I created no issue, because a create
is a write to a public repository, so the offset between a create's `Date`
and the issue's `updated_at` is read from the documentation and the code and
not observed. I couldn't obtain GitHub's documented text of the 403 message
for an archived repository.

## Findings

### `since` names a second, and the listing includes an issue updated in that second

GitHub documents `since` as "Only show results that were last updated after
the given time", as `YYYY-MM-DDTHH:MM:SSZ`. The word "after" reads as
exclusive, and the service is inclusive. Issue 659's `updated_at` was
`2026-09-29T08:19:41Z`. Listing `repos/meowshed/meowpaw/issues?state=all`
with `since=2026-09-29T08:19:41Z` returned issue 659, and with
`since=2026-09-29T08:19:42Z` it didn't. Issue 778 was also listed with
`since` equal to its `updated_at`, `2026-09-30T16:00:44Z`.

### A create returns the issue with its own `created_at` and `updated_at`

GitHub documents the 201 answer to creating an issue as the whole issue
object, with `created_at` and `updated_at` as required fields. Those are
GitHub's time for the issue, which is what `since` compares.

### The listing starts at the `Date` of the run's first response, which can be the first create's

`Layer::began` in `request.rs` returns the `Date` of the first response the
run received. `name_repository` in `github.rs` sends no request when the
repository is named on the command line, so in `project EPC-NNNN o/r` whose
first task is unmapped, the first response is the first create's. A
response's `Date` is the moment GitHub sent the response, after it wrote the
issue. Where the write and the response fall in different seconds, `since` is
a second after the issue's `updated_at`, and the finding above shows the
listing then leaves the issue out. The run reports that task as
`created, not read back (issue #N, not in the listing)` and exits 3, though
the create succeeded. The mapping is written on the task, so the next run
reads the issue through it and creates no second one.

### A refusal can have a cause the permission headers don't describe

GitHub documents that a classic token not authorised for an organisation that
enforces single sign-on gets a 404 or a 403, and that the 403 carries an
`X-GitHub-SSO` header with a URL to authorise the token, which expires after
an hour. It documents `X-Accepted-GitHub-Permissions` as the permissions an
endpoint requires, for example `pull_requests=write,contents=read`. That
header says what the endpoint accepts, not why this credential was refused,
so a 403 that carries it and was caused by single sign-on reads as a missing
permission. `permission` in `request.rs` quotes GitHub's message only where
neither permission header is present.

### GitHub answers a bad credential with 401 and `Bad credentials`

A request with a token that isn't valid returned `HTTP/2.0 401 Unauthorized`
and the body message `Bad credentials`. The answer's
`Access-Control-Expose-Headers` lists `X-OAuth-Scopes`,
`X-Accepted-OAuth-Scopes` and `X-GitHub-SSO` among the headers GitHub may
send.

### Several rejected requests lock out the account's valid credentials too

GitHub documents: "Authenticating with invalid credentials will initially
return a `401 Unauthorized` response. After detecting several requests with
invalid credentials within a short period, the API will temporarily reject
all authentication attempts for that user (including ones with valid
credentials) with a `403 Forbidden` response." It states neither the number
nor the period.

### A run goes on after a 401 on a mapped issue

`run` in `project.rs` reports a failed read or update of a mapped issue and
goes on to the next task. After a 401 on the first mapped issue, a run over an
epic of forty mapped tasks sends forty more requests with the same rejected
credential. A 401 on a create stops the loop, and the read-back listing then
still runs for any issue already created, which sends one more request with
that credential.

## Options for where the listing starts

| Option                                                                  | Better at                                                                                | The case against it                                                                                                                           |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                              | No change; the failure is safe, because the next run reads the issue through its mapping | A run that did everything reports a partial result and exits 3, and a person or a loop acts on that                                           |
| The first response's `Date` less a margin, such as 60 seconds           | One line; covers any offset up to the margin                                             | The margin is a guess, and a wider window reads more pages in a busy repository                                                               |
| The earliest `updated_at` among the issues the run created              | GitHub's own time for the very issues the listing must find, so no margin                | Needs the field in every create's answer; where it is missing the start has to come from elsewhere                                            |
| A read before the first create, whose `Date` then precedes every create | Keeps "the first response's `Date`" true as written                                      | Costs a request the run doesn't otherwise need, and a read in the same second as the create still leaves the equal-second case to inclusivity |

I lead with the earliest `updated_at`. The case against it is a missing
field, which GitHub documents as required. Where it is missing anyway, the
first response's `Date` is the fallback, which is no worse than today.

## Options for a refusal line and a rejected credential

| Option                                                                      | Better at                                                                                                        | The case against it                                                                                                                           |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Do nothing                                                                  | Lines stay short, and the permission is still named                                                              | A 403 caused by single sign-on or an archived repository reads as a missing permission, and a run keeps sending with a rejected credential    |
| Quote GitHub's message on every refusal line                                | The person sees GitHub's own reason whatever the header says                                                     | The line gets longer, and a message is GitHub's text, which can change                                                                        |
| Quote the message only where the credential already holds an accepted scope | Shorter where the header is the whole story                                                                      | Works only for classic tokens, which send scopes; a fine-grained token sends none, so the case it guards against goes unguarded               |
| Stop the run at the first 401, sending nothing more                         | Keeps a bad credential from locking out the account's good ones, and ends forty requests' worth of the same line | A 401 caused by something passing, such as a token revoked and reissued mid-run, ends a run that a retry could finish; the next run does that |

I lead with quoting the message on every refusal line, and with stopping at
the first 401. The case against stopping is a transient 401, and a run that
stops is resumed by running it again, while a lockout blocks valid
credentials for a period GitHub doesn't state.

## Conclusions

1. The read-back listing must include every issue the run created that
   GitHub still holds, whichever request was the run's first.
2. A refusal report must carry the reason GitHub gave, beside the permission
   it named, because a header describes what an endpoint accepts and not why
   this credential was refused.
3. After GitHub rejects the run's credential, the run must send no further
   request with it, because repeated rejected requests make GitHub reject the
   account's valid credentials too.

## Sources

- [List repository issues and Create an issue](https://docs.github.com/en/rest/issues/issues), read 2026-09-30 - `since` and the create's answer.
- [Authenticating to the REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api), read 2026-09-30 - the 401, the lockout after several rejected requests, and single sign-on's 404 or 403 with `X-GitHub-SSO`.
- [Troubleshooting the REST API](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api), read 2026-09-30 - `X-Accepted-GitHub-Permissions`, and a 404 in place of a 403 for a private repository.
- `gh api` 2.101.0 against `meowshed/meowpaw`, run 2026-09-30 - `since` at and one second after issue 659's `updated_at`, and a 401 for a token that isn't valid.
- `crates/meow/src/github.rs`, `crates/meow/src/github/request.rs` and `crates/meow/src/github/project.rs` at `b172dbbb`, read 2026-09-30 - where the listing starts, how a refusal is worded and what a run does after a 401.
