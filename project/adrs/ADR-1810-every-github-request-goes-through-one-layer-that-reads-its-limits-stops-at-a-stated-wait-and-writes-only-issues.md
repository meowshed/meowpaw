---
id: ADR-1810
artifact: adr
status: approved
revised: 2026-09-29
addresses:
  [REQ-2566, REQ-2568, REQ-2572, REQ-2574, REQ-2576, REQ-2578, REQ-2582]
postpones: [REQ-2580]
supersedes: []
---

# 1810. Every GitHub request goes through one layer that reads its limits, stops at a stated wait, and writes only issues

## Decision

**Amended by ADR-2320.** The read-back listing's `<start>` is the earliest
`updated_at` among the run's create answers, and the `Date` of the run's first
response only where no create answer carries one.

**Amended by ADR-2330.** Every refusal line ends with GitHub's own reason, and
after a 401 the run sends no further request.

`meow-github` sends every request to GitHub through one request layer,
`crates/meow/src/github/request.rs`, and no other code in the crate's `github`
feature starts `gh`. The layer runs `gh api --include`, so it gets the status
line, the headers and the body of every response, a refused one included,
because `gh` prints a refused call's headers on standard output and only its
message on standard error (RES-0290). `history`, `project` and naming the
repository all go through it:

- Naming the repository reads `repos/{owner}/{repo}` through the layer, where
  it ran `gh repo view`, because `gh repo view` shows no headers.
- `history` follows each listing's `Link` header, one page a call, in place of
  `--paginate --slurp`, because `--include` with `--slurp` prints text that
  isn't JSON (RES-0290). Reads keep `--cache 1h` (REQ-2564), except a run's
  first call, which the next section needs fresh.

### What the layer reads

On every response the layer reads `x-ratelimit-limit`,
`x-ratelimit-remaining`, `x-ratelimit-used`, `x-ratelimit-resource`,
`x-ratelimit-reset`, `retry-after` and `Date`, comparing names without regard
to case, because `gh` prints `X-Ratelimit-Remaining` where GitHub's
documentation writes `x-ratelimit-remaining` (REQ-2566). A response that
carries none of them is recorded as carrying none, and the run goes on,
because RES-0290 saw a 404 on an unrouted path carry no rate-limit header,
and reading that as a limit reached would stop a run for nothing.

Only a call sent with `--cache` is treated as a possible replay, because
RES-0290 observed an uncached call reach GitHub. The layer sends a run's first call
without `--cache`, whichever call that is, and records the offset between
that response's `Date` and the local clock when the response arrived. Each
later uncached response, every write among them, records the offset again. A
cached response is a replay when its `Date` is 60 seconds or more before the
moment the layer started the call, with that moment moved onto GitHub's clock
by the offset. The layer doesn't read a replay's limit headers as current and
doesn't count it as a request, because RES-0290 saw a replay carry the headers
stored with it, `Date` included, up to an hour old.

The offset takes the local clock's error out of the test, so a local clock
running minutes ahead of GitHub's doesn't make every fresh response look like
a replay. The test tolerates any fixed skew, and less than 60 seconds of
change in the skew between two uncached responses. RES-0290 found this
machine's clock and GitHub's `Date` agreeing to the second, so the offset is
a guard for a machine whose clock isn't synchronised, not a correction this
one needed.

### How a wait is derived

Every wait goes through one table naming the unit GitHub documents for each
header, and no other code converts a header into a duration (REQ-2578):

| Header              | Unit GitHub documents | The wait it gives                                            |
| ------------------- | --------------------- | ------------------------------------------------------------ |
| `retry-after`       | seconds               | that many seconds from when the response arrived             |
| `x-ratelimit-reset` | UTC epoch seconds     | the reset minus the response's `Date`, from when it arrived  |
| `Date`              | HTTP date             | none; it is the reference `x-ratelimit-reset` is measured to |

A wait is measured against the response's own `Date`, so a local clock
running behind GitHub's doesn't shorten it. A value that doesn't parse in its
unit gives no wait, and the run reports the wait as unknown and sends nothing
more, because a guessed wait is either too short or invented. The table is
keyed by service, so a later pack for a service that counts in milliseconds,
as RES-0134 found Linear does, adds rows under its own name and changes none
of these.

### When the run is throttled

A response is throttled when it is a 429, or a 403 carrying `retry-after`,
`x-ratelimit-remaining: 0` or a message naming a secondary rate limit
(RES-0290). The wait is `retry-after` where it is present, and the reset
where `remaining` is 0. Otherwise it is 60 seconds, doubled for each further
secondary throttle in the same run, because GitHub's best-practices page asks
for that and warns that it may ban an integration that keeps sending
(RES-0290). A
fresh response with `remaining` at 0 holds the next request to the same
resource the same way, because sending it would only earn the 403.

By default the run stops at a throttle: it sends nothing more, the read-back
listing included, prints
`throttled: <method> <endpoint>, retry after <UTC time> (<header>)` and exits
3, so it honours a stated wait by not retrying at all (REQ-2566). Exit 3 is
the status `meow-github` already gives a run that stopped before finishing,
as its README states for `unread`, so every stop this decision adds uses it. With
`--wait`, which both commands accept, the layer sleeps until that time and
never less, and sends the throttled request again. Before each sleep it adds
the wait to the waits the run has already slept, and where the total would
pass an hour it doesn't start the sleep and stops as throttled. A primary
reset is at most an hour away, so a run still throttled after an hour of
waiting has another cause, and a person should see it.

### The budgets

The layer keeps four counts for the run, checks them before each request, and
prints them as the last lines of every run's report (REQ-2568):

- Primary requests: the requests this run sent, and for each
  `x-ratelimit-resource`, the limit, remaining and reset the last fresh
  response stated. The limit is read from `x-ratelimit-limit`, so a credential
  held to 1,000 an hour inside a GitHub Actions workflow, or to 5,000 or 15,000
  elsewhere, is reported as GitHub states it, and never assumed from the form.
- Secondary points: 1 for each `GET` and 5 for each other method, over the
  last minute, against 900 (RES-0133 for the ceiling, RES-0290 for the
  weights).
- Content creation: each `POST`, over the last minute against 80 and over
  the last hour against 500 (RES-0290). GitHub doesn't say which endpoints
  generate content (RES-0290), so I count every `POST`, which overcounts and
  stops a run early where the other choice stops it late, at GitHub's
  throttle.
- Spacing: the layer sends writes one at a time, each at least one
  second after the previous one, as GitHub's best-practices page asks
  (RES-0290). A run therefore creates at most 60 issues a minute, so the hour's
  500 is the content ceiling that stops it, and the minute's 80 never is.

A request that would pass a ceiling isn't sent: the run stops as it does at a
throttle, naming the count and when it frees. Each count covers this run
alone. Another run, or a person on the same account, spends the same budgets
where the layer can't see it, and GitHub's throttle is what reports that.

`project` reads its created issues back through one listing after its last
create, `repos/{r}/issues?state=all&since=<start>&per_page=100`, uncached and
paged, and matches each created issue by number. `<start>` is the `Date` of
the run's first response, which is uncached and arrives before any create, so
the listing's window is measured on GitHub's clock and a local clock running
ahead can't leave out the run's first issues. It spends at
least one read for each 100 issues where it spent one for each issue, because
RES-0133 found a read-back after every write is no cheap safety measure. The
listing also returns pull requests and every issue anyone else updated during
the run, so its cost grows with the repository's activity as well as with
the issues this run created. A created issue the listing lacks or reads
differently is reported with what the listing showed, in a complete run as in
a partial one. After a failed write or a refusal the listing still runs, because neither
asks the run to stop sending. After a throttle or a ceiling it doesn't,
because GitHub's best-practices page warns that a request sent while
throttled may get the integration banned (RES-0290), and a ceiling reached
means the run's budget is spent. REQ-1368 still holds, since each link is read
back from the tracker, in this run's listing or through its mapping in the
next run.

### What it changes in ADR-1310

ADR-1310 reads each issue back straight after creating it. This decision reads
them in the one listing above instead. The read of an issue already mapped to
a task, which decides whether it was edited on GitHub, is unchanged.

### A partial run

Whenever `project` stops before it has visited every task, at a throttle, a
ceiling, a refusal or a failed write, it prints
`partial: projected TSK-a; created, not read back TSK-b; not projected TSK-c`
and exits 3 (REQ-2572). It prints the line after the read-back listing, where
the listing runs, so each list says what the listing showed. A task counts as
projected when its issue was updated or found unchanged in this run, or was
created and the listing read it back matching the record. A task whose issue
was created and then was missing from the listing, read back differently, or
not read back because the run stopped at a throttle or a ceiling, goes on the
`created, not read back` list, with what the listing showed where it ran. Its
task holds the mapping, so the next run reads that issue back through it and
doesn't create a second one. A run of `project`
again continues from the mapping on each task, so the tasks already projected
cost one read each. `history` keeps ADR-1290's rule: it prints no document
when it stops and names the listings it read.

### A refusal

A 401 is reported as `unauthenticated: <method> <endpoint>`. A 403 that
isn't a throttle is reported as `refused: <method> <endpoint> needs
<permission>` (REQ-2574). A 404 on an object the record says exists is
reported the same way with `, or it is hidden from this credential` added,
because GitHub answers 404 for a private resource (RES-0290). The
permission comes from `X-Accepted-GitHub-Permissions`, and otherwise from
`X-Accepted-OAuth-Scopes` beside the credential's own `X-OAuth-Scopes`.
Where both are empty, as RES-0290 saw on a 403, it prints
`GitHub named no permission` and quotes GitHub's message. Each exits 3.

### The credential's form

The first line of `project`'s report names the form of authentication
(REQ-2582): `GH_TOKEN from the environment`, `GITHUB_TOKEN from the
environment` or `gh's stored credential`, taken in the order of precedence
`gh` documents, with `, inside a GitHub Actions workflow` added when
`GITHUB_ACTIONS` is `true`. The layer reads whether each variable is set and
never its value, because the value is secret material (RES-0133). The form
says what `gh` sent. Which budget that earned is the `x-ratelimit-limit` in
the budget lines, because inside a workflow either variable can hold the
workflow's own token or a personal one, and only GitHub's answer tells them
apart (RES-0290).

`history` puts the form and the budgets into its document as the fields
`credential` and `budget`, because its standard output is one JSON document
that onboarding parses. Onboarding reads its fields by name, so two more
change nothing it reads.

### Governance

The layer sends a write only to an endpoint on its allow list, which holds the
two writes the crate builds: `POST repos/{r}/issues` and
`PATCH repos/{r}/issues/{n}` (REQ-2576). Any method other than `GET` to any
other path is refused before `gh` starts, as
`refused by meow-github: <method> <endpoint> isn't a write this pack makes`.
A later decision that adds a write adds its endpoint in the same change.

The crate also holds a governance list, and a unit test fails if any
allow-list entry matches it. Every entry but the fifth is a path through which
RES-0133 or RES-0290 found repository settings, a required check, a workflow's
policy or a workflow file can change. The fifth is my own choice, since no
research lists it:

- `repos/{o}/{r}` itself, which holds the repository's settings;
- `branches/{b}/protection` and everything under it;
- `rulesets` and everything under it, for a repository and for an
  organisation;
- `actions/permissions` and everything under it, `actions/workflows/{id}/enable`
  and `actions/workflows/{id}/disable`;
- `actions/secrets`, `actions/variables`, `environments`, `hooks` and
  `collaborators`, which change what a workflow receives or who can change the
  rest;
- `contents/.github/workflows/` and everything under it, which writes a
  workflow file without a pull request.

The model can run `gh` itself, which the layer never sees, so `meow-github`
also ships a `PreToolUse` command hook on Bash. It runs
`meow-github governance-guard` on every Bash command that contains `gh` as a
word, and the guard splits the command at `&&`, `||`, `;`, `|` and each new
line. In each part it skips leading variable assignments, such as
`GH_TOKEN=x`, and a leading `env` with its assignments, and looks at the part
only if the next word is `gh`. It answers `ask` when a part changes something
on the governance list, or can change it where the guard can't see what it
sends. Such a part is one of these:

- `gh api` to a path on the list with a method other than `GET`, or with a
  field or an `--input` body and no method, since `gh` then sends `POST`
  (RES-0290);
- `gh api graphql` whose query contains `mutation`, or whose query the guard
  can't read because it comes from a file or from standard input, since one
  mutation can change branch protection or a ruleset through a path that
  isn't on the list;
- `gh repo edit`, `gh repo rename`, `gh repo archive` or `gh repo delete`,
  which change the repository itself;
- `gh workflow enable` or `gh workflow disable`;
- `gh secret` or `gh variable` with `set` or `delete`.

The reason it gives names the method and the endpoint and never the command,
because a command can carry a token in front of it. For anything else it prints
nothing and exits 0, which leaves the call to the normal permission flow
(RES-0203).

I chose `ask`, because REQ-2576 forbids the change unless someone asked for
it, and a person approving the prompt has asked. Where nobody can answer, a
run under `--permission-prompts none` denies what would prompt (RES-0299). A
workflow file edited in the work tree reaches the repository only through a
pull request, whose reviewer sees it as a diff, so the hook leaves Edit and
Write alone.

REQ-2576's reason is that governance and work aren't approved by the same
person, and the prompt goes to whoever runs the session, who is usually the
person approving the work. The hook can't tell whether that person holds the
governance role, so `ask` meets the requirement's wording and not its reason.
Part of what stands behind it is GitHub's own check: branch protection and
required status checks accept a change only from a credential with admin or
owner permissions on the repository (RES-0290), and the repository owner
decided who holds those. Where the session's person holds them, they are a
governance approver by the owner's grant, and where they don't, GitHub
refuses the change whatever the prompt said. RES-0290 read no such statement
for rulesets, Actions permissions or repository settings, so for those the
prompt is the only guard. The cost falls on the repository owner, who has to
keep administration rights away from anyone who shouldn't approve
governance, because the hook won't do it for them.

### Postponed

REQ-2580 is postponed. It applies where a service bills by query cost, and
the harness calls one service, GitHub, only through REST, which counts
requests (RES-0133). Linear's complexity budget is the case the requirement
describes (RES-0134), and no Linear pack exists. It comes with the decision
that adds a pack for a service billing by query cost, or a `meow-github`
command that reads through GitHub's GraphQL interface in a loop over items.

### What works, and what doesn't yet

After this decision a throttled `project` stops, says when to try again and
lists what it projected and what it didn't, and a second run continues from
there. Every run names its credential's form and its budgets, and a refusal
names the permission it wanted. The pack writes only issues, and a `gh`
command the model runs against governance asks the person first. What still
doesn't work:

- A budget spent by another run or by a person on the same account is seen
  only when GitHub throttles.
- A `POST` whose response was lost, to a network failure, may have created an
  issue with no mapping on its task, and the next run creates a second one.
- Governance changed through something other than `gh`, such as `curl` with a
  token, isn't caught, and a bare unattended run, which skips plugin hooks
  (RES-0299), isn't guarded by the hook.
- A `gh` the guard's split doesn't reach isn't caught: one inside a subshell,
  `eval`, `xargs`, a script file or a shell function, or one named through a
  variable or an alias.
- The hook asks the session's person, and can't tell whether that person
  holds the governance role REQ-2576's reason separates from the work.

## Why

RES-0133 found the content limit is the one a large epic hits part way, that
`retry-after` is an instruction, that a write costs five times a read, and
that token scope stays invisible until a call needs it. RES-0290 observed how
`gh` 2.101.0 shows each of those to a program: only under `--include`, with a
cache that replays stale headers, with header names in a different case, and
with a refusal that can name its permission in neither header.

One layer, because a rule each call site keeps is a rule the next call site
misses. The decisions planned for milestones, pull requests and stacks each
add a write, and each gets the budgets, the waits and the allow list by
calling the layer.

Stopping is the default, because a run that sleeps up to an hour holds its
session and its spend while nobody is told. The person who starts it chooses
`--wait` knowing that.

The strongest objection is that the allow list makes every later write a
change in two places, and that the hook reads shell text, which a variable,
an alias, a subshell, a script or `--method=PUT` written in an unexpected
form can slip past. I
accept both: a missing allow-list entry fails its own fixture the first time
it runs, and the hook is the second guard, behind the layer, for the calls the
model makes by hand.

## Alternatives

| Option                                          | Better at                                 | Why it lost                                                                                                                                 |
| ----------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| A retry loop inside each command                | Fewer lines now                           | Each call site repeats the wait rules and their units, and a retry by default spends the budget GitHub asked the run to keep                |
| Read `rate_limit` before and after a run        | One extra call, no header parsing         | It carries no `retry-after` and nothing about the refused call, so neither REQ-2566's wait nor REQ-2574's permission is reached             |
| Wait by default                                 | A run finishes with nobody watching       | Holds a session up to an hour unasked, and an unattended run's spend with it                                                                |
| A skill carrying RES-0133's rules for the model | Covers every way the model reaches GitHub | Costs context on every turn and an evaluation loop, and advises where the hook asks a person each time                                      |
| The hook answers `deny`                         | Nothing reaches GitHub, even approved     | REQ-2576 allows a change someone asked for, and a person would have to leave the session to make it                                         |
| Keep one read-back per created issue            | The read follows its write at once        | Doubles the primary requests each create spends, competes with the read of each mapped issue, and RES-0133 found it no cheap safety measure |
| Do nothing                                      | No change                                 | Seven requirements stay unmet, and a throttled `project` says "stopped part way" with no wait and no list                                   |

## What it costs

Whoever runs `project` waits at least a second for each write, so projecting
80 tasks takes at least 80 seconds. A throttled run goes back to the person who
started it. Left alone for a month, it has lost nothing: it exited 3, its
report names what is left, and the next run continues from each task's
mapping.

`history` starts one `gh` process a page where it started one a listing, and
spends the same requests. Onboarding gets two more fields in the document.

Every Bash command containing `gh` as a word starts `meow-github` once more,
for the hook. A command hook loads nothing into context, so the unit's budget
stays at 0 characters. The person who wants a governance change answers one
prompt for each such command, and one for every GraphQL mutation, since the
guard doesn't tell a governance mutation from any other.

The repository owner pays for the hook's blindness to roles: whoever runs
the session answers the prompt, so keeping governance with the right people
rests on who the owner gives administration rights to.

A run's first call goes to GitHub even when the cache holds its answer, so a
run spends at most one request more than it did. A replay from the cache less
than a minute old is counted as a fresh request, and its `remaining` read as
current, so a count can run one request high and a `remaining` a minute
stale. Both err towards stopping early. A local clock that jumps by a minute
or more during a run, between two uncached responses, can make the replay
test read a fresh response as a replay or the other way round.

Whoever maintains the crate keeps the allow list and the governance list, and
each later write adds one entry and one fixture.

## What would reverse it

- I would drop the parsing of `--include` if `gh` reported a response's limit
  headers in a structured form of its own.
- I would count only the endpoints GitHub names once it documents which
  requests generate content.
- I would drop the 60-second `Date` test if `gh` marked a cached replay or
  stopped storing headers with it.
- I would make waiting the default once an unattended run's declared
  authority names a longest wait, because the person would then have chosen it
  before the run.
- I would make the hook answer `deny` if a prompt the hook raises were ever
  allowed with no person to answer it, because `ask` would then no longer mean
  a person asked.
- I would route the hook's prompt to a named governance approver, or answer
  `deny`, if the repository owner and the people running sessions were
  routinely different people with administration rights, because the prompt
  would then reach someone REQ-2576's reason doesn't mean.

## Consequences

- A module `crates/meow/src/github/request.rs` holding the layer, the unit
  table, the counts, the allow list and the governance list; `gh()` in
  `github.rs` goes, and `history` and `project` call the layer.
- `--wait` on `history` and `project`.
- `meow-github` gains `hooks/hooks.json` and a `governance-guard` command, and
  raises its minor version, because its behaviour changes.
- Its README gains the credential line, the budget lines, `partial`,
  `--wait`, and in the hand path the headers to read and the one-second
  spacing between writes.
- SPC-1080's section on projecting and its failure table, which the spec step
  rewrites to state the layer, the reports and both lists.
- ADR-1310's read-back after each create becomes one listing, as stated above.
- The stand-in `gh` in `plugins/meow-github/tests/test_github.py` prints a
  header block under `--include`, and takes an injected clock.

## How I will know it was realised

1. A stand-in `gh` answering a create with 403 and `retry-after: 30` makes the
   run print `throttled`, the endpoint and the time 30 seconds after the
   response, exit 3, and send no further call. With `--wait` and an injected
   clock, the stand-in records the next call no earlier than 30 seconds after
   it. With `--wait`, a first throttle of 3,540 seconds followed by one of
   120 seconds makes the run sleep the first, start no second sleep, and stop
   as throttled (REQ-2566).
2. A unit test derives 3,207 seconds from `x-ratelimit-reset` 1790695444
   against a `Date` of 1790692237, the pair RES-0290 observed, and would get
   about 3.2 seconds, or a date in 1970, if the value were read as
   milliseconds. A `retry-after` that isn't a number of seconds gives an
   unknown wait and no further call (REQ-2578).
3. A response with no rate-limit header is reported as carrying none and the
   run goes on. A replay whose `Date` is ten minutes old isn't counted and its
   `remaining` isn't reported as current. With the injected local clock two
   minutes ahead of the stand-in's `Date`, a fresh cached response is counted
   and its `remaining` reported as current, and the run's first call carries
   no `--cache` (REQ-2566).
4. With 501 unmapped tasks, the stand-in records 500 creates and the run stops
   before the 501st, naming content creation at 500 of 500 this hour. The
   stand-in's timestamps show writes at least a second apart. The budget lines
   name each of the four counts, and with `x-ratelimit-limit: 1000` and
   `GITHUB_ACTIONS=true` the primary line names 1,000 (REQ-2568).
5. The stand-in failing the third create makes the run send the read-back
   listing for the first two, then print `partial: projected` with those two
   and `not projected` with the rest, and exit 3. With the injected local
   clock two minutes ahead of the stand-in's `Date`, the listing's `since` is
   the first response's `Date` and both issues are read back. The stand-in
   answering the third create with a secondary throttle makes the run send no
   listing, and print the first two under `created, not read back` and the
   rest under `not projected`. A created issue the listing omits goes under
   `created, not read back` (REQ-2572).
6. A 403 carrying `X-Accepted-GitHub-Permissions: issues=write` is reported
   with `POST repos/o/r/issues` and `issues=write`. One carrying only the
   OAuth scope headers names the accepted scopes and the credential's own,
   and one carrying neither quotes GitHub's message. A 404 on a mapped issue
   adds that it may be hidden from this credential (REQ-2574).
7. `GH_TOKEN` set, only `GITHUB_TOKEN` set, and neither set yield the three
   forms on the first line, and `GITHUB_ACTIONS=true` adds the workflow. A
   sentinel token value in either variable appears nowhere in the output
   (REQ-2582).
8. A unit test shows the layer refusing `PATCH repos/o/r`,
   `PUT repos/o/r/branches/main/protection`, `POST repos/o/r/rulesets`,
   `PUT repos/o/r/actions/permissions/workflow` and
   `PUT repos/o/r/contents/.github/workflows/ci.yml` without starting `gh`,
   and no allow-list entry matching the governance list. A source test finds
   every method and endpoint the crate builds on the allow list (REQ-2576).
9. Hook fixtures answer `ask` to `gh api -X PUT
repos/o/r/branches/main/protection`, `gh api repos/o/r/rulesets -f name=x`,
   `gh api repos/o/r/rulesets --input rs.json`,
   `gh repo edit --visibility private`, `gh repo archive`,
   `gh api graphql -f query='mutation { x }'`,
   `GH_TOKEN=x gh api -X PUT repos/o/r/branches/main/protection`,
   `env GH_TOKEN=x gh repo delete o/r` and
   `git status && gh api -X PUT repos/o/r/rulesets/1`, and print nothing for
   `gh api repos/o/r/issues` and `gh api graphql -f query='{ viewer { login } }'`.
   The token in front of a refused command appears nowhere in the hook's
   output (REQ-2576).
10. Every requirement ADR-1810 addresses lands in exactly one closed task, and
    REQ-2580 reads as postponed.

## What this does not settle

- REQ-2580, until a pack or command reads by query cost.
- GitHub's GraphQL budget of 2,000 points a minute, since no command sends
  GraphQL.
- Budgets spent by another run or a person on the same account.
- An issue created by a `POST` whose response was lost.
- Governance changed by a command other than `gh`, or by a `gh` the guard's
  split doesn't reach, and a bare unattended run, which ADR-2000's declared
  authority bounds in place of the hook.
- Whether the person answering the hook's prompt holds the governance role.
- Conditional requests, which a 304 answers without spending primary quota
  (RES-0290).
- The skill RES-0133 describes for the model. Its first rule, the
  three-valued status, belongs to the decision that addresses REQ-2570.
