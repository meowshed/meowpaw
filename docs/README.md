# Documentation

How to use what `meowpaw` ships. The record of what must be true and why lives
under `project/`, and this hierarchy stays separate from it.

| Page                                  | What it covers                                                                    |
| ------------------------------------- | --------------------------------------------------------------------------------- |
| [meow-core](meow-core.md)             | The kernel, and the reply shape it imposes                                        |
| [meow-prose](meow-prose.md)           | The writing standard, loaded before Claude writes                                 |
| [meow-prose-gate](meow-prose-gate.md) | A hook that blocks a publish carrying a defect any reader can point to            |
| [meow-verbs](meow-verbs.md)           | The five verification verbs, run as the repository declared them                  |
| [meow-scm](meow-scm.md)               | The commit convention, checked before a message is used                           |
| [meow-git](meow-git.md)               | A pack that refuses a commit on the trunk and checks a branch before it is pushed |
| [meow-method](meow-method.md)         | Runs the method's nine steps, and checks the record they write                    |

One page per unit the harness ships, and a unit's catalogue entry links to its
page.

## Install

Add the marketplace and install the units you want by name:

```bash
claude plugin marketplace add https://meow.retran.me/meowpaw/marketplace.json
claude plugin install meow-verbs@meowpaw
```

Each unit comes with its binaries for macOS, Linux and Windows on ARM64 and
x64, so it needs neither Rust, Python nor Node.js. A later release reaches you when you run
`claude plugin marketplace update meowpaw`, or by itself once you turn on
auto-update for `meowpaw` in the **Marketplaces** tab of `/plugin`.
