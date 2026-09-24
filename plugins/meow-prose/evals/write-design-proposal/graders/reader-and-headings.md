---
type: llm
focus: last_message
weight: 2
---

Judge the proposal's structure.

PASS when the proposal states who it is written for or which decision it asks for near the top, its headings read as a story on their own (a heading such as "Serve cached pages for up to 60 seconds" rather than "Overview" or "Details"), and the decision, its cost and its limit (pages up to 60 seconds stale) all appear.

FAIL when no reader or decision is stated, the headings are generic labels such as "Overview", "Background" and "Conclusion", or the staleness limit is missing.
