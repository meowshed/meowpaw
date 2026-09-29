---
type: regex
target: trace
pattern: '^(?:(?!(?:"type":"assistant"|"type":"tool_result")[^\n]*?size\W{0,8}(?:none|reduced|full)\b)[\s\S])*"type":"tool_use","id":"[^"]*","name":"(Write|Edit|NotebookEdit|Bash)"'
flags: i
match: not_contains
weight: 2
---
