---
type: llm
focus: last_message
weight: 2
---

Judge the rewrite.

PASS when it names who acts and uses verbs, such as "Validate the importer's configuration before you deploy", with no chain of "of"s, no "There is a requirement for", and no "initiation" or "prior to".

FAIL when the rewrite keeps nouns where verbs belong ("the validation of", "the initiation of"), keeps two or more "of"s in a chain, or keeps the empty "There is" frame.
