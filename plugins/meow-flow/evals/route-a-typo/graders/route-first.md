---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*size: *(none|reduced|full))(?=.*shape:).*"type":"text"'
flags: mi
match: contains
weight: 2
---
