---
id: ADR-2750
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1420, REQ-1422]
supersedes: []
---

# 2750. An attended irreversible action asks each time

## Decision

In an attended session, every harness action that is hard to reverse or
visible outside the repository requires a fresh platform permission prompt
for that one invocation. A prior approval cannot authorise a later invocation,
so no shipped rule requests a reusable permission prefix for these actions
(REQ-1420, REQ-1422).

The rule applies to pushes, merges, releases, issue writes and changes to
repository governance. Read-only operations and writes confined to the
repository remain under their ordinary step permissions. An unattended run
keeps ADR-2380's separately declared authority and is outside this attended
rule.

Once accepted, the shipped method and permission hooks distinguish attended
irreversible actions and ask for each one. It does not add a second prompt
where the platform already supplies that exact per-call prompt.

## Why

RES-0031 records that external side effects cannot be recovered from the
working tree. The platform prompt is the boundary the person can inspect at
the moment of action, and a reusable approval would turn one decision into an
unstated policy.

## Alternatives

| Option                   | Better at          | Why it lost                    |
| ------------------------ | ------------------ | ------------------------------ |
| One approval per session | Fewer prompts      | Confirmation would carry over  |
| Ban irreversible actions | Safety             | Attended work could never land |
| Ask for every invocation | Explicit authority | Chosen despite the prompt cost |

## What it costs

An attended sequence with several external writes asks several questions.

## What would reverse it

- The platform exposes a transaction whose preview and one confirmation bind
  an exact immutable set of operations.

## Consequences

The method and permission hooks name the irreversible operations and request
no reusable approval for them.

## How I will know it was realised

1. A fixture push, merge, release, issue write or governance change asks for
   confirmation before the command runs.
2. Approving one fixture invocation does not approve the next.
3. Read-only and repository-local fixture operations gain no new prompt.

## What this does not settle

- Unattended authority, which ADR-2380 decides before the run starts.
