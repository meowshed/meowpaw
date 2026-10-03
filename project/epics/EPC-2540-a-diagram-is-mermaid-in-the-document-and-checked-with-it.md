---
id: EPC-2540
artifact: epic
status: approved
revised: 2026-10-03
realises: ADR-2620
---

<!-- Written to the writing standard meow-prose ships: lead with the answer, give each rule its reason in the same sentence, and show the failing case. -->

# A diagram is Mermaid in the document, checked with it, and said again in prose

Realises exactly one authorising record, ADR-2620. The epic is complete when
`meow-markdown diagrams` fails a Mermaid block that doesn't parse and an image
embedded in a record document, `check` refuses a notation with a build step
for the record, and the skill carries the two rules no parser holds, as
SPC-1195 states under "Diagrams".

## Acceptance criteria

Taken from ADR-2620's list of how it will be known realised:

1. A fixture document with a Mermaid block that doesn't parse fails the `check` verb (REQ-2304).
2. A fixture record with an embedded `.png` fails (REQ-2290).
3. A profile declaring a notation with a build step is refused for the record (REQ-2294).
4. Every requirement ADR-2620 addresses is named by a closed task.

## Marks

```text
[ ] not started   [>] in progress   [x] done, with evidence
[~] dropped, with the reason        [+] added after approval, with why
```

A task is marked in the commit that advances it, never in a later pass. A
task that can run in parallel with its neighbours carries `[P]` after its
number.

## Tasks

- [ ] T-001 TSK-4985 parse each Mermaid block with `meow-markdown diagrams`, and bind `check` to it, in `plugins/meow-markdown/` and the `markdown` feature of `crates/meow/`
      closes: REQ-2292, REQ-2304

- [ ] T-002 TSK-4990 report an image embedded in a record document and refuse a build-step notation for the record, with `[docs] diagrams` in the table of keys
      closes: REQ-2290, REQ-2294, REQ-2296
      depends: TSK-4985 (not blocking) - the image finding prints from `diagrams`, and either task can add the command's skeleton

- [ ] T-003 [P] TSK-4995 carry the prose and content rules for a diagram in the skill and `reviewing.md`
      closes: REQ-2300, REQ-2302

## Coverage

Each of the seven requirements ADR-2620 addresses lands in exactly one task.
TSK-4985 is the smallest set that tests the decision, because a block that
fails to parse failing the `check` verb is the claim. TSK-4995 runs in
parallel with the other two.

## Not covered

Which diagrams the specifications carry, which ADR-2630's question section
asks, and a check that the prose says everything a diagram does, which no
parser can make, so review holds REQ-2300.
