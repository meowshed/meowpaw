---
id: EPC-1350
artifact: epic
status: approved
revised: 2026-09-27
realises: ADR-1370
checked-at:
---

# Each unit ships its own page, and a program holds the documentation to the tree

Realises exactly one authorising record, ADR-1370. The epic is complete when
each unit's page ships inside the unit, every user-facing page names its reader
and the version it describes, the catalogue entries carry the fields a reader
sees before an install, and `tools/check_docs.py` holds all of it in the
`test` verb.

## Acceptance criteria

Taken from ADR-1370, from its list of how I will know it was realised, before
the tasks below were written:

1. `tools/check_docs.py` passes on the tree and fails on each of six probes: a
   unit with no page, a page missing `reader`, a stale `describes` version, a
   page citing a record identifier, a `plugin.json` missing `license`, and an
   `llms.txt` link to a missing file.
2. Every unit's page is `plugins/<unit>/README.md`, and no `docs/<unit>.md`
   remains.
3. The release workflow, run over the committed catalogue, produces entries
   carrying `description`, `homepage`, `repository`, `license` and `keywords`
   for every unit.
4. `docs/README.md` lists every page with its reader and what it answers,
   names the planned and unbuilt parts, and records each absent kind with its
   reason.
5. Every requirement ADR-1370 addresses lands in exactly one closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A task
that can run in parallel with its neighbours carries `[P]` after its number,
as in `- [ ] T-002 [P] TSK-NNNN`.

## Tasks

- [x] T-001 TSK-2030 move each unit's page into the unit, give every page its
      front matter, and check both in `tools/check_docs.py`
      closes: REQ-2838, REQ-3130, REQ-3136, REQ-3138, REQ-3142, REQ-3148, REQ-3152
      evidence: nine fixtures and `tools/check_docs.py` in the `test` verb, in
      #414.

- [x] T-002 [P] TSK-2040 carry the catalogue fields in every `plugin.json`,
      and copy them into the served entries at release
      closes: REQ-3160, REQ-3162, REQ-3164
      evidence: three fixtures, and the release copying four fields, in #415.
      depends: TSK-2030 - the homepage points at the page T-001 moves

- [x] T-003 [P] TSK-2050 generate the index, name what is planned and what is
      not written, and add the tutorial and the troubleshooting page
      closes: REQ-3132, REQ-3134, REQ-3140, REQ-3150, REQ-3154
      evidence: three fixtures, the generated index, and the tutorial run in an
      empty directory, in #416.
      depends: TSK-2030 - the index is generated from the front matter T-001
      adds

- [ ] T-004 [P] TSK-2060 write `llms.txt` and check its links
      closes: REQ-3144, REQ-3146
      depends: TSK-2030 - the route file links the pages at the paths T-001
      gives them

## Coverage

ADR-1370 addresses 17 requirements, and each lands in exactly one task above.
The smallest set that tests the decision is T-001: once it lands, every unit's
page ships with the unit and a version bump without a restamp fails the gate.
T-002, T-003 and T-004 depend only on T-001, so they can run in parallel.

## Not covered

Nothing ADR-1370 addresses. The document step's obligations on a repository's
own documentation are a later decision, as ADR-1370 says.
