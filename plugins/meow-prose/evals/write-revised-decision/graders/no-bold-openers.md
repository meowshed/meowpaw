---
type: regex
pattern: "^\\s*(?:[-*]\\s+)?\\*\\*[^*\\n]+\\*\\*"
flags: im
match: not_contains
target: last_message
weight: 1
---

A paragraph or list item opening in bold states a conclusion with its argument stripped out (the pattern "bold standing in for structure").
