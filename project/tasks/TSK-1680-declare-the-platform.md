---
id: TSK-1680
artifact: task
status: approved
revised: 2026-09-26
epic: EPC-1200
closes: [REQ-1736, REQ-1740, REQ-1742]
issue: 271
---

# Each unit declares the platform it needs and the behaviours it relies on

Each unit declares the platform it needs and the behaviours it relies on, as ADR-1200 decides. One task, one branch, one pull request, one
review.

## Acceptance criteria

1. Given every unit, when its directory is listed, then it holds a `requires.toml` naming a Claude Code version. Closed by: a listing.
2. Given every unit's page, when it is read, then it names the behaviours the unit relies on and where each is documented. Closed by: a search of the pages.

## What to do

Give each unit a `requires.toml` with `claude_code = "2.1.283"`, the version its units were tested on, and a comment saying so. Add a line to each unit's documentation page naming the Claude Code version and the platform behaviours the unit relies on, each with the documentation page that states it.

## Depends on

Nothing. ADR-1200 is approved.

## Evidence

Not yet.

## Left alone

REQ-1738, REQ-1759 and REQ-1764, which ADR-1200 leaves.
