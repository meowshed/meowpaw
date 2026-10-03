---
reader: someone choosing or running meow-scm
answers: what meow-scm does, what it adds to a session and how to run it
kind: reference
describes: [meow-scm@0.5.0]
---

# meow-scm

`meow-scm` checks a commit message against the convention your repository
declares, and against a ban on crediting a tool, before the message is used.
It installs on its own, with no other part of the `meowpaw` harness, and it
names no version control tool, so it works whichever one you use.

## Install it

Add the marketplace and install the unit:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-scm@meowpaw
```

## Declare your convention

Put it under `[commits]` in `.meowpaw/profile.toml` at the repository's root:

```toml
[commits]
subject_limit = 72
trailers = ["Signed-off-by"]
may_name = ["Ada Lovelace <ada@example.org>"]

[commits.types]
feat = "minor"
fix = "patch"
docs = "none"
```

Each type says what it means for a release: `major`, `minor`, `patch` or
`none`. The subject limit is 72 where you don't declare one, and every trailer
you name must appear on every message. `may_name` lists each person, as
`Name <address>`, who agreed to be named in a trailer, and
`meow-scm convention` prints the list.

## What Claude Code does with it

Before Claude Code writes a commit message, a squash message or a pull
request title, the `meow-scm:commit` skill has it read your convention, write
the message, and check the exact text it will use:

```text
line 1: subject length: 78 characters, over the limit of 72
line 6: trailer: the `Signed-off-by` trailer is missing
meow-scm check-message: 2 problems; don't use this message until they are fixed
```

The check names every break with its line: a subject not in the form
`type(scope)!: description`, a type you didn't declare, a subject over the
limit or ending in a full stop, a missing blank line after the subject, a
missing trailer, a trailer naming a person `may_name` doesn't list, a break
with no `BREAKING CHANGE:` trailer, and any line that credits a tool, an agent
or a vendor. A break is a subject carrying `!` or a type you declared as
`major`. It exits 0 when the message meets your convention and 1 when it
doesn't.

The ban on crediting a tool holds whatever your profile says. Where you
declare no convention, the check applies the ban alone and exits 3, so a
message is never reported as meeting a convention nobody stated. The skill
also keeps a subject to one change in the imperative, and a body to why the
change was made, which a check can't decide.

## What it costs you

The skill's description costs 263 characters in context on every turn. The
program is a native binary shipped inside the unit, so it needs nothing
installed on the machine. On a machine the unit carries no binary for, the
check reports the message as unchecked and exits 3.

## The sign-off records the route

Where a message carries `Signed-off-by` trailers, the check compares the first
with the commit's author as git reports it, and refuses one naming anybody
else, because the chain starts with the author's own statement. Each later
sign-off names someone the change passed through, so it is a trailer naming a
person, and passes only where it names the author or someone `may_name`
lists. Where git reports no author, the check says the sign-off wasn't
compared.

A trailer names a person when its value has the form `Name <address>`, such as
`Co-authored-by`, `Reviewed-by` or `Acked-by`. The check reads trailers from
the message's last paragraph, as git does, and a key in any case. Three trailers record where
something came from and are exempt: `Signed-off-by` naming the author,
`Cherry-picked-from` and `Fixes`.

## What it needs

Claude Code 2.1.283 or later, the version this unit was tested on, declared
in `plugins/meow-scm/requires.toml`. It relies on these platform behaviours,
each documented by Claude Code:

- a skill loaded by its description: [documentation](https://code.claude.com/docs/en/skills.md)
- a plugin's `bin/` programs, run by path: [documentation](https://code.claude.com/docs/en/plugins-reference.md)
