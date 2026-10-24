# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Every specification answers the template's seven questions (TSK-5010, REQ-2250, ADR-2630, SPC-1090 "The
questions a specification answers").

The wording of the section is the `spec` template's, so the test reads the questions from it. A question is
answered by text, or left as the word `unanswered`, and a question missing or empty fails.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = sorted((ROOT / "project" / "specs").glob("SPC-*.md"))
TEMPLATE = ROOT / "plugins" / "meow-flow" / "templates" / "spec.md"


def questions_section(text):
    """The text under the `## Questions` heading, up to the next `## ` heading, outside fenced blocks."""
    found, inside, fenced = [], False, False
    for line in text.splitlines():
        if line.startswith(("```", "~~~")):
            fenced = not fenced
        if not fenced and line.startswith("## "):
            inside = line.strip() == "## Questions"
            continue
        if inside:
            found.append(line)
    return "\n".join(found)


def answers(section):
    """Each `### ` question of a section with the text under it."""
    parts = re.split(r"^### (.+)$", section, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


TEMPLATE_QUESTIONS = list(answers(questions_section(TEMPLATE.read_text(encoding="utf-8"))))


class SpecificationQuestions(unittest.TestCase):
    def test_the_template_holds_seven_questions(self):
        """TSK-5010 criterion 1, REQ-2250: the template the specifications follow lists seven questions."""
        self.assertEqual(len(TEMPLATE_QUESTIONS), 7, TEMPLATE_QUESTIONS)

    def test_there_are_specifications_to_hold(self):
        """TSK-5010 criterion 1, REQ-2250: a test over no specification proves nothing, so it fails."""
        self.assertGreater(len(SPECS), 0)

    def test_each_specification_answers_each_question_or_marks_it_unanswered(self):
        """TSK-5010 criterion 1, REQ-2250: each specification carries all seven questions, answered or `unanswered`."""
        for path in SPECS:
            with self.subTest(spec=path.name):
                section = questions_section(path.read_text(encoding="utf-8"))
                self.assertTrue(section.strip(), "no `## Questions` section")
                held = answers(section)
                self.assertEqual(list(held), TEMPLATE_QUESTIONS, "the questions, in the template's order")
                empty = [question for question, answer in held.items() if not answer]
                self.assertEqual(empty, [], "questions with no answer and not marked `unanswered`")

    def test_a_section_without_its_questions_fails(self):
        """TSK-5010 criterion 1, REQ-2250: the check fails a specification missing a question or an answer."""
        full = "## Questions\n\n" + "\n\n".join(f"### {q}\n\nunanswered" for q in TEMPLATE_QUESTIONS)
        self.assertEqual(list(answers(questions_section(full))), TEMPLATE_QUESTIONS)
        short = full.replace(f"### {TEMPLATE_QUESTIONS[0]}\n\nunanswered", "")
        self.assertNotEqual(list(answers(questions_section(short))), TEMPLATE_QUESTIONS)
        blank = full.replace("unanswered", "", 1)
        self.assertIn(TEMPLATE_QUESTIONS[0], [q for q, a in answers(questions_section(blank)).items() if not a])


if __name__ == "__main__":
    unittest.main()
