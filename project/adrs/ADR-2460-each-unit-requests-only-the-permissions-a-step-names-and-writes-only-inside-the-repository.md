---
id: ADR-2460
artifact: adr
status: approved
revised: 2026-10-03
addresses: [REQ-1424, REQ-1426, REQ-1429, REQ-1430, REQ-1432]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2460. Each unit requests only the permissions a step names, and writes only inside the repository

## Decision

Each tool an agent definition or a skill allows traces to a step that uses
it, and the unit's README names the step beside the tool (REQ-1430,
REQ-1432). `meow-author check` already reads every agent's `tools:` list
under ADR-1700, and it now fails a tool with no step named for it.

The harness writes outside the repository only to its own run state and to
the record at the location the profile declares (REQ-1429). Every automatic
check it installs, a hook or a gate task, fails with a diagnostic when its
tool is missing and never skips (REQ-1426). Where a hook's tool is missing,
it denies with a reason naming the tool, which ADR-2450 makes the only other
answer a hook gives.

The harness never reads, prints or sends a repository's secret material, and
never puts it in an artifact (REQ-1424). CLAUDE.md's `never_touch_secrets`
states the rule for this repository, and the kernel's instructions state it
for every repository, because a constitution is one of several documents
loaded and a repository's own may not carry it.

Once this is accepted, a unit's permissions can be read against its steps.
What still doesn't work: no program can prove the harness never reads a
secret, so REQ-1424 rests on the instruction and on review.

## Why

RES-0004 found that the platform grants a plugin's agents the tools they
declare and nothing narrower, so the declaration is the only place a unit can
be narrow. RES-0271 found that a record kept outside the repository is the
one write outside it that a person expects. RES-0023 found a check that skips
when its tool is missing reports green with nothing behind it.

## Alternatives

| Option                     | Better at                        | Why it lost                                                |
| -------------------------- | -------------------------------- | ---------------------------------------------------------- |
| Do nothing                 | No new check                     | A tool can be added to an agent with no step that needs it |
| A permission manifest      | One place lists every permission | It repeats what the agent definitions already declare      |
| Trust the platform sandbox | No rule of our own               | The sandbox doesn't know which step needs which tool       |

## What it costs

Each unit's README grows a line per tool, and adding a tool to an agent means
naming its step in the same pull request.

## What would reverse it

- The platform lets a plugin declare permissions per step, which would make
  the README line redundant.

## Consequences

`meow-author check` fails an agent tool with no step named for it. The
kernel's instructions carry the secrets rule.

## How I will know it was realised

1. `meow-author check` fails a fixture agent whose README names no step for
   one of its tools (REQ-1432).
2. A gate task whose tool is missing exits non-zero with the tool's name
   (REQ-1426).
3. The kernel's instructions state the secrets rule (REQ-1424).

## What this does not settle

- REQ-1420 and REQ-1422, the confirmation before an irreversible action,
  which the unattended chain decides.
