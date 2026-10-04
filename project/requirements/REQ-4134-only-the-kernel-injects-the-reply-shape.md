---
id: REQ-4134
artifact: requirement
status: approved
cites: RES-0340, BUG-1402
---

# Only the kernel injects the reply shape into the system prompt

The `@meowshed/meow-core` extension alone pushes the reply shape into the
system prompt guidelines. No other package's extension injects it. A package
that makes a nested model call carries its own bundled copy of the reply
shape into that call's messages, because a nested call runs its own prompt
and never sees the session's.

Rationale: BUG-1402 found every shipped package injecting the shape, so
installing two layers charges the same ten rules to the context twice. The
layering already puts the reply shape in the kernel; the other layers
reaching for it duplicates a rule and teaches the model nothing.
