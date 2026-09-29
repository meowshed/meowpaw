---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*ambiguous\W{0,8}yes\b[^\\]{20,}).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 2
---
