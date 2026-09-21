---
id: BUG-1060
artifact: bug
status: approved
severity: minor
violates: REQ-0704
found: 2026-09-21
revised: 2026-09-21
issue: 38
---

# A field the constitution required was dropped from the record and left in the templates

## Reproduction

At `bcedd25`:

```bash
grep -l '^unit:' project/requirements/*.md | wc -l    # 222 of 1056
grep -l '^unit:' project/research/*.md | wc -l        # 0 of 126
grep -l 'unit:' templates/*.md | wc -l                # 4
grep -rn 'as `unit`' CLAUDE.md project/README.md      # both require it
grep -n 'unit' tools/check_front_matter.py            # no match
```

## What the system does

The `unit` field was removed from the research corpus, and the removal stopped
there. It survived on 222 requirements, in four templates, in two sentences
calling it mandatory, and in sixteen records written this session, which copied
it from the files beside them.

Nothing anywhere resolves `U-0001`: the record holds no registry, declares no
artifact kind for a unit, and says nowhere which unit of work it names. No check reads the field:
`check_front_matter` requires `id`, `artifact`, `status` and `revised`.

## What it should do, and why

Checking the record reports artifacts whose recorded state contradicts the tree
(REQ-0704). A living document demanding a field that four fifths of the record
omits, that nothing defines and that nothing checks, is that contradiction,
stated as a rule instead of as a state.

The templates are why the field survived its own removal. An author writing a
record copies the template and the files beside it, so sixteen new records
acquired the field this session, after the decision to drop it and without
anybody choosing to keep it.

## Triage

Implementation. The removal was decided and half done, and finishing it changes
no requirement.

## Closed by

`unit` gone from every record and every template, and the two sentences in
`CLAUDE.md` and `project/README.md` replaced by what they were protecting: a
record is found by what it says and by the identifiers it cites, never by when
somebody wrote it.

`CLAUDE.md` keeps "one commit per unit of work", which is prose about squashing
and not this field.
