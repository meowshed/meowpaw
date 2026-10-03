---
id: ADR-2370
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [REQ-2940, REQ-2942, REQ-2944, REQ-2946, REQ-2948, REQ-2950, REQ-2952]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2370. The profile is read at the root, reports the keys it doesn't know, and keeps a personal file apart

## Decision

The native tool reads `.meowpaw/profile.toml` from the repository root and
from no directory above it (REQ-2940). It reports the profile in one of three
states, and every command that reads the profile says which:

- `absent`: no file. Each verb resolves by detection, as before.
- `unparseable`: the file exists and doesn't parse. The report carries the
  parser's message and the line it gives, every verb is unresolved, and no verb
  falls back to detection (REQ-2948).
- `parsed`: the file parses. The report names each key the tool doesn't know,
  one line a key, and the command goes on, with its exit status unchanged
  (REQ-2942).

A key is known when the tool's table of profile keys lists it. The table is one
list in the tool, and each entry carries the reason nothing else answers it:
the ecosystem doesn't declare it, the platform doesn't own it, it isn't prose
and detection can't produce it (REQ-2950). A pull request that adds a key adds
its entry.

A personal profile lives in `.meowpaw/profile.local.toml`, beside the shared
one, and holds `[verbs]` only. The tool reads it after the shared profile, and
a verb it sets replaces the shared one on that machine. Any other table in it
is an unknown key. When the tool creates the file, it adds the file's path to
`.git/info/exclude` in the same step, because that file belongs to the
clone and not to the repository, so no file the repository keeps changes
(REQ-2944). A verb in the personal profile whose command starts with an
absolute path outside the repository, or with `~`, stays unresolved and the
report names the cause: the path is specific to this machine, and the tool
should be found through the repository's toolchain declaration (REQ-2946).

A check over a vocabulary the profile declares, such as the commit types in
`[commits.types]`, validates against the profile's list. The tool's built-in
list applies only where the profile declares none (REQ-2952).

Once this is accepted, a mistyped key stops failing silently, a broken profile
stops reading as an empty one, and a developer can pick their own command for a
verb without a commit. What still doesn't work: a profile in a part of a
repository below its root (REQ-3040), a trust prompt for a profile from an
unfamiliar repository, and the requirement that the profile's format permits
comments and shares the front matter shape (REQ-2954, see the last section).

## Why

RES-0261 compared two precedents and found the same rule in both: ignore a key
you don't recognise, so an older tool keeps working against a newer file. It
also found that ignoring in silence costs an afternoon, because the person
who mistyped `tset` sees no effect and no message. Reporting the key keeps the
compatibility and removes the afternoon.

The reader already has two of the three states: `crates/meow/src/profile.rs`
returns `Absent`, `Unparseable` or `Parsed`, and the verb runner leaves verbs
unresolved on `Unparseable`. What is missing is the third state's key list, the
personal file and the machine-path check. The tool reads one directory, the
root, so REQ-2940 holds today and needs a test that keeps it so.

The personal file takes `[verbs]` only because RES-0261 splits the file where
the choice is: what `test` means is the repository's, and which of three
installed checkers a developer prefers is theirs. A wider personal file would
let one developer change the commit convention or the record's paths, and then
the gate passes on one machine and fails on the next.

`.git/info/exclude` is the place for the exclusion because REQ-1563 lets the
step that writes a profile write only files the harness owns, and `.gitignore`
is a file the repository keeps.

## Alternatives

| Option                                      | Better at                         | Why it lost                                                                                                       |
| ------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Do nothing                                  | No work                           | A typo in a key keeps having no effect and no message, and the three requirements for the personal file stay open |
| Reject an unknown key as an error           | The typo surfaces at once         | A profile written for a newer tool then breaks every older install, which RES-0261 names as the cost to avoid     |
| Ignore an unknown key without saying so     | Quiet output                      | The person who configured the key learns nothing, which is the failure RES-0261 describes                         |
| Use the platform's local settings for verbs | No second file of our own         | The platform owns its settings and the harness can't read or validate them as a profile                           |
| Let the personal file override every table  | One merge rule for the whole file | One developer could change the commit types or the record's root, and the gate would differ per machine           |
| Ignore a path in a personal verb            | Never refuses a command           | The report would then pass on one machine for a command that exists only there                                    |

## What it costs

Each key a unit adds needs an entry in the tool's table, so a key and its
reason travel in the same pull request. A unit that adds a key without an entry
shows up as an unknown key in its own report, which is the check working, but it
is one more edit.

A developer with a personal verb gets a second source for what `test` runs, and
the report must say which file a resolved verb came from, or "the gate passed"
means different things on two machines. Every report that names a resolved verb
names the file it came from.

## What would reverse it

- A released tool reports a key from one of its own units as unknown twice,
  which would show that a table kept in the tool can't follow the units, and
  each unit should declare its keys instead.
- A developer asks for a personal setting outside `[verbs]` and the request
  names a case where the machine, not the repository, decides.

## Consequences

The profile reader returns the parsed table together with its unknown keys.
`paw`, the verb runner and the diagnostic print the state line. The profile
template gains a note on the personal file. SPC-1080 states the personal file
and the table of keys, and REQ-2992 (the public interface) lists them once the
specification does. Each of the seven requirements gets a task, most of them
tests around behaviour the reader already has.

## How I will know it was realised

1. A fixture with a profile in the parent of the repository root and none in
   the root reports `absent` (REQ-2940).
2. A fixture whose profile has a syntax error reports `unparseable` with the
   parser's message, resolves all five verbs as unresolved and runs no
   detection (REQ-2948).
3. A fixture with the key `tset` under `[verbs]` reports `tset` once, runs the
   other verbs, and exits as it would without the key (REQ-2942).
4. Every key in the table has a reason in the source, and a test fails for an
   entry without one (REQ-2950).
5. Creating `.meowpaw/profile.local.toml` through the tool adds it to
   `.git/info/exclude` and changes no tracked file (REQ-2944).
6. A personal `test = "/Users/someone/bin/runner"` leaves `test` unresolved and
   the report names a machine path as the cause. The same value in a shared
   profile is not refused by this rule (REQ-2946).
7. A repository whose profile lists its own commit types rejects a commit whose
   type is outside that list, even when the built-in list has the type
   (REQ-2952).

## What this does not settle

- REQ-2954. It asks that the profile's format share the record's front matter
  shape, and the profile is TOML (`CLAUDE.md`, ADR-1070), so the two disagree.
  TOML already carries comments, which is the half of the requirement that
  matters. I leave it open for a later decision: withdraw REQ-2954 through its
  tombstone and state the comments rule as a new requirement.
- A profile in a part of a repository, and a per-part profile that declares
  what it needs (REQ-3040, REQ-3042).
- Trust for a profile from an unfamiliar repository, and the platform's
  permission settings for the gate's commands (RES-0261, conclusions 6 and 7).
- Which specification states the table of keys. This record says it lives in
  the tool and leaves the document to the spec step.
