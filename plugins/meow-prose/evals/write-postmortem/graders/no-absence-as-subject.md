---
type: regex
pattern: "(^|[.!?]\\s+)(Nothing|Nobody|No one) \\w+"
flags: im
match: not_contains
target: last_message
weight: 1
---

A world where nobody acts hides who didn't and why (the pattern "absence as the subject").
