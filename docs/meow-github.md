# meow-github

`meow-github` reads a GitHub repository's history: every issue and pull
request, whether each pull request merged, and every conversation and review
comment. It prints them as one JSON document and writes nothing to GitHub.
`/meow-method:onboard` reads a repository's history through it, and it installs
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
  ]
}
```

`merged` is `false` for a pull request closed without merging, which records a
rejected approach, and `null` for an issue.

## Project an epic's tasks onto issues

Once an epic is approved, file one issue per task:

```bash
meow-github project EPC-1310
```

Each issue is titled with the task's identifier and title, and its body cites
the epic, the requirements the task closes and its dependencies, and ends with
a marker naming the task and a fingerprint. The task gains `issue:` with the
issue's number and `projected:` with the fingerprint, so the mapping lives in
the repository. Each issue is read back after it is created. Run it again and
nothing changes. It refuses an epic that isn't approved.

The record owns each issue's title and body, and GitHub owns whether it is
open or closed, which the pack never writes. A task you changed updates its
issue on the next run. An issue someone edited on GitHub is reported and left
as it is, and an issue closed on GitHub while the epic leaves its task
unmarked is reported, because the epic decides what the tasks are. Add
`--check` to see each task's state without writing anything:

```bash
meow-github project EPC-1310 --check
```

## When it can't read

Where `gh` is missing, isn't signed in, or GitHub refuses a listing, it prints
`unread`, names the listing that failed and what GitHub said, lists what it
read before it stopped, and exits 3. It prints no document then, because a part
of the history would read as the whole of it. Where its binary is missing for
your machine, it names the machine and says to reinstall the unit.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-github/requires.toml`, and GitHub's client, `gh`, signed in.
It relies on this platform behaviour, documented by Claude Code:

- a plugin's `bin/` programs on the Bash tool's `PATH`: [documentation](https://code.claude.com/docs/en/plugins-reference.md)

## Where the rules come from

ADR-1290 decides the pack, and SPC-1080 states it. RES-0277 records what a
repository's history holds and what reading it costs.
