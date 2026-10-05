---
reader: someone choosing or running meow-github
answers: what meow-github does, what it adds to a session and how to run it
kind: reference
describes: [meow-github@0.14.0]
---

# meow-github

`meow-github` reads a GitHub repository's history: every issue and pull
request, whether each pull request merged, and every conversation and review
comment. It prints them as one JSON document and writes nothing to GitHub.
`/meow-flow:onboard` reads a repository's history through it, and it installs
on its own, with no other part of the `meowpaw` harness.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-github@meowpaw
```

It reads through GitHub's own client, so install `gh` and sign in with
`gh auth login` first. The pack never sees your credential.

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

## Project an authorising record's tasks onto issues

Declare the tracker in `.meowpaw/profile.toml` first. Without it the command
says so and does nothing, and nothing in the method needs a tracker:

```toml
[tracker]
kind = "github"
```

The command opens by naming the profile's state, as
`meow-github project: profile: parsed`, and each key no unit reads, as
`meow-github project: unknown key: <path>`, which changes no exit status.

Once an epic is approved, file one issue per task:

```bash
meow-github project EPC-1310
```

An approved defect that carries tasks directly uses the same projection and
derives completion from its own task marks:

```bash
meow-github project BUG-1210
```

Each issue is titled with the task's identifier and title, and its body cites
the authorising epic, defect or decision, the requirements the task closes and
its dependencies, and ends with a marker naming the task and a fingerprint. The task gains `issue:` with the
issue's number and `projected:` with the fingerprint, so the mapping lives in
the repository. After its last create, the run reads the issues it created
back in one listing of the issues written since the `updated_at` GitHub gave
the earliest of them, and matches each by number. Where no create's answer
states that time, the listing starts at the `Date` of the run's first
response. The listing can lag a create by seconds, so the run reads each
issue it left out on its own, by number, before it reports that issue as not
read back. Run it again and nothing changes. It refuses an authorising record
that isn't approved.

Where a run stops before it has projected every task, or neither the listing
nor a read by number shows a created issue as it was written, the report says which tasks are in which state and
the run exits 3:

```text
partial: projected TSK-1930; created, not read back TSK-1940 (issue #512, reads differently from what was written); not projected TSK-1950, TSK-1960
```

| Group                    | Holds each task whose issue                                               |
| ------------------------ | ------------------------------------------------------------------------- |
| `projected`              | Was updated, was found unchanged, or was created and read back as written |
| `created, not read back` | Was created and not confirmed, with the issue's number and the reason     |
| `not projected`          | Is any other task of the authorising record, visited or not               |

A group with no task reads `none`. The reason is `couldn't be read`,
`reads differently from what was written`, `the listing couldn't be read`,
`the listing was throttled`, `the listing's credential was rejected`,
`no listing ran`, `no read ran` or
`the task doesn't name it`.
The run sends the listing after a write GitHub refused, and sends none after a
throttle, a budget ceiling or a 401, where it sends nothing more at all. A task under
`created, not read back` keeps its `issue:`, so the next run reads that issue
through the mapping and creates no second one. The one exception is
`the task doesn't name it`: the issue exists and the task file couldn't be
written, so set `issue:` on the task by hand before the next run.

A decision one task realises has no epic. Name the decision, and the pack files
an issue for each task that names it in `realises:`, under nothing:

```bash
meow-github project ADR-2300
```

The record owns each issue's title and body, and GitHub owns whether it is
open or closed, which the pack never writes. A task you changed updates its
issue on the next run. An issue someone edited on GitHub is reported and left
as it is, and an issue closed on GitHub while its task remains open in the
record is reported. An epic or defect decides that state with its task marks;
a task directly realising a decision decides it with Evidence. Add
`--check` to see each task's state without writing anything:

```bash
meow-github project EPC-1310 --check
```

## Project a task by hand

You can file a task's issue without the pack and get the same issue and the
same mapping, so installing the pack later continues your record instead of
duplicating it. Write the body as the pack does: the task and its authorising
record, the requirements it closes, and its dependencies. Its first sentence
is `<task> of <epic>, which realises <decision>.` for an epic, `<task> of
<defect>.` for a defect, or `<task>, which realises <decision>.` for a direct
decision task. Then:

```bash
title="TSK-1930: Project an approved epic's tasks onto issues"
fingerprint=$(printf '%s\n%s' "$title" "$body" | shasum -a 256 | cut -c1-12)
gh api repos/OWNER/REPO/issues -X POST -f title="$title" -f body="$body

<!-- meow-github: projected from TSK-1930 at $fingerprint -->"
```

Set the task's `issue:` to the number GitHub returns and add
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

| Line                                     | GitHub answered                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| `unauthenticated: <method> <endpoint>`   | 401: the credential is missing, expired or revoked                                         |
| `refused: <method> <endpoint> needs ...` | 403 that isn't a throttle                                                                  |
| The same, ending `, or it is hidden ...` | 404 on an issue a task maps, which GitHub also gives for an issue the credential can't see |

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
refusal stopped: a task, the naming of the repository or the read-back.
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
meow-github project EPC-1310 --wait
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

## What it writes, and what it asks about

The pack writes to GitHub only through two endpoints: `POST repos/{o}/{r}/issues`,
which creates an issue, and `PATCH repos/{o}/{r}/issues/{n}`, which updates
one. It sends any other method than `GET` to no other endpoint, and refuses
such a call before `gh` starts:

```text
refused by meow-github: PUT repos/OWNER/REPO/branches/main/protection isn't a write this pack makes
```

The pack also ships a `PreToolUse` hook on the Bash tool. When a Bash command
runs `gh` to change how a repository is governed, the hook asks you before the
command runs, naming the method and the endpoint, and never the command,
because a command can carry a token. It asks about:

- `gh api` with a method other than `GET`, or with a field or an `--input`
  body, to an organisation's `rulesets`, or to the repository itself, `branches/{b}/protection`, `rulesets`,
  `actions/permissions`, `actions/workflows/{id}/enable` or `/disable`,
  `actions/secrets`, `actions/variables`, `environments`, `hooks`,
  `collaborators` or `contents/.github/workflows/`, or anything under them;
- `gh api graphql` whose query holds `mutation`, or comes from a file, from
  standard input or from the shell, as `$(...)` or a variable;
- `gh repo edit`, `gh repo rename`, `gh repo archive`, `gh repo unarchive`
  and `gh repo delete`;
- `gh workflow enable` and `gh workflow disable`;
- `gh secret` and `gh variable` with `set`, `delete` or `remove`.

It reads each part of a command between `&&`, `||`, `;`, `|`, `&` and a new
line, joining a line a backslash continues and keeping a redirect such as
`2>&1` whole, after any variable assignments, a leading `env` or `command`
with its flags, `nohup`, and a shell word such as `then`, `do` or `{`. It reads
`gh` by name or by a path ending in `/gh`. For anything else it says nothing,
and your own permission rules decide.

The hook is a guard and not a barrier. It doesn't see a `gh` run inside a
subshell, `bash -c`, `eval`, `xargs`, `sudo`, `timeout`, a script, a function
or an alias, or a session with hooks turned off. Where the machine has no `meow-github` binary,
it lets every command through, because a hook that fails blocks every Bash
call.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-github/requires.toml`, and GitHub's client, `gh`, signed in.
The hook runs a native program on every Bash command, which loads nothing into
context, so the unit still keeps 0 characters in context on every turn. It
relies on these platform behaviours, each documented by Claude Code:

- a plugin's `bin/` programs on the Bash tool's `PATH`: [documentation](https://code.claude.com/docs/en/plugins-reference.md)
- a `PreToolUse` command hook that answers `ask` through
  `hookSpecificOutput.permissionDecision`: [documentation](https://code.claude.com/docs/en/hooks.md)
