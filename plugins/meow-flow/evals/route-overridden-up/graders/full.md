---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*size\W{0,8}full\b).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 2
---
