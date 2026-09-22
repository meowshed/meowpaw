---
id: RES-0271
artifact: research
status: draft
revised: 2026-09-22
elaborates: RES-0012, RES-0262
---

# Where the record lives

## Summary

A repository can keep its record, the tree of research, requirements,
decisions, specifications, epics, tasks and defects, in one of three places:
its own tree, another repository, or a folder named by a path relative to its
root, which may lie outside it. RES-0262 kept the record in the repository so
that a second person on another machine can trust it, and that reason holds
for the first two places. It fails only where the named folder is under no
version control, so the constraint worth keeping is that the harness reports
such a record as local to this machine, not that it refuses the placement.

Research for where a repository's record is kept. It does not cover where the
harness keeps its own run state, which is
[RES-0262-state-outside-the-repository.md](RES-0262-state-outside-the-repository.md),
nor how each artifact kind is laid out inside the record, which is
[RES-0012-catalogues.md](RES-0012-catalogues.md).

## The question

The owner asked on 2026-09-22, in issue #64, that the record be able to live in
the code repository, in another repository, or in any folder given relative to
the code repository's root. Two approved statements stand against it: REQ-1428,
which forbids modifying files outside the repository except the harness's own
run state, and RES-0262, whose second conclusion keeps the record in the
repository. The question is whether their reasons forbid the three placements
or only one kind of folder.

## Method

I read RES-0262 and RES-0012 again for the reasons behind their conclusions,
and REQ-0520 and REQ-1428 for what they oblige. No external source was
consulted and nothing was run. The placements come from the owner's request,
and the findings are reasoning over the corpus, which is the limit of this
record.

## Findings

### The reason for keeping the record in the repository is that others can fetch it

RES-0262 keeps the record, the gate records and the evidence in the repository
"because a second person on another machine needs them to trust the work", and
keeps evidence off the machine because "evidence that lives on one machine is
an assertion". Both reasons are about who can read the record, and neither is
about which directory holds it.

A record in another repository meets both. A second person clones it the way
they clone the code, and its history is reviewable in the same way.

### A folder relative to the root is shared when it is under version control

A path such as `../specs` names the same place on every machine that follows
the checkout convention the repository states, so a team whose record sits in a
sibling checkout gets one layout everywhere. Where that folder is itself a
repository, it is the second placement under another name.

Where the folder is under no version control, the record exists on one
machine. That is the case RES-0262 warns against, and it is detectable: the
harness can ask whether the declared folder sits inside a working tree.

### Writing to the declared place is not writing outside the project

REQ-1428 protects files the harness has no business touching, and makes one
exception for the harness's own run state. The record's declared location is
the project's own material, named by the repository, so writing there is the
same kind of act as writing inside the tree. The rule's reason survives if the
exception is the location the repository declares, and nothing else.

### Declaring the location is already required

REQ-0520 has the repository declare the location of each artifact kind, so
adoption costs no file moves. The three placements extend what the declaration
may name, and add no new place for it.

## Conclusions

1. A repository declares where its record lives: in its own tree, in another
   repository, or in a folder named by a path relative to its root, which may
   lie outside it.
2. The harness reads and writes the record at the declared location and
   nowhere else outside the repository, apart from its own run state.
3. Where the declared location is under no version control, the harness
   reports the record as local to this machine, because a record only one
   machine holds is an assertion to everyone else.
4. A repository that declares nothing keeps its record in its own tree, which
   is where this repository keeps its record.

## Sources

- [RES-0262-state-outside-the-repository.md](RES-0262-state-outside-the-repository.md) -
  the second and third conclusions, keeping the record and the evidence in the
  repository so a second person on another machine can trust them.
- [RES-0012-catalogues.md](RES-0012-catalogues.md) - the artifact kinds and the
  declaration of their paths.
- Issue #64, 2026-09-22 - the owner's request for the three placements, and the
  statement that this repository keeps its record in its own tree.
