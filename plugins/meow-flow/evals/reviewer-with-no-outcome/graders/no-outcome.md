---
type: regex
pattern: "^[ \\t]*outcome: (DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED)[ \\t]*$"
flags: m
match: not_contains
target: last_message
weight: 1
---
