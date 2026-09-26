# Templates

One template per kind of artifact, which `meow-method`'s steps write from. A
repository changes one by putting its own at `.meowpaw/templates/<kind>.md`,
and `meow-method template <kind>` prints the one in force.

| Template          | Kind          | Lifetime                             |
| ----------------- | ------------- | ------------------------------------ |
| `vision.md`       | Vision        | Living                               |
| `constitution.md` | Constitution  | Living                               |
| `spec.md`         | Specification | Living                               |
| `research.md`     | Research      | A record, frozen on approval         |
| `requirement.md`  | Requirement   | A record, one obligation per file    |
| `adr.md`          | Decision      | A record                             |
| `epic.md`         | Epic          | A record, its marks kept current     |
| `task.md`         | Task          | A record, its evidence added on done |
| `bug.md`          | Defect        | A record                             |
| `insight.md`      | Insight       | A record, written when learned       |
| `profile.toml`    | Profile       | Configuration, rewritten freely      |

Every template opens with a paragraph or section that lets a reader stop:
what the artifact covers and what it doesn't. A section may be answered
"Nothing", with the reason, and an answer has to be earned, because a padded
section reads as a claim and gets cited.

Every template names where its artifact came from in its front matter, as bare
identifiers and never as links, because a path changes when a repository is
reorganised. Only the upward direction is written: what cites an artifact is
computed, because its author can't know it.
