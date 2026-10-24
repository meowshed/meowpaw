---
id: ADR-3050
artifact: adr
status: approved
revised: 2026-10-24
addresses: [REQ-0930, REQ-0932]
postpones: []
supersedes: []
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# 3050. The reply shape reaches every Claude Code session through a session-start hook

## Decision

`meow-core` ships a second `SessionStart` hook, `hooks/reply-shape`. At the start of a session, and again on resume, clear and compaction, it prints the style file's `<role>` block and its `<rules name="the reply shape">` block as the hook's `additionalContext`, so the model holds the shape whether or not anyone selects the output style. The hook reads the blocks from `output-styles/meow.md` at run time, so the style file stays the one source of the text. A missing or unreadable style file, or one with no rules block, makes the hook print nothing and exit 0, because a hook that fails a session costs more than a reply in the platform's default shape.

This replaces the mechanism ADR-1000 chose and keeps the rest of it. ADR-1000 relied on `force-for-plugin` to hold the shape without each person opting in, and BUG-1040 found that Claude Code 2.1.278 does not honour it. The style file, its front matter and its rules block stay: selecting the style still works, and the rules block is still what a unit hands to a subordinate agent. Pi keeps its own delivery, which its core extension already makes.

Once this is accepted, a session in a repository that has `meow-core` enabled carries the shape from its first turn. What still doesn't work: a model can ignore text in its context and no program reads a reply, so REQ-0930 holds as far as an instruction can hold it. Where the style is also selected, the shape reaches the model twice.

## Why

RES-0203 recorded that a `SessionStart` hook's `additionalContext` reaches the model, which the platform documents, while the same research found a hook cannot read the conversation as it stands. A hook that sends text at the start is therefore the one mechanism that needs neither the conversation nor a platform field that does not work. Reading the blocks from the style file keeps one copy of the rules, so the hook and the style cannot drift.

## Alternatives

| Option                                                     | Better at                        | Why it lost                                                                                 |
| ---------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------- |
| Do nothing                                                 | Costs no work                    | Leaves REQ-0930 unmet in every session where nobody selects the style, which is the default |
| Wait for the platform to honour the field                  | No code of ours                  | The platform names no date, and the premise of ADR-1000 stays false meanwhile               |
| A `UserPromptSubmit` hook                                  | The rules arrive fresh each turn | It adds the same text to every turn, so a long session pays for it hundreds of times        |
| Write the rules into the repository's own instruction file | The platform loads it for sure   | The harness writes nothing into a repository it is installed in, which the vision rules out |

## What it costs

About 3.7 kilobytes of context at each session start and each compaction, and the same text twice where the style is also selected. The unit gains a second hook, a row in SPC-1240 and a sentence on its page.

## What would reverse it

- The platform honours `force-for-plugin` on the versions `meow-core` requires, and a session shows the style with nobody selecting it, which makes the hook redundant.

## Consequences

`meow-core` raises its patch version, BUG-1040 closes, and SPC-1000 states the new mechanism where it stated the failure.

## How I will know it was realised

1. The hook's output for this repository's style parses as one JSON object, and its `additionalContext` equals the style's role and rules blocks.
2. A style file with no rules block, or none at all, makes the hook print nothing and exit 0.
3. `plugins/meow-core/hooks/hooks.json` lists the hook under `SessionStart` beside `write-root`.

## What this does not settle

- Whether a model follows the shape, which only review of its replies shows.
- BUG-1360, the route not reported before a first tool call, which needs the conversation a hook cannot read.
