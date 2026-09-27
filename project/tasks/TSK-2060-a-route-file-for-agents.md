---
id: TSK-2060
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-3144, REQ-3146]
issue: 417
projected: 7f19fa1958a3
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

`llms.txt` at the repository root has an H1, a blockquote summary, sections
linking the introduction, the tutorial, the troubleshooting page and every
unit's page, and an `Optional` section linking the constitution, the vision,
the specifications and the record. It restates none of them: every line
after the summary is a heading or a link with a short note.

`tools/check_docs.py` fails a route file that is missing, lacks its H1 or
summary, links a path that doesn't exist, or carries a line of prose. Three
new fixtures, naming REQ-3144 and REQ-3146, failed against the check as
TSK-2050 left it and pass against this one:

```text
$ CHECK_DOCS=check_docs_before.py python3 -m unittest tools/test_check_docs.py
FAIL: test_a_route_file_without_its_heading_fails
FAIL: test_a_route_link_to_a_missing_file_fails
FAIL: test_prose_in_the_route_file_fails
FAILED (failures=3)
$ python3 -m unittest tools/test_check_docs.py
Ran 18 tests
OK
```

`REUSE.toml` declares `llms.txt` with the rest of the corpus.

## Left alone

Serving `llms.txt` from `meow.retran.me`, which the release doesn't publish.
