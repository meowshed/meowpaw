# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The question section of the specification template, and the design and spec steps that name and frame a
decision's concerns (TSK-5000, REQ-2252, ADR-2630, SPC-1090 "The questions a specification answers").

The template and the step files are text a model follows, so each fixture reads them for what the requirement
asks and fails where it is missing.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_FLOW_BIN", UNIT / "bin" / "paw"))
STEPS = UNIT / "skills" / "method" / "steps"

# The seven questions SPC-1090 names, as the words each heading carries.
QUESTIONS = [
    r"what .*for",
    r"depends on\b(?! it)|what it depends on",
    r"what depends on it",
    r"data lives",
    r"trust boundary",
    r"fails",
    r"deployed",
]


def template(kind):
    env = {**os.environ, "CLAUDE_PLUGIN_DATA": "/nonexistent/u"}
    done = subprocess.run([str(BIN), "template", kind], capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL)
    # `paw template` prints the path of the template in force, and the test reads the file it names.
    if done.returncode == 0:
        done.stdout = Path(done.stdout.strip()).read_text(encoding="utf-8")
    return done


class SpecTemplate(unittest.TestCase):
    def test_tsk_5000_criterion_1_the_spec_template_lists_seven_questions_each_unanswered(self):
        """TSK-5000 criterion 1, REQ-2252: `paw template spec` has one section of seven questions, each `unanswered`."""
        done = template("spec")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        sections = re.split(r"\n(?=## )", done.stdout)
        found = [s for s in sections if re.match(r"## .*[Qq]uestion", s)]
        self.assertEqual(len(found), 1, done.stdout)
        section = found[0]
        questions = re.findall(r"^### (.+)$", section, re.M)
        self.assertEqual(len(questions), 7, section)
        for pattern in QUESTIONS:
            with self.subTest(question=pattern):
                self.assertEqual(len([q for q in questions if re.search(pattern, q, re.I)]), 1, questions)
        answers = re.split(r"^### .+$", section, flags=re.M)[1:]
        self.assertEqual([a.strip() for a in answers], ["unanswered"] * 7, section)

    def test_tsk_5000_criterion_2_the_decision_template_names_the_optional_concerns(self):
        """TSK-5000 criterion 2, REQ-2252: `paw template adr` carries a `concerns:` list the front matter may leave empty."""
        done = template("adr")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        front = done.stdout.split("---")[1]
        self.assertRegex(front, r"(?m)^concerns: \[\]")
        self.assertRegex(front, r"(?m)^concerns:.*#.*optional")


class Steps(unittest.TestCase):
    def test_tsk_5000_criterion_3_the_design_step_names_each_concern_in_concerns(self):
        """TSK-5000 criterion 3, REQ-2252: `design.md` tells the step to name each concern in `concerns:`."""
        text = " ".join((STEPS / "design.md").read_text(encoding="utf-8").split())
        self.assertRegex(text, r"[^.]*\bconcern[^.]*`concerns:`[^.]*\.")
        self.assertRegex(text, r"performance, security or upgrade")

    def test_tsk_5000_criterion_3_the_spec_step_frames_each_concern_in_a_section_it_names(self):
        """TSK-5000 criterion 3, REQ-2252: `spec.md` tells the step to frame each concern in a section whose heading names it."""
        text = " ".join((STEPS / "spec.md").read_text(encoding="utf-8").split())
        self.assertRegex(text, r"[^.]*\bconcern[^.]*\bheading names it[^.]*\.")


if __name__ == "__main__":
    unittest.main()
