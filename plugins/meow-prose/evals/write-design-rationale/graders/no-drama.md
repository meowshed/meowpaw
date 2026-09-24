---
type: regex
pattern: "\\b(fatal|uncomfortable|striking|alarming|catastroph\\w*|read that again)\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

Emotion where the reason belongs (the pattern "drama in place of an argument").
