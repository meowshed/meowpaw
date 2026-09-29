# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""What the `prose` agent states about its report, as SPC-1030 "What an agent reports" and SPC-1090 "The review
before a gate" give it (REQ-0816)."""

import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
AGENT = UNIT / "agents" / "prose.md"
OUTCOMES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED")


def body():
    return AGENT.read_text(encoding="utf-8").split("---\n", 2)[2]


def word_in(word, text):
    """Whether `text` names the outcome `word` as a whole word, so DONE_WITH_CONCERNS doesn't name DONE."""
    return re.search(rf"(?<![A-Za-z_]){word}(?![A-Za-z_])", text) is not None


def sentences(text):
    """Each sentence of a prompt, with a list item and a table row each ending one, white space made single and
    backticks dropped, so a rule is read clause by clause whether it is prose, a list or a table."""
    out = []
    for part in re.split(r"\n(?=\s*(?:[-|*]|\d+\.)\s)|\n\s*\n", text):
        part = re.sub(r"\s+", " ", part.replace("`", "")).strip()
        out.extend(s for s in re.split(r"(?<=[.;])\s+", part) if s)
    return out


class ProseReport(unittest.TestCase):
    """TSK-2702 criterion 3, REQ-0816: `prose` states when it reports each of the four outcomes, puts the outcome
    line first and the cause second, and quotes no more than the span a finding names, 25 words at most."""

    def test_it_names_the_four_outcomes(self):
        """TSK-2702 criterion 3, REQ-0816: prose names DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT and BLOCKED."""
        self.assertEqual({w for w in OUTCOMES if word_in(w, body())}, set(OUTCOMES))

    def test_it_says_when_it_reports_each_outcome(self):
        """TSK-2702 criterion 3, REQ-0816, SPC-1090 "The review before a gate": DONE for a review in the scope
        asked or for the default reader; DONE_WITH_CONCERNS where a file the change touched couldn't be read;
        NEEDS_CONTEXT where the brief names nothing it can review; BLOCKED where a tool call was denied."""
        rows = (
            ("DONE", r"scope|reader|whatever"),
            ("DONE_WITH_CONCERNS", r"could ?n.t (be )?read|touched"),
            ("NEEDS_CONTEXT", r"names nothing|no text|nothing (to|you can|it can)|exist"),
            ("BLOCKED", r"denied"),
        )
        text = sentences(body())
        for word, pattern in rows:
            with self.subTest(outcome=word):
                self.assertTrue(any(word_in(word, s) and re.search(pattern, s, re.I) for s in text),
                                f"no sentence says when {word} is reported ({pattern})")

    def test_the_outcome_is_the_first_line_and_the_cause_the_second(self):
        """TSK-2702 criterion 3, REQ-0816, SPC-1030 "What an agent reports": the outcome line comes first, before
        the verdict, and the cause second."""
        text = sentences(body())
        self.assertTrue(any("outcome:" in s and re.search(r"first line", s, re.I) for s in text),
                        "no sentence puts outcome: on the first line")
        self.assertTrue(any(re.search(r"\bcause\b", s, re.I) and re.search(r"second line", s, re.I) for s in text),
                        "no sentence puts the cause on the second line")

    def test_it_quotes_no_more_than_the_span(self):
        """TSK-2702 criterion 3, REQ-0816: prose quotes nothing beyond the span a finding names, 25 words at most,
        which V1 already holds and this change must keep."""
        self.assertTrue(any(re.search(r"\bquot", s, re.I) and re.search(r"\bspan\b", s, re.I) and re.search(r"\b25 words\b", s)
                            for s in sentences(body())), "no rule limits a quotation to the finding's span, 25 words at most")


if __name__ == "__main__":
    unittest.main()
