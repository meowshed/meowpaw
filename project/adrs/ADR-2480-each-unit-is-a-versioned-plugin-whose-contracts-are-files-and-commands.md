---
id: ADR-2480
artifact: adr
status: approved
revised: 2026-10-03
addresses:
  [
    REQ-1480,
    REQ-1481,
    REQ-1482,
    REQ-1483,
    REQ-1484,
    REQ-1488,
    REQ-1494,
    REQ-1738,
    REQ-2990,
    REQ-2994,
    REQ-2996,
    REQ-2998,
    REQ-3000,
    REQ-3002,
    REQ-3006,
  ]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2480. Each unit is a versioned plugin whose contracts are files and commands

## Decision

Each unit installs through the platform's plugin mechanism from
`.claude-plugin/marketplace.json`, with no installer of its own (REQ-1480).
Each carries a version in its plugin manifest (REQ-2990) and stays at major
version zero until its public interface stops moving (REQ-2994). A released
version is never changed: the release workflow refuses to publish a version
that already has a release, and a change ships as a new version (REQ-2996).

Units talk to each other only through files and commands (REQ-1481), and no
unit's behaviour depends on the order in which hooks from several units run
(REQ-1483). Each unit's `requires.toml` names the units it needs and the
platform version it was tested on (REQ-1482). A pack names the range of the
kernel's version it works with (REQ-2998). A unit started on an older
platform than its `requires.toml` names fails with a diagnostic naming both
versions (REQ-1738).

An upgrade keeps a repository's own configuration and record, because both
live in the repository and not under a unit's install root (REQ-1484,
REQ-3000). Machine-specific or secret configuration lives in the user's own
settings and never in the repository or a unit's files (REQ-1488). Every file
of configuration the harness owns is TOML (REQ-1494). Where a unit requires
another, the platform enables the required one and won't disable it while the
first is on, and the unit's README says so (REQ-3006). Each release's notes
are written for the person whose repository changes, and never generated
from commits (REQ-3002).

Most of this already holds: `.claude-plugin/marketplace.json` lists every
unit, `plugins/meow-flow/requires.toml` names its platform version, and the
profile and budgets are TOML. What this decision adds is the check that holds
each rule.

Once this is accepted, a test can hold each unit to its manifest. What still
doesn't work: no unit except the ones with a `requires.toml` states its
platform version, until each gains one.

## Why

RES-0004 found that the platform gives plugins no shared runtime and no
defined hook order, so a contract between units can only be a file or a
command. RES-0264 found that a version a project republishes breaks every
lockfile that pinned it, and that semantic versioning's major version zero is
the honest state for an interface still changing. CLAUDE.md already makes
TOML the harness's configuration format.

## Alternatives

| Option                   | Better at                      | Why it lost                                                       |
| ------------------------ | ------------------------------ | ----------------------------------------------------------------- |
| Do nothing               | No new checks                  | Fifteen requirements rest on a release script and on memory       |
| A shared runtime library | Units call each other directly | The platform installs plugins separately and offers no such thing |
| Version 1.0 now          | A promise of stability         | The interface changed in every recent release                     |

## What it costs

Each unit gains a `requires.toml` and a kernel range, and each release needs
written notes, which take the releaser's time.

## What would reverse it

- The platform adds a manifest field for a minimum platform version or for
  dependencies, which would replace `requires.toml`.

## Consequences

`meow-author check` fails a unit with no version, no `requires.toml` or no
kernel range in a pack. The release workflow refuses a version that has a
release. Each unit states its platform version.

## How I will know it was realised

1. `meow-author check` fails a fixture unit with no `requires.toml`
   (REQ-1482).
2. The release workflow exits non-zero for a version whose tag exists
   (REQ-2996).
3. A unit run under a lower platform version than it names prints both
   versions and stops (REQ-1738).
4. No file under a unit's install root is written at run time (REQ-3000).

## What this does not settle

- What the public interface is, which ADR-2490 declares.
- Provisioning without a person, which ADR-2500 decides.
