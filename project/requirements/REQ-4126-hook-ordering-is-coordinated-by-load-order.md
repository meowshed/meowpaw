---
id: REQ-4126
artifact: requirement
status: draft
cites: RES-0340
---

# Hook ordering between extensions is coordinated by load order

Where two or more extensions register handlers for the same event (for example,
both the prose gate and the git guard intercept `user_bash` for `git commit`),
the extensions' load order determines which handler runs first. Pi runs
handlers in extension load and registration order. A meowpaw extension that
must run before another declares this in its documentation and in the package's
`package.json` ordering, not in a platform mechanism, because Pi provides none.

Rationale: Claude Code merges hooks from different plugins and runs them
independently. Pi composes event handlers in load order, and a handler that
returns a blocking result prevents later handlers from running. The meowpaw
extensions must be ordered so that the prose gate (which blocks bad text) runs
before the git commit guard (which checks the convention), because a message
that fails the prose gate should not reach the convention check. This ordering
was unsupportable in Claude Code and is explicit in Pi.
