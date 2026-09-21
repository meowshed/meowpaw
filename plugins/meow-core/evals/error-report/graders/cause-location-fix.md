---
type: llm
focus: last_message
weight: 2
---

Judge whether the reply reports the failure as cause, location and fix.

PASS when all three are present and identifiable:

- the cause: a `&str` was expected where a `String` was passed
- the location: `src/profile/resolve.rs`, line 184
- the fix: something concrete that would make it compile, such as borrowing the
  value or calling a method that yields a string slice

FAIL when any of the three is missing, or when the reply asks the person to
investigate instead of naming the fix.
