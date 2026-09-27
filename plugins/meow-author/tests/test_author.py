# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every condition `meow-author check` fails on, as SPC-1030 states.

Each fixture builds a scratch repository holding one unit, or a repository's
own `.claude/`, and runs the check. `MEOW_AUTHOR_BIN` names the launcher to
test, so the fixtures can first run against a program that reports nothing
and be seen failing (REQ-2072).
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_AUTHOR_BIN", UNIT / "bin" / "meow-author"))
GOOD = """---
name: demo
description: The demo skill. It MUST be loaded before a demo is run.
---

<role>
You run the demo.
</role>

<steps name="demo">
1. Read `${CLAUDE_SKILL_DIR}/notes.md`.
2. Run the demo, report what it printed, and stop.
</steps>

<rules name="demo">
- D1. Run the demo once, because twice changes nothing.
</rules>
"""

NOTES = "<rules name=\"notes\">\n- N1. Note it, because it helps.\n</rules>\n"


class Repository:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def check(self, *paths):
        return subprocess.run([str(BIN), "check", *paths], cwd=self.root, capture_output=True, text=True)

    def run_cost(self):
        return subprocess.run([str(BIN), "cost"], cwd=self.root, capture_output=True, text=True)


def unit(skill=GOOD, extra=None):
    files = {"plugins/meow-demo/skills/demo/SKILL.md": skill, "plugins/meow-demo/skills/demo/notes.md": NOTES}
    files.update(extra or {})
    return files


class Check(unittest.TestCase):
    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def fails(self, files, expected, *paths):
        done = self.repo(files).check(*paths)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(expected, done.stdout)

    def test_a_well_formed_unit_passes(self):
        done = self.repo(unit()).check()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 authoring failures", done.stdout)

    def test_a_heading_fails(self):
        """REQ-1112: one structural vocabulary, with no Markdown headings."""
        self.fails(unit(GOOD + "\n## A heading\n"), "a Markdown heading, where the prompt uses tags")

    def test_a_tag_outside_the_vocabulary_fails(self):
        """REQ-1114: the vocabulary is fixed, so a tag outside it is a defect."""
        self.fails(unit(GOOD + "\n<context>\nMore.\n</context>\n"), "<context> is not in the vocabulary SPC-1030 states")

    def test_a_nested_tag_fails(self):
        """REQ-1128: one format across units, so one check audits them all."""
        self.fails(unit(GOOD.replace("<role>\nYou run the demo.", "<role>\n<rules>\n- R1. x.\n</rules>")), "<rules> opens inside <role>")

    def test_a_tag_never_closed_fails(self):
        """REQ-1128: a tag left open is a malformed prompt."""
        self.fails(unit(GOOD.replace("</rules>\n", "")), "<rules> is never closed")

    def test_text_outside_every_tag_fails(self):
        """REQ-1120: every obligation sits inside a tag, where it can be extracted."""
        self.fails(unit(GOOD + "\nAlways run twice.\n"), "text outside every tag")

    def test_a_skill_without_a_description_fails(self):
        """REQ-1110: every unit states what it is for and when to load it."""
        self.fails(unit(GOOD.replace("description: The demo skill. It MUST be loaded before a demo is run.\n", "")), "has no description in its front matter")

    def test_a_commands_directory_fails(self):
        """REQ-1111: one kind of loadable unit, a command being a skill only a person invokes."""
        self.fails(unit(extra={"plugins/meow-demo/commands/go.md": "Go.\n"}), "ships a commands/ directory")

    def test_a_supporting_file_nothing_names_fails(self):
        """REQ-1124, REQ-1142: the core names each supporting file, or nothing loads it."""
        self.fails(unit(extra={"plugins/meow-demo/skills/demo/orphan.md": NOTES}), "orphan.md is never named by the skill's core")

    def test_a_path_without_the_directory_variable_fails(self):
        """REQ-2688: supporting files are addressed through the platform's directory variable."""
        self.fails(unit(GOOD.replace("`${CLAUDE_SKILL_DIR}/notes.md`", "`../demo/notes.md`")), "climbs out of the file with no directory variable")

    def test_a_procedure_without_a_stopping_point_fails(self):
        """REQ-1122: a procedure states where it stops."""
        self.fails(unit(GOOD.replace("report what it printed, and stop.", "and read its output.")), "has a procedure and no step naming where it stops")

    def test_a_repositorys_own_skills_are_checked(self):
        """REQ-1672, REQ-1678: a repository checks its own material with the shipped capability."""
        files = {".claude/skills/local/SKILL.md": GOOD.replace("${CLAUDE_SKILL_DIR}/notes.md", "${CLAUDE_SKILL_DIR}/local-notes.md") + "\n## A heading\n",
                 ".claude/skills/local/local-notes.md": NOTES}
        self.fails(files, ".claude/skills/local/SKILL.md", ".claude")

    def test_nothing_to_check_is_unchecked(self):
        done = self.repo({"README.md": "Nothing here.\n"}).check(".")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unchecked", done.stdout)



class Cost(unittest.TestCase):
    """ADR-1460: meow-author cost reports each unit's cost against its budget."""

    def repo(self, budget="permanent_characters = 200\n", description="The demo skill. It MUST be loaded before a demo is run.", when=""):
        skill = GOOD.replace("description: The demo skill. It MUST be loaded before a demo is run.", f"description: {description}" + (f"\nwhen_to_use: {when}" if when else ""))
        files = unit(skill, {"plugins/meow-demo/.claude-plugin/plugin.json": '{"name": "meow-demo"}\n'})
        if budget is not None:
            files["plugins/meow-demo/budget.toml"] = budget
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository.run_cost()

    def test_a_unit_within_its_budget_passes_and_names_skill_doctor(self):
        """REQ-1072: the report gives each unit's cost, and names where its use is reported."""
        done = self.repo()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meow-demo: 55 of 200 characters on every turn", done.stdout)
        self.assertIn("/skill-doctor", done.stdout)

    def test_a_unit_over_its_budget_fails(self):
        """REQ-1072, REQ-1074: the cost report fails the gate on an overrun."""
        done = self.repo(budget="permanent_characters = 10\n")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("meow-demo: loads 55 characters on every turn, 45 over its budget of 10", done.stdout)

    def test_a_unit_with_no_budget_fails(self):
        """REQ-1074: every unit states the budget it is held to."""
        done = self.repo(budget=None)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("meow-demo: states no budget in budget.toml", done.stdout)

    def test_a_description_and_when_to_use_over_the_cap_fail(self):
        """REQ-1072: the platform caps a description and its when_to_use together."""
        done = self.repo(budget="permanent_characters = 5000\n", description="x" * 1000, when="y" * 600)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("description is 1601 characters, over the cap of 1536", done.stdout)

if __name__ == "__main__":
    unittest.main()
