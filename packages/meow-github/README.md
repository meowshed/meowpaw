---
reader: someone installing or running meow-github on Pi
answers: what meow-github provides, what it adds to a session and how to install it
kind: reference
describes: [@meowshed/meow-github@0.18.0]
---

# @meowshed/meow-github

Reads a GitHub repository's issues, pull requests and comments through gh as one JSON document, projects an approved decision or defect onto its one issue, retires the issues of archived tasks after an upgrade, and asks before a Bash command's gh changes how the repository is governed. Distributed as a Pi package.

## Install it

```bash
pi install npm:@meowshed/meow-github
```

The paw executable ships with `@meowshed/meow-core` alone (REQ-4612): this
package's launchers run their subcommands through it, so install the core
package beside this one for the binary-backed checks. Without it, every
check reports unrun and lets the command through.

```bash
pi install npm:@meowshed/meow-core   # carries the binary the launchers run
```

Installing from this repository's checkout is the development install: it
loads the package in place and runs no lifecycle script.

The pack is current as of gh 2.101.0, observed on 2026-10-24.

## Read a repository's history

In a clone, or naming the repository:

```bash
meow-github history
meow-github history meowshed/meowpaw
```

It reads four listings, every page of each, and keeps each response for an
hour so a second read costs no quota:

```json
{
  "repository": "meowshed/meowpaw",
  "issues": [
    {
      "number": 2,
      "kind": "pull request",
      "merged": true,
      "title": "...",
      "body": "...",
      "state": "closed",
      "author": "...",
      "url": "...",
      "labels": []
    }
  ],
  "comments": [{ "on": 3, "author": "...", "body": "...", "url": "..." }],
  "review_comments": [
    { "on": 2, "path": "...", "author": "...", "body": "...", "url": "..." }
  ],
  "credential": "gh's stored credential",
  "budget": [
    "primary requests: 5 sent; core limit 5,000, 4,995 remaining, resets 2026-09-29T15:30:37Z",
    "secondary points: 5 of 900 this minute",
    "content creation: 0 of 80 this minute, 0 of 500 this hour",
    "spacing: 0 writes, each at least one second after the previous one"
  ]
}
```

`merged` is `false` for a pull request closed without merging, which records a
rejected approach, and `null` for an issue. `credential` and `budget` are the
credential line and the budget lines that
[Credential and budgets](#credential-and-budgets) describes.

## Project a record onto its issue

Declare the tracker in `.meowpaw/profile.toml` first. Without it the command
says so and does nothing, and nothing in the method needs a tracker:

```toml
[tracker]
kind = "github"
```

The command opens by naming the profile's state, as
`meow-github project: profile: parsed`, and each key no unit reads, as
`meow-github project: unknown key: <path>`, which changes no exit status.

Once a decision or a defect is approved, file its one issue:

```bash
meow-github project ADR-1310
meow-github project BUG-1210
```

The issue's title is the record's identifier and title. Its body names the
record, the requirements a decision addresses or a defect violates, and the
record's `## Plan`, and ends with a marker naming the record and a fingerprint.
The record gains `issue:` with the issue's number, and `projected:` and
`tracked:` with the fingerprints, so the mapping lives in the repository. Write
`Closes #<issue>` in the pull request body, because the merge is what closes that
one issue. After its last create, the run reads the issue it created back in one
listing of the issues written since the `updated_at` GitHub gave it, and matches
it by number. Where the create's answer doesn't state that time, the listing
starts at the `Date` of the run's first response. The listing can lag a create by
seconds, so the run reads an issue it left out on its own, by number, before it
reports that issue as not read back. Run it again and nothing changes. It refuses
a record that isn't approved.

Where a run stops before it has projected the record, or neither the listing nor
a read by number shows a created issue as it was written, the report says which
state the record is in and the run exits 3:

```text
partial: projected none; created, not read back ADR-1310 (issue #512, reads differently from what was written); not projected none
```

| Group                    | Holds a record whose issue                                                |
| ------------------------ | ------------------------------------------------------------------------- |
| `projected`              | Was updated, was found unchanged, or was created and read back as written |
| `created, not read back` | Was created and not confirmed, with the issue's number and the reason     |
| `not projected`          | Was not visited                                                           |

A group with no record reads `none`. The reason is `couldn't be read`,
`reads differently from what was written`, `the listing couldn't be read`,
`the listing was throttled`, `the listing's credential was rejected`,
`no listing ran`, `no read ran` or
`the record doesn't name it`.
The run sends the listing after a write GitHub refused, and sends none after a
throttle, a budget ceiling or a 401, where it sends nothing more at all. A record
under `created, not read back` keeps its `issue:`, so the next run reads that
issue through the mapping and creates no second one. The one exception is
`the record doesn't name it`: the issue exists and the record's file couldn't be
written, so set `issue:` on the record by hand before the next run.

The record owns the issue's title and body. `project` and `sync` never write
whether an issue is open or closed, and only `upgrade` closes one. A record you
changed updates its issue on the next run. An issue someone edited on GitHub is
reported and left as it is, and an issue closed on GitHub while its record isn't
done is reported, because `paw done` decides that state. Add `--check` to see the
record's state without writing anything:

```bash
meow-github project ADR-1310 --check
```

## Synchronise a record and its issue

`project` writes the record to its issue. `sync` also takes a change made on
GitHub back into the record, by a fingerprint of each side taken at the last
synchronisation and not by a clock, because GitHub keeps one time for a whole
issue. The mapping carries both: `projected:` for the record side and
`tracked:` for the tracker side, which an older record gains at its next run.

```bash
meow-github sync ADR-1310
meow-github sync ADR-1310 --check
```

For a record that `project` has mapped, `sync` finds which side changed since
the last run:

| Changed since the last run | What `sync` does                                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Neither                    | Reports `unchanged`                                                                                         |
| The record only            | Updates the issue to what the record says                                                                   |
| The issue only             | Writes the issue's title into a draft record; reports the difference for an approved one and writes nothing |
| Both                       | Writes the record's text to the issue, because the record wins a conflict                                   |

The body of an issue is derived from the record's requirements and its plan, so
a body edited on GitHub isn't written into the record, and the record's body
goes back to the issue. An approved record's wording is never written from the
tracker, which the method forbids; the difference is reported and `sync` exits 1.
An issue closed on GitHub while its record isn't done is reported and not
reconciled, and `sync` exits 1, because the record decides when its work is done.
`--check` prints what the record would get and writes nothing.

The method runs `sync` at the start and the end of a record's work, where a
tracker is declared, and nothing runs it in the background.

## Retire the issues of archived tasks

Run `upgrade` after the pull request of `paw upgrade --write` has merged, because
an issue closed earlier could name a plan that is never merged.
`/meow-flow:upgrade` runs it for you, and `--check` previews it and writes
nothing:

```bash
meow-github upgrade --check
meow-github upgrade
```

| Archived task                     | Its issue is open                                                                        | Its issue is closed            |
| --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------ |
| Done                              | Closed as `completed`                                                                    | Left alone                     |
| Withdrawn, rejected or superseded | Closed as `not_planned`                                                                  | Left alone                     |
| Open, with `folded-into:`         | The record's issue is created first, then this one is closed as `not_planned`, naming it | Left alone, and reported       |
| Open, with no `folded-into:`      | Left open, and reported as needing a decision                                            | Reported as needing a decision |

An issue that maps to no task stays as it is, and a defect's issue stays its
issue. Each close is one write that prepends the notice to the body and sets the
state, so an interrupted run leaves no issue half changed and the next run skips
what is already closed. The command lists each open pull request whose title or
body names a folded task and changes none of them: rebase that branch and move
its plan to the record by hand. It exits 1 with no archived task, and 1 where an
open task needs a decision.

## Report the trunk's protections

`protections` reads the protection of the trunk `.meowpaw/profile.toml`
declares as `[git] trunk`, and the rules in force on that branch, and prints
which of six protections are in force. It changes nothing, because which
protections the trunk should have is the repository owner's decision. In a
clone, or naming the repository:

```bash
meow-github protections
meow-github protections meowshed/meowpaw
```

The report opens with the credential line and the profile's state, gives one
line for each protection in this order, and ends with the four budget lines
that [Credential and budgets](#credential-and-budgets) describes:

```text
credential: gh's stored credential
meow-github protections: profile: parsed
force pushes blocked: in force
deletion blocked: in force
required reviews: absent
required checks: in force
signed commits: absent
linear history: in force
primary requests: 3 sent; core limit 5,000, 4,997 remaining, resets 2026-09-29T15:30:37Z
secondary points: 3 of 900 this minute
content creation: 0 of 80 this minute, 0 of 500 this hour
spacing: 0 writes, each at least one second after the previous one
```

A protection that the branch protection or a ruleset sets is `in force`. Where
GitHub answers 404 for the branch protection, the branch has none, and the
rules are still read. Where a read is refused or throttled, the report prints
the `refused:` or `throttled:` line [When it can't read](#when-it-cant-read)
describes, names each protection it couldn't read as `unread`, never as
`absent`, and exits 3. Where the profile declares no trunk, the report says
so and exits 3.

To read the same thing without the pack, run the two reads it sends:

```bash
gh api repos/OWNER/REPO/branches/main/protection
gh api repos/OWNER/REPO/rules/branches/main
```

## Project a record by hand

You can file a record's issue without the pack and get the same issue and the
same mapping, so installing the pack later continues your record instead of
duplicating it. Write the body as the pack does: `The work of <id>.`, then
`Names <requirements>.`, then the record's `## Plan` under that heading. Then:

```bash
title="ADR-1310: The GitHub pack projects a record onto its issue"
fingerprint=$(printf '%s\n%s' "$title" "$body" | shasum -a 256 | cut -c1-12)
gh api repos/OWNER/REPO/issues -X POST -f title="$title" -f body="$body

<!-- meow-github: projected from ADR-1310 at $fingerprint -->"
```

Set the record's `issue:` to the number GitHub returns and add
`projected: <fingerprint>` beside it.

## When it can't read

Where `gh` is missing, isn't signed in, or GitHub refuses a listing, it prints
`unread`, names the listing that failed and what GitHub said, lists what it
read before it stopped, and exits 3. It prints no document then, because a part
of the history would read as the whole of it. It prints the credential line
first and the four budget lines last, as text, as
[Credential and budgets](#credential-and-budgets) describes. Where its binary
is missing for your machine, it names the machine and says to reinstall the
unit.

Where GitHub refuses a call, `history` and `project` name the method, the
endpoint and the permission the call needed, carry GitHub's own reason, and
exit 3:

```text
unauthenticated: POST repos/OWNER/REPO/issues; GitHub said "Bad credentials"
refused: POST repos/OWNER/REPO/issues needs issues=write; GitHub said "Resource not accessible by personal access token"
refused: GET repos/OWNER/REPO/issues/512 needs a permission: GitHub named no permission and said "Not Found", or it is hidden from this credential
```

| Line                                     | GitHub answered                                                                              |
| ---------------------------------------- | -------------------------------------------------------------------------------------------- |
| `unauthenticated: <method> <endpoint>`   | 401: the credential is missing, expired or revoked                                           |
| `refused: <method> <endpoint> needs ...` | 403 that isn't a throttle                                                                    |
| The same, ending `, or it is hidden ...` | 404 on an issue a record maps, which GitHub also gives for an issue the credential can't see |

After `needs`, the line gives the permission as GitHub named it, from the
first of these the response carries:

- `X-Accepted-GitHub-Permissions`, as it stands, such as `issues=write`;
- `X-Accepted-OAuth-Scopes` beside the credential's own `X-OAuth-Scopes`, as
  `one of the scopes repo; the credential holds read:org, gist`;
- neither, as `a permission: GitHub named no permission and said "..."`, with
  GitHub's message quoted.

A line that doesn't already quote GitHub's message ends with
`; GitHub said "<message>"`, because a permission header says what an
endpoint accepts and not why this credential was refused. After a 401 the
run sends nothing more, the read-back listing included, because GitHub
rejects an account's valid credentials too after several rejected requests.
`project` then prints `stopped at the rejected credential above` and the
`partial:` line.

Wherever a line quotes GitHub's message, a control character or a line
separator in it prints as a space, and a backslash or a double quote is
escaped, so the message can't split the line or end its quotation.

`project` prints the line on a line of its own, above the line saying what the
refusal stopped: a record, the naming of the repository or the read-back.
`history` prints it after `unread:`, and after the listing's name where a
listing was refused.

Every call goes through one request layer that reads GitHub's rate-limit
headers on each response. Where GitHub throttles a call, or a fresh response
says the limit is spent, `history` and `project` send nothing more, print
`throttled: <method> <endpoint>, retry after <UTC time> (<header>)` and exit
3, because a call sent while throttled can get the integration banned. Where
the header doesn't parse as its unit, the line says the time is unknown. Add
`--wait` to either command to sleep until that time and send the call again:

```bash
meow-github project ADR-1310 --wait
```

A run sleeps an hour at most in all, because a primary limit resets within an
hour and a run still throttled after that has another cause. It stops as
throttled at the wait that would pass the hour.

## Credential and budgets

GitHub's limits differ by how a run signs in, so every run names the form of
its credential. The first line of `project`'s report is `credential: <form>`,
and `credential` in `history`'s document is the form alone. The form is one of
these, in the order `gh` prefers them:

- `GH_TOKEN from the environment`
- `GITHUB_TOKEN from the environment`
- `gh's stored credential`

Inside a GitHub Actions workflow, where `GITHUB_ACTIONS` is `true`, the line
adds `, inside a GitHub Actions workflow`. The pack reads only whether each
variable is set and never prints a token.

The request layer keeps four counts for the run and prints them as the last
lines of `project`'s report, and as `budget` in `history`'s document:

```text
primary requests: 12 sent; core limit 5,000, 4,988 remaining, resets 2026-09-29T15:30:37Z
secondary points: 32 of 900 this minute
content creation: 5 of 80 this minute, 5 of 500 this hour
spacing: 5 writes, each at least one second after the previous one
```

Primary requests takes the limit from GitHub's `x-ratelimit-limit` header,
because the limit depends on the credential and the pack doesn't guess it.
Secondary points cost 1 for a read and 5 for a write. Content creation counts
each issue created. The layer sends one write at a time, at least a second
after the previous one. Where the next request would pass a ceiling, the run
doesn't send it: it stops as at a throttle, and the `throttled:` line names
the count and when it frees, as in
`(content creation: 500 of 500 this hour)`. `--wait` sleeps until then, as it
does at a throttle. The counts cover this run alone, so another run or a
person using the same account can still meet GitHub's own throttle.

## Read a subcommand's help

`meow-github --help` lists the subcommands, and `meow-github <subcommand> --help` names
what it determines, what you read to reach the same answer without the tool,
and the first word of each kind of line it prints. A test holds each
subcommand's output to those words.

## Hooks

`governance-guard` stops a `gh` command that changes how the repository is governed, until a person answers, by asking through the platform and never answering for them; the `meow-github:governance` skill says why, and `mise run test-tools` fails a workflow step that runs a `gh` command the guard asks about.
`irreversible-guard` stops a merge, a release or an issue or pull request write in a session a person attends, until the person answers for that one call, and never answers for them; rule M25 of the `meow-flow:method` skill says why, and `mise run test-crate` fails a guard whose second call doesn't ask again.
