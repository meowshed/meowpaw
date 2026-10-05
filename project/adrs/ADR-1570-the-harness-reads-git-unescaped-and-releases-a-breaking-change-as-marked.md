---
id: ADR-1570
artifact: adr
status: done
revised: 2026-09-27
addresses: [REQ-2522, REQ-2524, REQ-2540, REQ-3192]
postpones: [REQ-2532, REQ-2544]
supersedes: []
---

# 1570. The harness reads git unescaped and without locks, keeps to the repository's configuration, and releases a breaking change as it is marked

## Decision

Every place the native tool asks git for a list of paths asks for the
NUL-separated form, `-z`, and splits on NUL, so a path holding a quote, a
newline or a non-ASCII character reaches the harness as the path it is
(REQ-2522). Today `meow-licence` does this and three places don't: the record
check's list of documents and two of the evidence listing's calls. Fixtures
hold those three; a listing added later is held by review, because no program
here can tell which git output carries paths.

Every git command the harness runs to read goes through one helper that sets
`GIT_OPTIONAL_LOCKS=0`, so a read never takes the index lock or refreshes the
index behind the person's back (REQ-2524). The helper already does this; this
decision records it, has a unit test hold it, and has another fail where the
native tool's sources start git anywhere but that helper.

REQ-2532 is postponed. It asks the harness to record the signer, the key and
the fingerprint beside a signature verdict so the verification can be checked
again later, and the push guard's verdict is printed to one session and kept
nowhere. It is taken up when the harness keeps its own verdicts where
evidence is kept, since a report nobody keeps can't be checked again.

The harness writes git configuration only inside the repository, its own
`.git/config` and committed control files, and never with `--global`,
`--system` or into a user's or machine's configuration (REQ-2540). A unit test
fails where the native tool's sources, a shipped skill, agent, hook or output
style under `plugins/`, or a workflow under `.github/` names `git config` with
`--global` or `--system`. It catches those two flags and nothing else: a write
through `--file ~/.gitconfig`, `GIT_CONFIG_GLOBAL` or the file itself is held
by review.

The release workflow refuses to release a unit whose commits since its last
release include one marked breaking, with `!` in the subject or a
`BREAKING CHANGE:` footer, unless the unit's version raises its major number,
or its minor number while the major is zero (REQ-3192). A commit belongs to
each unit whose directory under `plugins/` it touches, and a commit touching
`crates/meow/` belongs to every unit that ships the native binary, because a
unit's release is what it ships and the binary ships inside each of those; so
one breaking commit across two units holds both, and a breaking commit
touching neither a unit nor the native tool holds none.
REQ-2814 named no exception at zero and REQ-2994 keeps the harness at major
version zero, so the two couldn't both be met; REQ-3192 replaces REQ-2814 with
semver's own provision for major version zero, which RES-0264 records. This
check never pushes a unit to 1.0.0, which stays a person's decision.

REQ-2544 is postponed. It asks the harness to say so where an operation it
performs is recorded in a log that makes it reversible, such as git's reflog,
and the harness performs no such operation today. A commit is recorded in the
reflog, but the harness doesn't make one: the person's own command commits,
and the commit guard only inspects it. The harness rewrites no history.

After this decision the harness reads every path git names correctly, never
locks the index to read, records enough to recheck a signature, touches no
configuration beyond the repository, and can't release a breaking change
without the version showing it. What still doesn't work: the release check
reads commit messages, so a breaking change left unmarked still releases as a
minor or a patch; a later git call that bypasses the reading helper is caught
by its test, but a later path listing without `-z` and a configuration write
the scan doesn't match are held by review alone; REQ-2524 asks the same of any
tool the harness reads, and this decision covers git only.

## Why

RES-0131 found that git escapes a path holding a special character in its
default output, so a harness parsing that output gets a path that doesn't
exist, and that the NUL-separated form is the one meant for programs. It found
that a read which takes the index lock contends with the person's own work,
and that `GIT_OPTIONAL_LOCKS=0` reads without it. It found that a signature
verdict with no signer and key can't be checked again, because the verdict
depends on the allowed signers at the time.

RES-0221 found that the conventional commit specification maps a breaking
change to a major version, which only helps a reader if the release honours it.
RES-0264 found that semver sets major version zero aside for a design still
changing, where anything may change, so at zero the minor carries what the
major would. REQ-2540 keeps the harness to the repository's own configuration,
because a user's or a machine's configuration reaches every repository on it.

## Alternatives

| Option                                         | Better at                           | Why it lost                                                                                                       |
| ---------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Do nothing                                     | No change                           | Three listings misread an unusual path, a signature can't be rechecked, and a breaking change can ship as a minor |
| Set `core.quotePath=false` in place of `-z`    | One setting, no parsing change      | Unescapes non-ASCII characters but still breaks a path holding a newline                                          |
| Force a 0.x unit to 1.0.0 on a breaking change | Reads REQ-2814 without an exception | Breaks REQ-2994, which keeps the harness at major version zero, and claims a stability nobody can keep            |
| Check breaking changes at review, not release  | No change to the workflow           | Review is a judgement, and a mapping a program can hold shouldn't rest on one                                     |

## What it costs

The release workflow reads every commit since each unit's last tag, and a
maintainer who marks a change breaking has to raise the unit's major version
before it can ship, or the minor at zero. The push guard's report grows by
one line per signed commit.

## What would reverse it

The `-z`, lock and configuration rules follow from git's documented interfaces,
and change only if git drops them. I would move the check from release to the
pull request if it refused a release for a commit marked breaking by mistake
more than once, because the mistake is cheaper to fix before the merge. I would
take up REQ-2544 once the harness runs an operation git records in its reflog,
such as a rebase or a reset, and REQ-2532 once the harness keeps its own
verdicts beside evidence.

## Consequences

- The record check's document listing and the evidence listing use `-z`.
- A unit test holds `GIT_OPTIONAL_LOCKS=0` in the reading helper, and another
  holds that no source writes global or system configuration.
- REQ-2814 is withdrawn, replaced by REQ-3192.
- The release workflow refuses a breaking change without a major version.
- SPC-1060 and SPC-1080 state these.

## How I will know it was realised

1. Fixtures show the record check and the evidence listing reading a path
   holding a newline, a quote and a non-ASCII character as it is.
2. Unit tests show the reading helper setting `GIT_OPTIONAL_LOCKS=0`, and
   fail on a source, a shipped prompt or a workflow naming `git config` with
   `--global`.
3. A unit test fails on a source that starts git outside the reading helper.
4. A test of the release check refuses a breaking commit with a patch bump,
   accepts it with a minor one at zero and a major one above zero, and holds
   each unit a commit touches, every binary-shipping unit for a commit
   touching `crates/meow/`.
5. Every requirement ADR-1570 addresses lands in exactly one closed task, and
   REQ-2532 and REQ-2544 read as postponed.

## What this does not settle

- A breaking change nobody marked.
- REQ-2544, until the harness rewrites history, and REQ-2532, until it keeps
  its own verdicts.
