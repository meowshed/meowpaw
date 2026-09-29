---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*\breduced\b)(?=.*authori[sz]).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 1
---
