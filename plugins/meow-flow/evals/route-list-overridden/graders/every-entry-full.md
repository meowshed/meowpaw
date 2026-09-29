---
type: llm
focus: last_message
weight: 2
---

Judge whether the override set every entry to full and kept the list.

PASS when the reply lists the three changes, gives each the size `full`, and stops without starting any of them.

FAIL when the reply merges the changes into one, gives an entry another size, or starts work on a change.
