---
id: RES-0290
artifact: research
status: approved
revised: 2026-09-29
elaborates: RES-0133, RES-0134
---

# gh 2.101.0 shows GitHub's limit headers only under `--include`, replays stale ones from its cache, and names where its token came from

## Summary

On 2026-09-29, `gh api --include` printed a response's status line and
headers ahead of its body and exited 1 on a 403 or a 404 with both still on
standard output, so a program reads the limit headers only by asking for them
and by reading the output of a failed call. A response replayed from
`--cache` carried the headers stored with it, `Date` included, so its
`x-ratelimit-remaining` described an earlier moment. `--include` with
`--slurp` printed text that isn't JSON. A 404 on a path GitHub doesn't route
carried no rate-limit header at all. `gh auth status --json hosts` named the
token's source as `keyring`, `GH_TOKEN` or `GITHUB_TOKEN` without printing the
token. GitHub's documentation, read the same day, says what to do on a limit
error when `retry-after` is absent, that writes go serially and at least a
second apart, and how a refusal names the permission it wanted.

This note covers the REST interface as `gh` 2.101.0 presents it on
github.com. It doesn't cover GraphQL, GitHub Enterprise Server, or Linear,
which RES-0134 read.

## The question

RES-0133 says a harness reads `x-ratelimit-remaining`, `x-ratelimit-reset` and
`retry-after` on every response. The question is how a program that reaches
GitHub only through `gh` can see them, and what it has to do with a response
that carries none, an old one, or one that refuses the call.

The assumption behind it is that `gh` passes the headers through at all, and
that each response it returns is a fresh one. Both are checked below, and the
second fails for a cached read.

## Method

I ran `gh` 2.101.0, released 2026-09-15, on this machine on 2026-09-29,
signed in through its stored credential with `GH_TOKEN`, `GITHUB_TOKEN` and
`GITHUB_ACTIONS` unset. Every call read or rendered, and none wrote:

- `gh api --include rate_limit`, and the same against
  `repos/meowshed/meowpaw/no-such-thing` for a 404 and
  `repos/cli/cli/actions/secrets` for a 403, recording the exit status,
  standard output and standard error of each.
- `gh api --include --paginate` and `--include --paginate --slurp` over
  `repos/meowshed/meowpaw/labels?per_page=4`, nine labels over three pages.
- `gh api --include --cache 1h` twice, two seconds apart, over a label page
  and over the 403 above, comparing `Date` and `X-Ratelimit-Remaining`.
- `gh api --include 'repos/{owner}/{repo}'` from a clone, and
  `gh api --include rate_limit` three times with `date -u +%s` read just
  before and just after each call, comparing `Date` with the local clock.
- `gh auth status --active --json hosts`, with `--jq` selecting every field
  but the token, three times: signed in, with `GH_TOKEN=not-a-token`, and with
  only `GITHUB_TOKEN=not-a-token`.
- `gh api --verbose markdown --input` over a file holding `{"text":"hi"}`,
  once with no `--method` and once with `-X GET`, recording the method sent.
  `POST markdown` renders text and changes nothing on GitHub, so it shows the
  method without writing.
- `gh help environment` and `gh api --help`.

I read seven GitHub documentation pages on 2026-09-29, listed under
`## Sources`. I didn't exhaust a limit, so every statement about a limit
error is the documentation's, and no response carrying `retry-after` or
`X-Accepted-GitHub-Permissions` was observed. The credential here is an OAuth
token, so what a fine-grained token or an Actions token receives is quoted,
not seen.

## Findings

### `--include` puts the status line and headers before the body, and a failed call still prints them

`gh api --include rate_limit` printed `HTTP/2.0 200 OK`, one header a line,
a blank line and the JSON body, and exited 0. The 404 and the 403 each exited
1, printed the same block to standard output, and printed
`gh: Not Found (HTTP 404)` or GitHub's message with `(HTTP 403)` to standard
error. So the headers of a refused call are on standard output, beside an
exit status that says only that the call failed.

`gh` writes header names in Go's canonical case, such as
`X-Ratelimit-Remaining`, where GitHub's documentation writes
`x-ratelimit-remaining`. A reader that compares names exactly misses every
one.

### Each response names its own limit, and `x-ratelimit-reset` counted epoch seconds

The 200 carried `X-Ratelimit-Limit: 5000`, `X-Ratelimit-Remaining`,
`X-Ratelimit-Used`, `X-Ratelimit-Resource: core` and
`X-Ratelimit-Reset: 1790695444`. `date -u +%s` printed 1790692237 a moment
later, so the reset lay 3,207 seconds ahead, which is inside the hour a
primary limit spans only when the value counts seconds. Read as milliseconds
it would have lain in January 1970.

The limit arrives on every counted response, so the budget that applies to a
credential is read from GitHub rather than assumed from how the run
authenticated.

`gh api --include 'repos/{owner}/{repo}'`, run from a clone of this
repository at 14:47 UTC, exited 0, filled the placeholder from the clone's
remote, and printed the body for `meowshed/meowpaw` under the same header
block, with `X-Ratelimit-Resource: core`. So naming the repository through
`gh api` reads the same signals as every other call.

### GitHub's `Date` and this machine's clock agreed to the second

Three `gh api --include rate_limit` calls, one straight after another at
14:47 UTC, each printed `Date: Tue, 29 Sep 2026 14:47:21 GMT`, which is 1790693241. `date -u +%s` printed 1790693240 or 1790693241 before each call
and 1790693241 or 1790693242 after it. So on this machine that moment the
two clocks differed by less than the header's one-second resolution. One
machine at one moment shows no drift, and says nothing about a machine whose
clock isn't synchronised.

### A 404 on a path GitHub doesn't route carried no rate-limit header

The 404 for `repos/meowshed/meowpaw/no-such-thing` carried no
`X-Ratelimit-*` header, while the 403 carried all five. So a response can
lack the signals, and a reader that takes a missing `remaining` as zero
reports a limit that wasn't reached.

### `--paginate` prints one header block a page, and `--slurp` with `--include` isn't JSON

`--include --paginate` printed three status lines, one a page, each followed
by its headers and body, with `X-Ratelimit-Remaining` falling from 4998 to 4996. `--include --paginate --slurp` printed `[HTTP/2.0 200 OK`, so its
output doesn't parse as JSON. Each page carried a `Link` header naming the
next page, which GitHub's best-practices page says to follow in place of
building page addresses.

### A response replayed from `--cache` carries the headers stored with it

Two `--cache 1h` reads of the same page, two seconds apart, printed the same
`Date: Tue, 29 Sep 2026 14:30:37 GMT` and the same
`X-Ratelimit-Remaining: 4992`. An uncached read straight after printed 4991.
So a replay reports the quota as it stood when the response was stored, up to
an hour earlier, and a reader that trusts it believes a spent budget is still
there.

The two cached reads of the 403 printed `Date` values two seconds apart, so
the 403 observed wasn't replayed from the cache. No 404 or 429 was read
twice through `--cache`, so whether `gh` stores those is unknown.

`gh api --help` offers `--cache` as an option and doesn't say whether a call
without it is ever cached. The one uncached read above printed a new `Date`
and a lower `X-Ratelimit-Remaining`, so that call was observed fresh. One
read shows that call wasn't replayed, and doesn't show that `gh` never caches
without the flag.

### `gh` names where its token came from, without printing it

`gh auth status --active --json hosts` lists the fields `active`,
`gitProtocol`, `host`, `login`, `scopes`, `state` and `tokenSource`, and
leaves the token out unless `--show-token` is passed. `tokenSource` read
`keyring` signed in, `GH_TOKEN` with that variable set, and `GITHUB_TOKEN`
with only that one set. `gh help environment` says `GH_TOKEN` and
`GITHUB_TOKEN` are read "in order of precedence" and take precedence over
stored credentials. So whether a variable is set, and which, decides the form
without the value being read.

Neither source says whether a token in either variable is the one GitHub
Actions issues to a workflow or a personal token a workflow passes in.
`GITHUB_ACTIONS=true` says only that the run is inside a workflow.

### `gh api` sends `POST` once a field or an `--input` body is given

`gh api --help` says the method is "`GET` normally and `POST` if any
parameters were added". It says nothing of the method when `--input` supplies
the body, though one of its examples, `gh api repos/{owner}/{repo}/rulesets
--input file.json`, creates a ruleset. `gh api --verbose markdown --input`
with no `--method` sent `POST /markdown` and got `200` with the rendered
text, and the same call with `-X GET` sent `GET /markdown` and got `404`. So
a command with `-f`, `-F` or `--input` and no `--method` is a write, and a
reader that looks only for `--method` misses it.

### GitHub says how to wait on each kind of limit error

The rate-limits page says an exceeded primary limit returns 403 or 429 with
`x-ratelimit-remaining` at 0, and an exceeded secondary limit returns 403 or
429 "and an error message that indicates that you exceeded a secondary rate
limit". The best-practices page gives the order: where `retry-after` is
present, don't retry "until after that many seconds has elapsed"; where
`x-ratelimit-remaining` is 0, wait until `x-ratelimit-reset`; otherwise "wait
for at least one minute before retrying", with "an exponentially increasing
amount of time between retries" while the secondary limit persists. It warns
that "continuing to make requests while you are rate limited may result in
the banning of your integration".

The rate-limits page gives `x-ratelimit-reset` in "UTC epoch seconds", the
secondary limits of 80 content-generating requests a minute and 500 an hour,
and point costs of 1 for most `GET`, `HEAD` and `OPTIONS` requests and 5 for
most `POST`, `PATCH`, `PUT` and `DELETE` requests. It gives `GITHUB_TOKEN`
1,000 requests an hour per repository, or 15,000 for resources of a GitHub
Enterprise Cloud account. Neither page says which endpoints generate content.
The rate-limits page says a call to `GET /rate_limit` "does not count against
your primary rate limit, but it can count against your secondary rate limit".

### GitHub asks for serial writes a second apart, and a 304 costs no primary quota

The best-practices page says to "make requests serially instead of
concurrently", and for "a large number of `POST`, `PATCH`, `PUT`, or `DELETE`
requests, wait at least one second between each request". A second between
writes keeps a run under 60 writes a minute, below the 80 content-generating
requests a minute allow. It doesn't keep a run below 500 an hour: at one write
a second, a run passes 500 in under nine minutes. The same page says a conditional request answered
`304` "does not count against your primary rate limit".

### A refusal names the permission in one of two headers, or in neither

The troubleshooting page says `X-Accepted-GitHub-Permissions` names what an
endpoint needs, as `contents=read`, as `pull_requests=write,contents=read`
for several at once, and with sets separated by `;` where any one set is
enough. The OAuth scopes page says `X-OAuth-Scopes` "lists the scopes your
token has authorized" and `X-Accepted-OAuth-Scopes` "lists the scopes that
the action checks for". The observed 403, sent with an OAuth token, carried
`X-Oauth-Scopes: admin:public_key, gist, read:org, repo, workflow`, an empty
`X-Accepted-Oauth-Scopes` and no `X-Accepted-GitHub-Permissions`, and its
body said "You must have repository read permissions or have the repository
secrets fine-grained permission." So a refusal can leave both headers empty
and name the permission only in its message.

The troubleshooting page also says GitHub answers 404 in place of 403 for a
private resource, "to avoid confirming the existence of private
repositories". So a 404 can be a missing permission.

The OAuth scopes page says the `workflow` scope "grants the ability to add
and update GitHub Actions workflow files".

### Required checks and workflow policy are set through endpoints beside branch protection

The rulesets page lists "Require status checks to pass before merging" among
a ruleset's rules, and says a ruleset controls "how users can interact with
selected branches and tags", so a required check is set through a ruleset as
well as through branch protection. The Actions permissions page lists `PUT`
endpoints under `repos/{owner}/{repo}/actions/permissions`, one of which
"sets the default workflow permissions granted to the GITHUB_TOKEN when
running workflows in a repository". So a harness that refuses only branch
protection still lets a required check or a workflow's policy change.

### Branch protection accepts a change only from a repository administrator

The branch protection page says "Protecting a branch requires admin or owner
permissions to the repository", and says the same of updating required
status checks and of admin enforcement. So GitHub itself refuses those
changes from a credential without that role. I read no such statement for
rulesets, Actions permissions or repository settings.

### Options for reading the signals

Three ways exist for a program that calls `gh` to see the limits, and doing
nothing is a fourth.

- Read the headers of every call through `--include`. It's better at
  covering every response, refusals included, at no extra request. Against
  it: the program parses the header block itself, pages by `Link` because
  `--slurp` no longer yields JSON, and has to tell a cached replay from a
  fresh response.
- Ask `rate_limit` before and after a run. It's better at simplicity, since
  one call reports every resource's primary budget. Against it: it reports
  only the primary budgets, never a `retry-after`, says nothing about the
  response that was refused, and each call still spends secondary points,
  though not primary quota, as the rate-limits page says.
- Let `gh` fail and read its standard error. It's better at needing no
  parsing. Against it: standard error carried only the message and the
  status, so neither the reset nor the permission reaches the program.
- Do nothing. It's better at costing nothing. Against it: a filing loop
  meets the content limit part way through, as RES-0133 found, and can't say
  when to try again.

## Conclusions

1. A program that calls `gh` reads limit signals from `gh api --include`,
   because standard error carries none of them and `gh api --help` describes
   `--include` as what adds "HTTP response status line and headers" to the
   output. No call was run without `--include` to show the headers absent.
2. Header names are compared without regard to case, because `gh` prints
   them in a different case from GitHub's documentation.
3. A response that carries no rate-limit header is reported as carrying none,
   never as a limit reached, because a 404 on an unrouted path carries none.
4. Pages are followed through the `Link` header one call at a time, because
   `--include` with `--slurp` doesn't print JSON.
5. A response replayed from `gh`'s cache is told apart from a fresh one, and
   its limit headers aren't read as current, because a replay carries the
   headers stored with it. This revises RES-0133's conclusion 5, that reads
   are cached because quota is the binding constraint, and both hold in part:
   reads stay cached to save quota, and a call whose limit headers have to be
   current leaves out `--cache`. A call without `--cache` was observed fresh
   on one read, so a program that relies on it still checks `Date` where a
   stale answer would mislead it.
6. `x-ratelimit-reset` is read as UTC epoch seconds and `retry-after` as a
   number of seconds from the response, because GitHub's rate-limits page
   gives those units. Measuring the reset against the response's own `Date`,
   and not against the local clock, is a choice and not a finding: it keeps
   the wait independent of the local clock, and the one comparison made here
   found the two clocks agreeing to the second.
7. A limit error with neither `retry-after` nor a zero remaining waits at
   least one minute, and longer each time it repeats, because GitHub's
   best-practices page says so and warns that it may ban an integration that
   keeps sending.
8. Writes go one at a time and at least a second apart, because GitHub's
   best-practices page asks for it. The spacing also keeps a run below 80
   content-generating requests a minute, and doesn't keep it below 500 an
   hour, which a run has to count separately.
9. The primary budget is read from `x-ratelimit-limit`, because the credential
   decides it and the response states it. This replaces RES-0133's
   conclusion 10, which assumes the 1,000-an-hour `GITHUB_TOKEN` limit inside
   a workflow: a workflow can pass in a personal token, which earns a larger
   budget, and only the response tells the two apart.
10. Which of `GH_TOKEN` and `GITHUB_TOKEN` is set, in `gh`'s order of
    precedence, names the token's source and not its form, because neither
    variable nor `GITHUB_ACTIONS` tells a workflow's own token from a personal
    one. `GITHUB_ACTIONS` wasn't observed here, since the method ran with it
    unset. The budget the token earns is read as conclusion 9 says, from
    `x-ratelimit-limit`.
11. A refusal names its permission from `X-Accepted-GitHub-Permissions`, then
    `X-Accepted-OAuth-Scopes` beside `X-OAuth-Scopes`, then GitHub's message,
    because a response can fill either header or neither. The order is a
    choice: `X-Accepted-GitHub-Permissions` names what the endpoint needs,
    while `X-Accepted-OAuth-Scopes` names only what it checks for, and a
    reader has to compare it with `X-OAuth-Scopes` to find what is missing.
12. A 404 on a resource that may be private is reported as possibly a missing
    permission, because GitHub hides a private resource behind one. A 404 on a
    public repository hides nothing and needs no such note.
13. A command with a field or an `--input` body and no method is read as a
    write, because `gh api` sends `POST` once either is given.
14. Which endpoints generate content is a choice the harness records, because
    GitHub's documentation doesn't say.
15. A harness that refuses writes to branch protection alone still lets a
    required check change through a ruleset and a workflow's policy change
    through the Actions permissions endpoints, as the finding on rulesets and
    Actions permissions shows. Which endpoints the harness treats as
    governance is left to a decision.

## Sources

- [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), read 2026-09-29 -
  403 or 429 for an exceeded primary or secondary limit, `GET /rate_limit`
  costing no primary quota, `x-ratelimit-reset`
  in UTC epoch seconds, 80 content-generating requests a minute and 500 an
  hour, 1 point for most reads and 5 for most writes, and `GITHUB_TOKEN` at
  1,000 an hour per repository or 15,000 on Enterprise Cloud.
- [Best practices for using the REST API](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api), read 2026-09-29 -
  serial requests, a second between writes, the order of waits on a limit
  error with exponential growth, the warning of a ban, a 304 costing no
  primary quota, and following `Link` headers.
- [Troubleshooting the REST API](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api), read 2026-09-29 -
  `X-Accepted-GitHub-Permissions` and its three forms, and 404 in place of 403
  for a private resource.
- [Scopes for OAuth apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps), read 2026-09-29 -
  `X-OAuth-Scopes`, `X-Accepted-OAuth-Scopes`, and the `workflow` scope.
- [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), read 2026-09-29 -
  "Require status checks to pass before merging" as a ruleset rule.
- [REST API endpoints for GitHub Actions permissions](https://docs.github.com/en/rest/actions/permissions), read 2026-09-29 -
  the repository's `PUT .../actions/permissions` endpoints, and the one
  setting `GITHUB_TOKEN`'s default permissions.
- [REST API endpoints for protected branches](https://docs.github.com/en/rest/branches/branch-protection), read 2026-09-29 -
  "admin or owner permissions to the repository" for protecting a branch and
  for updating required status checks.
- `gh` 2.101.0 on this machine, run on 2026-09-29 - `--include` output on 200,
  403 and 404, header case, `--paginate` and `--slurp` with `--include`,
  `--cache` replays, the `repos/{owner}/{repo}` placeholder, `Date` beside
  `date -u +%s`,
  `gh auth status --json hosts` and its `tokenSource`, the method sent with
  `--input` and no `--method`, and the help of
  `gh api` and `gh help environment`.
