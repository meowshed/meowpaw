---
type: regex
target: trace
pattern: '^\{"type":"assistant"(?=.*(router|gave|overrid|was)[^\\]{0,40}\bnone\b).*"type":"text".*"parent_tool_use_id":null'
flags: mi
match: contains
weight: 1
---
