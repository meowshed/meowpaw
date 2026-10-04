---
id: REQ-4106
artifact: requirement
status: approved
cites: RES-0340
---

# A hook handler shells out to the existing native binary

Where a Claude Code hook runs a native binary (`meow-git commit-guard`,
`meow-prose-gate check`, `meow-loop guard`, `meow-github governance-guard`,
`paw status --waiting`), the Pi event handler shells out to the same binary
with the same arguments. The handler interprets the exit code and output the
same way the Claude Code hook mechanism does: exit 0 is pass-through, exit 2
is feedback to the model, and non-zero with output is a block.

Rationale: The native binaries carry test coverage, Rust performance and
deterministic behaviour. Porting each to TypeScript would duplicate tested
logic and introduce a second implementation to maintain. Shelling out
preserves the existing implementation and lets the extension add structured
output and event composition around it.
