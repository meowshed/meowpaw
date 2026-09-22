---
id: ADR-1040
artifact: adr
status: draft
revised: 2026-09-22
addresses: [REQ-0954]
supersedes: []
---

# 1040. The style carries the reply shape to a subordinate agent

## Decision

`meow-core` ships the reply shape once, in its output style. A prompt that
dispatches a subordinate agent includes the style's
`<rules name="the reply shape">` block as it stands, read from
`${CLAUDE_PLUGIN_ROOT}/output-styles/meow.md`, so the subordinate agent reads
the same rules as the main conversation, word for word (REQ-0954).

The separate fragment, `fragments/reply-shape.md`, is removed.

### What it changes in ADR-1000

ADR-1000 has `meow-core` ship "the same rules as a prompt fragment", a second
text beside the style. The rules still reach every subordinate agent, but from
the style's own block and not from a second file. Everything else ADR-1000
decided stands.

## Why

The owner decided it on 2026-09-22. Two texts stating the same rules in
different words drift apart, and nothing checked that they agreed: the fragment
already lacked the style's condition for confirming a destructive action first.
One text cannot disagree with itself.

The style's rules are written as list items inside one `<rules>` block since
ADR-1030, so a dispatching prompt can take that block whole without taking the
style's role, which addresses the main conversation.

## Alternatives

| Option                                   | Better at                                          | Why it lost                                                            |
| ---------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------- |
| The style's rules block, included whole  | One text, which cannot drift                       | Chosen                                                                 |
| A separate fragment, as ADR-1000 decided | A text written for a subordinate agent's position  | Two texts drift, and the fragment already had                          |
| A fragment generated from the style      | One source, with a text shaped for the subordinate | A build step in a unit that has none, to save a few words              |
| Do nothing                               | Costing nothing now                                | The drift stays, and a check comparing the two would be the only guard |

## What it costs

A subordinate agent reads R10, the rule about dispatching, which matters only
if it dispatches an agent of its own. The rule costs about 80 tokens per
dispatch and applies there too.

## What would reverse it

A measurement showing a subordinate agent answering worse with the style's
block than with a text written for its position, on the cases TSK-1190 builds
for dispatched agents.

## Consequences

- `plugins/meow-core/fragments/` is removed.
- The style's dispatch rule names its own rules block.
- `tools/check_subagent_shape.py` fails on a dispatching unit that does not
  name `output-styles/meow.md`.
- SPC-1000 lists the style's rules block as what a dispatching prompt carries.

This decision adds no task. TSK-1230 (#66) makes the change, because it
already rewrites the style and the fragment.

## How I will know it was realised

1. `fragments/reply-shape.md` does not exist, and the style's R10 names the
   style's own rules block.
2. `tools/check_subagent_shape.py` fails on a probe unit that dispatches
   without naming `output-styles/meow.md`, and passes on the tree.

## What this does not settle

Whether a subordinate agent answers better with a text written for its
position. TSK-1190 builds the cases that would show it.
