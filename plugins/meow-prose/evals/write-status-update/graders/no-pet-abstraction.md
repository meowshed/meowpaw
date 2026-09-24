---
type: regex
pattern: "\\b(shape of|surface area|the seam|blast radius|the story here)\\b"
flags: im
match: not_contains
target: last_message
weight: 1
---

Category words standing in for the thing (the pattern "pet abstraction").
