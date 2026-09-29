---
type: regex
pattern: "^[ \\t]*outcome: (DONE|DONE_WITH_CONCERNS|NEEDS_CONTEXT|BLOCKED)[ \\t]*(\\r?\\n|$)"
match: contains
target: last_message
weight: 1
---
