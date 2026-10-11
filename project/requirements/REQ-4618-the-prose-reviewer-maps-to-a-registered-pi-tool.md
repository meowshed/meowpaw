---
id: REQ-4618
artifact: requirement
topic: pi-packages
class: functional
status: approved
verification: static
elaborates: RES-0340
revised: 2026-10-11
---

# REQ-4618

The prose reviewer maps to a registered Pi tool, `meow-prose-review`, whose
nested model call carries the reply shape and prefers glm 5.3 flash; a model
the `MEOW_NESTED_MODEL` environment variable names goes first. The call
inlines the standard it reviews against, read from the package's own
`skills/writing/` at load, because a nested call reads no file and holds no
skill, and every prompt and supporting file the extension loads is bundled
inside the package (REQ-4130).