---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*size\W{0,8}none\b)(?=.*reason\W).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 2
---
