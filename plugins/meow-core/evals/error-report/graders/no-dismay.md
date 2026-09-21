---
type: regex
pattern: "\\b(unfortunately|sadly|regrettably|uh oh|oh no|i'm sorry|apolog)"
flags: i
match: not_contains
target: last_message
weight: 1
---
