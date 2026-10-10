---
name: markdown
description: The stages a Markdown repository binds, what its configuration says, and what a reviewer of its documents checks. It MUST be loaded before binding a stage in, reporting the tools of, or reviewing a document in a repository whose Markdown documents are checked. It MUST NOT be used to write the profile or a tool's configuration.
---

<role>
You read what a repository configured for its Markdown through the pack's
program, and you report what it printed. The program binds each stage from the
files the repository commits, and its binding runs none of the tools it names,
so its table is a proposal the person accepts, never a result. No single
Markdown exists: the render target decides what a document means, so you read
it first.
</role>

<steps name="read the configuration">
1. Run `meow-markdown status` and show its
   output.
2. If it exits 3, report the line starting `unresolved:` as it stands, and
   stop.
3. Otherwise report the render target and each configuration file with what
   reads it, and stop.
</steps>

<steps name="bind the stages">
1. Run `meow-markdown bind` and show the table
   it prints, each comment included.
2. Give the table to the person to put in `.meowpaw/profile.toml`, and stop.
</steps>

<steps name="review Markdown">
1. Run `meow-markdown status` for the render
   target.
2. Read `reviewing.md` before you review a Markdown
   document, and hold the document to each point in it.
3. Report each finding as the line, what is wrong and what would fix it, and
   stop.
</steps>

<rules name="the render target">
- M1. Judge front matter, an admonition or a diagram block only against the
  target `[markdown] target` declares, because a fenced `mermaid` block is a
  picture in one target and a code listing in another. The table below is
  what the skill knows for each known target, from the renderers'
  documentation and not observed by the pack, so check the renderer's own
  configuration before you report a finding on it.
- M2. Where `status` says the target is unknown to the skill, say so and judge
  none of the three, because a guess about a renderer is a finding nobody can
  act on.

| Target       | Front matter                                        | Admonition                                                                         | Diagram block                                                                  |
| ------------ | --------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `github`     | YAML between `---` lines, shown as a table          | `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]` or `[!CAUTION]`                | `mermaid`, `geojson`, `topojson` and `stl` fences render as pictures           |
| `gitlab`     | YAML `---`, TOML `+++` or JSON `;;;`, shown as code | `> [!note]` and the same four others, from GitLab 17.10                            | `mermaid`, and `plantuml` or Kroki's languages where the instance enables them |
| `mkdocs`     | YAML `---`, read as the page's metadata             | `!!! note`, with the `admonition` extension                                        | `mermaid` only through a `pymdownx.superfences` custom fence; otherwise code   |
| `docusaurus` | YAML `---`, with keys such as `title` and `slug`    | `:::note`, `:::tip`, `:::info`, `:::warning` or `:::danger`                        | `mermaid` with `@docusaurus/theme-mermaid` and `markdown.mermaid: true`        |
| `hugo`       | YAML `---`, TOML `+++` or JSON `{`                  | None built in: a theme's shortcode, or `> [!NOTE]` through a blockquote hook       | `mermaid` through a code block render hook the theme supplies                  |
| `mdbook`     | None: a `---` block renders as text                 | `> [!NOTE]` from mdBook 0.5; before that, a preprocessor such as `mdbook-admonish` | `mermaid` through the `mdbook-mermaid` preprocessor                            |
| `obsidian`   | YAML `---`, shown as properties                     | `> [!note]` callouts of any type, folded with `+` or `-`                           | `mermaid` renders natively                                                     |

</rules>

<rules name="the stages">
- M3. Never guess a command for a stage the program printed as unresolved or
  unbound, because a guessed command turns a settled "nothing" into a pass
  nobody checked.
- M4. Write the profile only when the person asks, because the profile is the
  repository's declaration.
- M5. Place the link check under `test` and never under `lint`, because it
  reaches the network and can fail for a reason the author didn't cause,
  while `lint` reads the file alone.
- M6. Name the versions the pack was observed against, lychee 0.24.2,
  markdownlint-cli2 0.23.2 and markdownlint-cli 0.49.1 (RES-0294), and where
  the installed tool is newer, say an observation may be stale, because a
  tool that moved on can change what its output means.
</rules>

<rules name="what the linter can't tell">
- M7. Report a clean lint as clean structure, and never as evidence that the
  document is good, because markdownlint checks heading levels, lists, fences
  and line length, and a document passing all of them can still say nothing.
- M8. Load `reviewing.md` on review for what no command reports, because the
  linter sees that a fence has a language tag and not that it is the right
  one.
</rules>

<rules name="where prose linting stops">
- M9. Say which kind of check ran, structure, style, spelling or links,
  because each answers a different question and one pass or fail hides which.
- M10. Report a style linter such as Vale as checking consistency against a
  declared style, and never as judging whether the writing is good, because
  Vale claims only the first.
- M11. Leave the writing standard to `meow-prose`, which owns it, and hold no
  prose to rules of this pack's own, because two standards that disagree
  leave the author unable to tell which applies.
</rules>

<rules name="what must never happen">
- M12. Never run markdownlint-cli against a `.markdownlint-cli2.*` file,
  because it ignores that file and runs its defaults, so the run looks clean
  with no configuration behind it.
- M13. Never fail a check on an unreachable link without saying it was
  unreachable, because a site that is down is no defect in the document, and
  `links` exits 3, not 1, to keep the two apart.
- M14. Never run a spell check, or report one as meaningful, where the
  repository keeps no project word list, because it then reports every proper
  noun and is switched off within a week.
</rules>
