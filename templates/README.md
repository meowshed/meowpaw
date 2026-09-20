---
id: REF-0002
artifact: reference
status: current
revised: 2026-09-20
---

# Templates

One per artifact kind. A project edits these rather than forking the harness
([R-H-083]).

| Template | Kind | Mode |
| --- | --- | --- |
| [`vision.md`](vision.md) | Vision | Living, project |
| [`constitution.md`](constitution.md) | Constitution | Living, project |
| [`spec.md`](spec.md) | Specification | Living, project |
| [`research.md`](research.md) | Research | Record |
| [`requirement.md`](requirement.md) | Requirement | Record, append-only |
| [`adr.md`](adr.md) | Decision | Record |
| [`bug.md`](bug.md) | Defect | Record |
| [`epic.md`](epic.md) | Epic | Mutable until realised, then a record |
| [`task.md`](task.md) | Task | Mutable until done, then a record |

## Relations

Every template declares where its artifact came from, in front matter, as bare
identifiers ([R-H-315]). Never a Markdown link: a link carries a path, and a
path changes when a repository is reorganised.

Only the **upward** direction is written — `prompted-by`, `elaborates`,
`addresses`, `realises`, `violates`, `supersedes`. What cites an artifact is
computed, because the author cannot know it and a hand-maintained reverse list
drifts ([R-H-317]).

## Adding a kind

A project declares kinds of its own in `.meowpaw/profile.yaml` — a prefix, a
mode, a template and a path ([R-H-332]) — and writes the template beside these.

A declared kind inherits every obligation the default kinds carry. Extensibility
adds artifacts to the method; it is not a way to hold one outside it.

## How these are written

Every section is **a question with a stated failure mode**, not a heading. A
heading gets filled; a question gets answered or refused.

Sections that may be left empty say so and say how you earn it. A template whose
sections must all be filled produces invented content, and invented content is
worse than a blank because it gets cited.
