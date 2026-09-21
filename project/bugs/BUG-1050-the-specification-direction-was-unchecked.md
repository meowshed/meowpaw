---
id: BUG-1050
artifact: bug
status: approved
severity: minor
violates: REQ-0246
found: 2026-09-21
revised: 2026-09-21
issue: 34
---

# A requirement the decision addresses was stated in no specification

**Written during the change that closes it, and not before it.** The work
started as a plain issue because I classified it as too small for a record,
which was wrong: the defect revealed a missing check, and the reasoning is
worth having later.

## Reproduction

At `3e8cd03`:

```bash
comm -23 \
  <(sed -n '/^addresses:/,/\]/p' project/adrs/ADR-1000-*.md | grep -o "REQ-[0-9]*" | sort) \
  <(sed -n '/^states:/,/\]/p' project/specs/SPC-1000-*.md | grep -o "REQ-[0-9]*" | sort)
REQ-0956
```

## What the system does

`ADR-1000` addresses sixteen requirements. `SPC-1000` states fifteen. REQ-0956,
which obliges a change to the reply shape to be measured against the shape it
replaces, was addressed by the decision and written into no specification.

`tools/check_coverage.py` compared a decision against its tasks and never
against a specification, so nothing would have reported it. Epic verification
found it by reading the two front-matter lists side by side.

## What it should do, and why

REQ-0244 wants every requirement in force stated somewhere, and REQ-0246 wants
both directions checked. One direction was checked and the other was assumed,
which is how a requirement gets built and never written down, or written down
and never built.

## Triage

Implementation. The requirements were right, the specification was short one
statement, and the check was short one direction.

## Closed by

`SPC-1000` gains a **Changing the shape** section stating REQ-0956, and
`check_coverage` gains the second direction. The check was seen failing first:
removing REQ-0956 from the specification's front matter produced
`ADR-1000: REQ-0956 is stated in no specification` and exit 1.
