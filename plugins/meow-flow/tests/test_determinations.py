# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""The method's step files name a subcommand for each mechanical determination, and its rules say how a
subcommand's output is cited (TSK-4350, SPC-1080 "Each subcommand makes one determination").

A step file is text a model follows, so each fixture reads the files for the instruction a requirement asks of
them and fails where one is missing.
"""

import json
import re
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
METHOD = UNIT / "skills" / "method"
STEPS = METHOD / "steps"

# A determination a program makes: a count, a coverage, a staleness, a resolution, a readiness or an allocation.
DETERMINATION = re.compile(
    r"\b(count(?:s|ed)?|coverage|stale(?:ness)?|resol(?:ve|ves|ved|ution)|ready|allocate[sd]?|identifier block"
    r"|set difference)\b",
    re.IGNORECASE,
)

# Items that match and ask for no determination, each with its reason (REQ-1172 leaves a judgement to the model).
EXEMPT = {
    ("implement.md", "never cite coverage as evidence"): "names coverage as something not to cite, and asks for none",
    ("research.md", "secondary coverage lags"): "means press coverage of a project, and not a count",
    ("spec.md", "Allocate a document's identifier to its subject"): "chooses a subject for a name: a judgement",
    ("spec.md", "which one is stale is a judgement"): "says the choice is a judgement and asks for none",
}


def items(text):
    """The paragraphs and numbered or lettered rules of a step file, each on one line."""
    parts = re.split(r"\n\s*\n|\n(?=(?:- [A-Z]\d+\.|\d+\. ))", text)
    return [" ".join(part.split()) for part in parts]


def unnamed(name, text):
    """The items of `text` that ask for a determination and name no `paw` subcommand."""
    found = []
    for item in items(text):
        if not DETERMINATION.search(item) or "paw " in item:
            continue
        if any(name == exempt and phrase in item for exempt, phrase in EXEMPT):
            continue
        found.append(item)
    return found


class StepFilesNameTheSubcommand(unittest.TestCase):
    def test_a_step_that_asks_for_a_count_with_no_subcommand_fails(self):
        """TSK-4350 criterion 1, REQ-1172: the fixture can fail."""
        self.assertEqual(
            unnamed("fixture.md", "3. Count the requirements the decision addresses and list them.\n"),
            ["3. Count the requirements the decision addresses and list them."],
        )
        self.assertEqual(unnamed("fixture.md", "3. Run `paw count` and list what it prints.\n"), [])

    def test_every_determination_in_a_step_file_names_a_subcommand(self):
        """TSK-4350 criterion 1, REQ-1172."""
        missing = {}
        for path in sorted(STEPS.glob("*.md")):
            found = unnamed(path.name, path.read_text(encoding="utf-8"))
            if found:
                missing[path.name] = found
        self.assertEqual(missing, {}, "a step file asks for a determination and names no `paw` subcommand")


class MethodRules(unittest.TestCase):
    def setUp(self):
        self.text = " ".join((METHOD / "SKILL.md").read_text(encoding="utf-8").split())

    def test_a_cited_output_carries_the_command_its_status_its_output_and_the_tree(self):
        """TSK-4350 criterion 2, REQ-1178."""
        self.assertRegex(self.text, r"- M\d+\. Cite a subcommand's output as evidence[^.]{0,200}exit status")
        self.assertRegex(self.text, r"exit status[^.]{0,120}tree revision")

    def test_a_contradiction_between_a_subcommand_and_the_tree_is_reported(self):
        """TSK-4350 criterion 2, REQ-1180."""
        self.assertRegex(self.text, r"- M\d+\. Where a subcommand's output contradicts[^.]{0,200}report both")
        self.assertRegex(self.text, r"contradicts[^.]{0,260}never defer")


class SessionStart(unittest.TestCase):
    def test_the_session_start_hook_runs_the_waiting_report(self):
        """TSK-4350 criterion 3, REQ-1190."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        commands = [h["command"] for group in hooks["SessionStart"] for h in group["hooks"]]
        self.assertTrue(any(c.endswith("/bin/paw status --waiting") for c in commands), commands)


if __name__ == "__main__":
    unittest.main()
