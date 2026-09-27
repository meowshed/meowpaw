---
id: TSK-2060
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-3144, REQ-3146]
issue:
---

# An agent finds the documentation through `llms.txt`

`llms.txt` at the repository root routes an agent to every page in the
published format, and `tools/check_docs.py` holds its links. One task, one
branch, one pull request, one review.

## Acceptance criteria

1. Given the tree, when `python3 tools/check_docs.py` runs, then it exits 0.
   Given a copy where `llms.txt` links to a missing file, lacks its H1, or
   carries a paragraph of prose outside the summary, then it exits 1 and names
   the line. Closed by: fixtures naming REQ-3144 and REQ-3146, seen failing
   first.
2. Given `llms.txt`, when a reader opens it, then it holds an H1, a blockquote
   summary, sections of links to the introduction, the tutorial, the
   troubleshooting page and each unit's page, and an `Optional` section
   linking the constitution, the specifications and the record. Closed by:
   the file.

## What to do

Write `llms.txt` as SPC-1110 states it, and extend `tools/check_docs.py` with
its checks.

## Depends on

TSK-2030, because the file links the pages at the paths it gives them.

## Evidence

Not yet.

## Left alone

Serving `llms.txt` from `meow.retran.me`, which the release doesn't publish.
