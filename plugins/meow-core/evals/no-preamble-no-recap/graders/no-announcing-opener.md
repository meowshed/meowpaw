---
type: regex
pattern: "^\\s*(great question|good question|sure[,!.]|certainly|of course|happy to|let me |i'll (explain|walk|break)|absolutely)"
flags: i
match: not_contains
target: last_message
weight: 1
---
