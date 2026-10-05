---
id: ADR-2350
artifact: adr
status: done
revised: 2026-10-03
addresses: [REQ-3004]
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 2350. `paw ready` stops naming the step that took a retired step's work

## Decision

`paw ready` refuses `cover`, `document` and `verify` as it refuses any step it
doesn't know: it exits 2 and names the seven steps in order, and it says
nothing of what took their work. The exit status of the three names stays 2.
Nothing else about the retirement changes: an approved defect that already
names a retired step in `enters` keeps it, a draft that names one is refused,
and the templates and skills name none (REQ-3004).

Once this is accepted, `paw ready` has one rule for a name it doesn't know.
What still holds is the retirement itself, which ADR-2300 decided.

## Why

ADR-2300 retired the three steps, and `meow-flow` 0.45.0 shipped the refusal
that names where each one's work went, so a prompt written for an earlier
release was told where to go. REQ-3004 says a deprecation is announced in one
release and removed in a later one, and `meow-flow` 0.46.3 is a later release
than 0.45.0, so the pointer may go. The pointer has no reader beyond a stale
prompt: the three names appear only in the refusal, in one test of it, in the
unit's README and in the grandfathering of approved defects.

## Alternatives

| Option                               | Better at                                  | Why it lost                                                                                              |
| ------------------------------------ | ------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Keep the pointer                     | Telling a stale prompt where its step went | The window REQ-3004 gives has run, and the pointer holds code and a test for names nobody types          |
| Refuse the names in `enters` as well | One rule for every use of a retired name   | An approved defect is a frozen record that can't change, so refusing its `enters` would flag it for good |
| Do nothing                           | No work, no risk                           | The deprecation then never ends, which REQ-3004 says it must                                             |

## What it costs

A prompt written for `meow-flow` 0.44 or earlier that runs `paw ready cover`
gets the list of seven steps and works out where the step went. Its exit status
is the same, so a script that tests only the status sees no difference.

## What would reverse it

- A report that someone's prompt still runs a retired step and the unknown
  step line leaves them no way to learn what replaced it.

## Consequences

The constant that lists the three names stays, for `enters` alone, and its
comment says so. The unit's README and SPC-1090 drop the pointer. One test is
replaced by a test that the three names are unknown steps. `meow-flow` takes a
patch release.

## How I will know it was realised

1. `paw ready cover TSK-0001`, `paw ready document TSK-0001` and
   `paw ready verify TSK-0001` each exit 2 and print the unknown step line
   with the seven steps, and none prints a replacement.
2. `paw check` still accepts an approved defect whose `enters` names `cover`.

## What this does not settle

- The `meow-verbs` stub, which REQ-3004 also lets a later release remove.
- Whether an approved defect's retired `enters` is ever rewritten.
