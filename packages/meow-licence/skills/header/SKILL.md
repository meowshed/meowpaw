---
name: header
description: The licence header this repository declares for its files. It MUST be loaded before any new file is created in a repository with a REUSE.toml, a [licence] table in .meowpaw/profile.toml or licence headers in its files. It MUST NOT be used to change a header a file already carries.
---

<role>
You add the licence header a repository declares to each file you create, and
you never touch a header a file already carries. The licence is the project's
decision, so you copy what it declared and never choose one yourself.
</role>

<steps name="head a new file">
1. Before you create a file, read the declaration: `REUSE.toml` at the
   repository's root, the `header` list under `[licence]` in
   `.meowpaw/profile.toml`, and the header the repository's files already
   carry.
2. If an annotation in `REUSE.toml` covers the new file's path, add nothing,
   because the bulk declaration already covers it.
3. Otherwise take the header's lines from `[licence]`, or where the profile
   declares none, from the header the repository's files carry, and put them
   at the top of the new file in the comment form its format permits. For a
   file that can't carry a comment, write them to `<file>.license` beside it.
4. If the repository declares nothing in any of the three places, write no
   header and say that its licensing is undeclared.
5. After creating files, run `meow-licence check`
   and report what it printed.
</steps>

<rules name="headers">
- L1. Add the declared header to every file you create that no annotation
  covers, code and documents alike, because a file copied out of the
  repository carries only the licensing written in it.
- L2. Write the header lines exactly as the repository declares them, never a
  default of your own, because the header's form is the repository's choice.
- L3. Put the lines in the comment form the file's own format permits, or in a
  `.license` file beside a file that can't carry a comment, because a header
  that breaks the file's syntax breaks the file.
- L4. Where `[licence]` declares no lines, copy the header the repository's
  own files carry, because that is the form the project already chose.
- L5. Never rewrite, reflow, reorder or move a header a file already carries,
  because reformatting a legal notice is modifying it.
- L6. Where the repository declares no licensing, write no header and report
  it as undeclared, and never choose a licence for the project, because the
  licence is the project's decision.
</rules>
