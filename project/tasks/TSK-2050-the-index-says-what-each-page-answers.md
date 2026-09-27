---
id: TSK-2050
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1350
closes: [REQ-3132, REQ-3134, REQ-3140, REQ-3150, REQ-3154]
issue:
---

# The index says what each page answers, what is planned and what is not written

`docs/README.md` carries a table generated from every page's front matter,
names the planned parts of the harness, and records each kind no page carries
with its reason, and a tutorial and a troubleshooting page join it. One task,
one branch, one pull request, one review.

## Acceptance criteria

1. Given the tree, when `python3 tools/check_docs.py` runs, then it exits 0.
   Given a copy with a page added and the table not regenerated, or with a
   kind neither carried nor listed under `## Not written`, then it exits 1.
   Closed by: fixtures naming REQ-3154 and REQ-3140, seen failing first.
2. Given `docs/README.md`, when a reader opens it, then it lists every page
   with its reader and what it answers, has a `## Planned` section naming the
   unbuilt parts, and a `## Not written` section for each absent kind with its
   reason. Closed by: the page, and the check.
3. Given `docs/tutorial.md` and `docs/troubleshooting.md`, when the review
   step reads them, then they describe only what ships and repeat another page
   only where a link would cost the reader the page they are on. Closed by:
   the review's judgement, recorded in the pull request (REQ-3132, REQ-3150).

## What to do

Add `--write` to `tools/check_docs.py`, generating the table in
`docs/README.md` between markers, and the checks SPC-1110 lists for the index.
Write `## Planned` from the parts of the harness the record decides and no
unit ships yet, and `## Not written` for each kind with no page. Write
`docs/tutorial.md`, taking a reader from an empty repository to a first
verified change with `meow-verbs`, and `docs/troubleshooting.md`, one entry
per failure a unit reports, each with its cause and fix.

## Depends on

TSK-2030, because the table is generated from the front matter it adds.

## Evidence

Not yet.

## Left alone

How-to guides and explanation pages beyond what the index records as not
written.
