---
type: llm
focus: last_message
weight: 2
---

Judge the code example in the section.

PASS when a sentence ending in a colon introduces the command, the command is in a fenced block whose opening fence names its language, such as ```bash, and a sentence after the block says what the reader should see (the number of rows loaded).

FAIL when the command appears with no lead-in sentence, its fence names no language, or nothing after it says what to expect.
