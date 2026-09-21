---
id: BUG-1070
artifact: bug
status: approved
severity: minor
violates: REQ-1115
found: 2026-09-21
revised: 2026-09-21
issue: 40
---

# The records are written below the standard the constitution requires

## Reproduction

Over the seven defect records, six tasks, the epic, the decision and the
specification, 8,202 words, as #39 left the tree:

```bash
grep -rn "^\*\*" project/bugs/*.md project/tasks/*.md project/epics/*.md \
  project/adrs/ADR-1000*.md project/specs/*.md | wc -l          # 9
```

Counting by hand for the shapes no check reads:

```text
paragraphs opening in bold      9     F4 allows one bold phrase per section
sentences over 35 words        30     the standard allows 1 per 1,000 words
counted openers                 4     state the first item, not how many
'mechanism' as a category word  4     name the thing
```

## What the system does

`check_prose` reports nothing on these files. It reads words: it caught `Δ`, it
caught `there is`, and it cannot see a paragraph that opens in bold, a sentence
of 48 words, or a claim written as a proverb with its reason missing.

Three bold fragments in a row under one heading in EPC-1000 were headings
written as bold text. Sentences such as "A template is how a dead field
outlives its own removal" read as conclusions and carry no reason, where the
standard asks for the reason in the same sentence.

## What it should do, and why

REQ-1115 obliges loadable material to be written in the form it should produce,
and `CLAUDE.md` extends one standard over documents, commit messages, pull
request bodies and replies. A record that reads as rules handed down teaches
the next author to write the same way, which is how a house style decays one
file at a time.

The gap is mechanical as well as editorial: the check that guards this standard
sees vocabulary and not shape, so a whole class of defect reaches `main`
unreported.

## Triage

Implementation for the prose, and a gap for the check. The texts are edited
here; a check that reads shape belongs to the unit `CLAUDE.md` already names,
`meow-prose`, and is not built in this change.

## Closed by

The nine bold paragraph openers reduced to two, both of which mark the one
thing a skimmer must not miss in their section: that BUG-1005 and BUG-1050 were
written after the work they record. The counted openers, the dangling `That`
and the category words are rewritten with the reason beside the claim, and
every number and citation is unchanged.

The nine templates and the two files `meow-core` ships state the obligation
where an author meets it, because a template is what the next author copies.

The style and the fragment were rewritten rather than annotated. Both explained
themselves in this project's own words, `unresolved verb` and a requirement
identifier, to a reader who has installed a plugin and never seen the record.
Both now open with the failure a reader recognises: a report where every
sentence is true and the one check that never ran sits in the middle.

The twenty pull request bodies carried the same defect at greater length, with
fifty-three verdict labels written as bold fragments. Each body was read and
rewritten, and four carried claims that later turned out to be false, about
`pre-squash-backup` holding the deleted records and about `force-for-plugin`
holding the shape. Those now carry the correction beside the claim.

The two skills under `.claude/skills/` taught the defect they forbid.
`technical-english` illustrated F4 with "a list of decrees" and the pattern
catalogue with "the voice of a statute", and I copied that vocabulary into this
repository and into my replies. Both now name the thing plainly, and the
`commits` skill loses its two counted openers and three bold list items.
