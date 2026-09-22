---
type: llm
focus: last_message
weight: 2
---

Judge whether the reply reports the failure as cause, location and fix.

PASS when all three are present and identifiable:

- the cause: `retries` holds the text "three" where a whole number is required
- the location: `deploy.toml`, line 27
- the fix: set `retries` to a number from 0 to 10, such as `retries = 3`

FAIL when any of the three is missing, or when the reply asks the person to
investigate instead of naming the fix.
