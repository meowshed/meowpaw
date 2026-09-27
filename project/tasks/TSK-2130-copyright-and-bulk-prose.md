---
id: TSK-2130
artifact: task
status: approved
revised: 2026-09-27
epic: EPC-1380
closes: [REQ-3060, REQ-3070]
issue: 446
projected: 3b0236bcaacc
---

# The attribution ban passes a copyright line, and a bulk declaration states its cost

A fixture shows `meow-scm check-message` passing a message that carries a
copyright line, and `meow-licence`'s page and this repository's `REUSE.toml`
state what declaring prose in bulk costs. One task, one branch, one pull
request, one review.

## Acceptance criteria

1. Given a message carrying `SPDX-FileCopyrightText: 2026 A Person
<a@example.org>`, when `meow-scm check-message` runs on it, then it
   reports no attribution. Closed by: a fixture naming REQ-3070.
2. Given `REUSE.toml`, when it is read, then the comment above its prose
   annotation states that a document lifted out of the repository carries no
   licensing. Closed by: the file.

## What to do

Add the fixture to `meow-scm`'s tests, and check `REUSE.toml`'s comment says
what REQ-3060 asks, rewording it only where it doesn't.

## Depends on

Nothing. It changes neither the new unit nor its program.

## Evidence

Not yet.

## Left alone

The ban itself, which already reaches only lines crediting a tool.
