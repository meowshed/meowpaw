---
id: TSK-1110
artifact: task
status: approved
revised: 2026-09-22
epic: EPC-1010
closes:
  [
    REQ-0990,
    REQ-0991,
    REQ-0992,
    REQ-0993,
    REQ-0994,
    REQ-0995,
    REQ-0996,
    REQ-0997,
    REQ-0998,
    REQ-3188,
    REQ-1062,
    REQ-1064,
    REQ-1066,
  ]
issue: 48
---

# Ship the standard as `meow-prose`

One task, one branch, one pull request, one review.

## What to do

Create `plugins/meow-prose/` with its manifest and its licence header, and list
it in `.claude-plugin/marketplace.json`. It installs without `meow-core` and
without `meow-prose-gate` (REQ-0012, REQ-0076).

Write the skill in `plugins/meow-prose/skills/writing/`. It states one standard
over everything the harness produces: artifacts, code comments, commit
messages, review findings and replies (REQ-0990). Start from the first two
texts in the appendix of ADR-1010, the standard as it stands and the shorter
draft, and pull the rules out of the first rather than writing new ones from
memory. The rewrite has two goals:

- Shorter, because a rule nobody can recall is a rule nobody applies, and the
  standard asks the same of itself that it asks of every text (REQ-3188). Keep
  every rule and its reason, and drop what carries nothing.
- Universal, because the borrowed text names this project's own habits, and a
  unit installed in somebody else's repository states rules that hold there.

The skill must state these rules, each with its reason (REQ-0994):

- A sentence names the actor and uses the verb (REQ-0991).
- A draft declares the reader it is written for (REQ-0993).
- British English (REQ-0995), one language per repository, declarable there
  (REQ-0996), and a technical term keeps its own domain's spelling (REQ-0997).
- The sections each document type carries, and their order (REQ-0998).
- Prose carries its content in the fewest tokens that content allows, and never
  loses content to get shorter (REQ-3188).

Before cutting anything, list every criterion the standard as it stands
carries: each numbered rule in its sections on leading with the answer, voice,
sentences, words, structure, formatting, plain English and code; each pattern
in its catalogue; each check in its self-review; and each document type's
skeleton. Publish the list as a table in the pull request, with a row per
criterion naming where it lands in the new skill or why it was dropped. A
shorter standard that silently lost a criterion is the loss REQ-3188 forbids,
and the table is how a reviewer sees that none was lost.

Write the description so it says when to load the skill, and not what the
skill contains (REQ-1062): before writing a document, a commit message, a pull
request body, a comment or a reply. The skill has to be in context before the
text is written (REQ-0992), because a standard applied afterwards is a rewrite
and gets skipped when time is short.

Put every obligation within the skill's first five thousand tokens and ahead of
its explanations (REQ-1064, REQ-1066), so a truncation after compaction costs
an explanation and never a rule. Anything past that moves into a supporting
file in the skill's directory.

Write the documentation page for the unit, which `docs/` holds and the
marketplace entry links to.

## Depends on

No other task. `meow-core` exists, and nothing here needs it.

## Evidence

In progress. #70 ships the unit, and the skill follows ADR-1020: tagged
throughout, with the document rules and the code rule moved into
`document-types.md` to keep the body under its limit.

#71 aligns `document-types.md` with the kinds of the record, the vision to the
defect record, as the record actually writes them, and puts a shipped template
ahead of the skill's own skeleton.

```text
$ claude plugin install meow-prose@meowpaw --scope local    # in a scratch repository
Successfully installed plugin: meow-prose@meowpaw (scope: local)

$ claude plugin list
meow-prose@meowpaw  Version: 0.1.0  Scope: local  Status: enabled
```

Token counts on Sonnet 5, measured as the difference in input tokens with the
file appended: `SKILL.md` 4,801, `patterns.md` 3,047, `document-types.md`
2,594 and `self-review.md` 1,105. Every obligation in the body sits inside its
first 5,000 tokens (REQ-1064, REQ-1066).

REQ-0992 is not met yet. In a clean repository on Sonnet 5, with the skill
listed in every session, the model loaded it in 0 of 9 runs across a commit
message, an install section and a pull request body, against 1 of 9 for the
first description. ADR-1020 answers this with a `SessionStart` hook, which
TSK-1240 builds, and this task closes on the routing measured with that hook.

## Left alone

The reviewer, the gate and the replacement path, which TSK-1120, TSK-1140 and
TSK-1130 build. This task ships the standard and nothing that holds it.
