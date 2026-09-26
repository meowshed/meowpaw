---
id: SPC-1100
artifact: spec
status: live
revised: 2026-09-26
checked-at: "#219"
states:
  [
    REQ-0237,
    REQ-0638,
    REQ-0640,
    REQ-0642,
    REQ-0644,
    REQ-0646,
    REQ-0648,
    REQ-0650,
    REQ-0652,
    REQ-0654,
    REQ-0658,
  ]
---

# The record's relations

## Scope

This covers how artifacts name one another: the identifiers, the relation
fields, and resolving an identifier to its artifact and to what cites it. It
leaves checking that a relation resolves to SPC-1070's relations check.

ADR-1150 decides it, EPC-1150 realises it, and `meow-method` implements it.

## Boundary

| Surface                          | What it is                                          |
| -------------------------------- | --------------------------------------------------- |
| `relations` in `lib/layout.toml` | The fixed vocabulary of relation fields             |
| `meow-method show <id>`          | The artifact an identifier names, and what cites it |

## Behaviour

### Identifiers

Every artifact carries an identifier of its own, `<PREFIX>-NNNN` for a numbered
kind, allocated once and never reused, and the prefix names the kind, so a
citation says what it cites without resolving it (REQ-0638, REQ-0640).

### Relations

An artifact names what it came from in its front matter, as bare identifiers
in one of the fields `relations` lists: `elaborates`, `addresses`,
`supersedes`, `realises`, `epic`, `closes`, `states` and `violates` (REQ-0644,
REQ-0646). Only that upward direction is written, and a decision names the
requirements it addresses, never the reverse (REQ-0237, REQ-0648). Every
identifier in a relation resolves to an artifact that exists (REQ-0654).

### Resolving an identifier

`meow-method show <id>` resolves an identifier alone, with no path, and prints
(REQ-0642, REQ-0652):

```text
REQ-0190 requirement, approved: project/requirements/REQ-0190-nine-steps.md
The method MUST proceed through nine named steps ...

Names
  elaborates: RES-0001

Cited by
  addresses: ADR-1130
  states: SPC-1090
  closes: TSK-1440
  body: project/README.md
```

`Names` lists the artifact's own relation fields. `Cited by` is derived each
run from every other artifact's relation fields, grouped by field, with a
mention in a body listed under `body` (REQ-0650). A withdrawn or superseded
artifact resolves and prints its status, so an identifier resolves forever
(REQ-0658).

## Failure paths

| Condition                       | What happens                                   |
| ------------------------------- | ---------------------------------------------- |
| An identifier with no artifact  | `show` says it resolves to nothing and exits 1 |
| No identifier given             | Usage, exit 2                                  |
| The record's root doesn't exist | `show` says so and exits 1, as `check` does    |
