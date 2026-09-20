#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The mechanically checkable half of the writing standard.

Judgements - whether a rule carries its reason, whether the voice has an author
- are review criteria, not gate checks, and are deliberately absent here.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"_archive", ".claude", ".git", "node_modules", "target", ".github", "tools", "templates"}

# Each pattern matches the defect, not a word that can also appear innocently.
# "obviously bad" is an adjective doing work; "Obviously, X" is a hedge. A check
# that trips on the first gets switched off within a week, and then it catches
# neither.
PATTERNS = {
    "filler": re.compile(
        r"\b(of course|note that|it is important to|basically)\b", re.I
    ),
    # B6: words that judge the reader's experience.
    "judges the reader": re.compile(r"\b(simply|easily|straightforward)\b", re.I),
    # B7: hype.
    "hype": re.compile(
        r"\b(robust|seamless|leverage|delve|crucial|pivotal|game-changing"
        r"|cutting-edge)\b",
        re.I,
    ),
    # D4: the long word where a short one exists.
    "long word": re.compile(
        r"\b(utilize|initiate|terminate|facilitate|approximately|obtain)\b"
        r"|due to the fact that",
        re.I,
    ),
    # D6: the empty frame. The sentence inside it is the whole sentence.
    "empty frame": re.compile(
        r"\b(in terms of|with respect to|in the context of|at the level of"
        r"|from the perspective of)\b",
        re.I,
    ),
    # D9, D10: demonstrative padding and stock metaphors.
    "padding": re.compile(
        r"\b(aforementioned|this particular|the respective)\b"
        r"|under the hood|low-hanging fruit|silver bullet|at the end of the day",
        re.I,
    ),
    # The frame announces that a claim is coming instead of making it.
    "announcing frame": re.compile(
        r"\b(worth noting|by the way|as an aside|incidentally|as a side note)\b",
        re.I,
    ),
    # A failure is reported by its cause and its fix, not by its drama.
    "dramatic failure": re.compile(
        r"\b(unfortunately|sadly|regrettably|uh oh|oh no)\b|there seems to be", re.I
    ),
    # H5: a double negative has two readings.
    "double negative": re.compile(r"\bnot un\w+", re.I),
    # H8: spell out the Latin abbreviation.
    "latin abbreviation": re.compile(r"\b(e\.g\.|i\.e\.|etc\.)"),
    # Sentence start, not line start: the prose is hard-wrapped, so a line can
    # begin mid-sentence and "two\nobviously bad" is not a hedge.
    "hedge": re.compile(
        r"(?:\A|[.!?][\"')\]]?\s+)(Obviously|Clearly|Needless to say)\b"
        r"|,\s*obviously\s*,",
    ),
    "weak opener": re.compile(r"(?:\A|[.!?][\"')\]]?\s+)There (is|are|was|were)\b"),
    # F: British spelling. A word whose domain spells it another way keeps that
    # spelling, and `artifact` is the term of art in software and the name of a
    # field every check reads.
    "american spelling": re.compile(
        r"\b(behaviou?r(?<!behaviour)s?|colou?r(?<!colour)s?|favou?r(?<!favour)s?"
        r"|honou?r(?<!honour)|labou?r(?<!labour)|cent(?:er|ers)|met(?:er|ers)"
        r"|analyz\w*|catalog(?!ue)s?|dialog(?!ue)s?|defense|offense|pretense"
        r"|fulfill|skillful|willful|travel(?:ed|ing)|cancel(?:ed|ing)"
        r"|model(?:ed|ing)|label(?:ed|ing)|gray|judgment|acknowledgment)\b",
    ),
    "ai attribution": re.compile(
        r"co-authored-by:.*(claude|anthropic|copilot)|generated with \[|noreply@anthropic",
        re.I,
    ),
}
# A document that states a rule quotes the wording the rule bans, and quoting a
# defect is not committing one.
ALLOWED = {"CLAUDE.md", "check_prose.py", "RES-0038-reporting.md"}

# Spelled as written by whoever owns the name. A borrowed name is not our prose.
PROPER_NOUNS = ("Diátaxis", "Слово живое и мёртвое")

# What is quoted, cited or executed is not what we wrote, and the standard binds
# only what we wrote. Blanking rather than deleting keeps every offset, so a
# reported line number still points at the line.
NOT_OUR_PROSE = (
    re.compile(r"^---\n.*?^---\n", re.S | re.M),  # front matter
    re.compile(r"```.*?```", re.S),  # fenced code
    re.compile(r"`[^`\n]+`"),  # inline code
    re.compile(r"\]\([^)]*\)"),  # link destinations
    re.compile(r"^\s*(?:[-*]\s+)?\[[^\]]+\]:\s*\S+", re.M),  # link definitions
    re.compile(r"<https?://[^>]*>|(?<![(<])https?://\S+"),  # bare URLs
    re.compile(r"^>.*$", re.M),  # block quotations: someone else's words
)


def mask(text: str) -> str:
    """Blank what we did not write, keeping the length and the line breaks."""

    def blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    for pattern in NOT_OUR_PROSE:
        text = pattern.sub(blank, text)
    for proper in PROPER_NOUNS:
        text = text.replace(proper, " " * len(proper))
    return text


def main() -> int:
    failures = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in files:
            # The attribution ban states its own patterns; the rule is not a
            # violation of itself.
            if not name.endswith(".md") or name in ALLOWED or "commits" in name:
                continue
            path = os.path.join(root, name)
            relative = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as handle:
                prose = mask(handle.read())

            def report(line_start: int, label: str, found: str) -> None:
                line = prose[:line_start].count("\n") + 1
                failures.append(f"{relative}:{line}: {label}: {found!r}")

            # F5: ASCII only outside code.
            for match in re.finditer(r"[^\x00-\x7F]", prose):
                report(match.start(), "non-ascii", match.group(0))
            for label, pattern in PATTERNS.items():
                for match in pattern.finditer(prose):
                    report(match.start(), label, match.group(0))

    for failure in sorted(failures):
        print(failure)
    print(f"{len(failures)} prose findings")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
