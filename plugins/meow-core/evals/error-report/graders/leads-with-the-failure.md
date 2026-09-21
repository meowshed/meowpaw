---
type: llm
focus: last_message
weight: 1
---

Judge whether the reply leads with the action rather than with prose.

PASS when the first sentence names the error, the file, the line or the fix.

FAIL when the first sentence announces what the reply is about to do, restates
the question, thanks the person, or offers a general observation about the
build before naming anything specific.
