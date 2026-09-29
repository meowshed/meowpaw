---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*no router).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 1
---
