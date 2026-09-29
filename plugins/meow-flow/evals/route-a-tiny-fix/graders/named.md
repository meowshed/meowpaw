---
type: llm
focus: last_message
weight: 1
---

Judge whether the reason names something the router read in the repository.

PASS when the reason names at least one file path, such as `.meowpaw/profile.toml` or a file under `project/` or `plugins/`, or a record identifier such as `SPC-1040` or `ADR-1070`.

FAIL when the reason names no path and no identifier, or names only words from the request.
