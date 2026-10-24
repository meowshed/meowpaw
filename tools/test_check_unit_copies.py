# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit's description and its package page agree with the unit's (TSK-5683, REQ-3196, REQ-4622)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_unit_copies as copies  # noqa: E402

DESCRIPTION = "Does a thing for Claude Code, writing no file."
PAGE = """---
reader: someone
answers: what it does
kind: reference
describes: [meow-demo@0.1.0]
description: "Does a thing for Claude Code, writing no file."
---

# meow-demo

Intro.

## Install it

Install the plugin.

## Bind your stages

Bind them.

## Hooks

<!-- host-specific: claude -->

Claude Code runs a hook.
"""
PACKAGE_PAGE = """---
reader: someone
answers: what it does
kind: reference
describes: [@meowshed/meow-demo@0.1.0]
---

# @meowshed/meow-demo

Does a thing for Pi, writing no file. Distributed as a Pi package.

## Install it

Install the package.

## Bind your stages

Bind them.
"""
PI_DESCRIPTION = "Does a thing for Pi, writing no file. Distributed as a Pi package."


def fixture():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    plugin = root / "plugins" / "meow-demo"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "meow-demo", "description": DESCRIPTION}))
    (plugin / "README.md").write_text(PAGE)
    package = root / "packages" / "meow-demo"
    package.mkdir(parents=True)
    (package / "package.json").write_text(json.dumps({"name": "@meowshed/meow-demo", "description": PI_DESCRIPTION}))
    (package / "README.md").write_text(PACKAGE_PAGE)
    return tmp, root


class Copies(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = fixture()
        self.addCleanup(self.tmp.cleanup)

    def test_agreeing_copies_pass(self):
        """TSK-5683 criteria 2 and 3: a unit whose copies agree and whose host-specific section is marked passes."""
        self.assertEqual([], copies.check(self.root))

    def test_a_description_that_differs_in_each_copy_is_named(self):
        """TSK-5683 criterion 2, REQ-3196: each copy is named when it alone is edited."""
        cases = {
            "plugins/meow-demo/README.md": PAGE.replace("writing no file", "writing a file", 1),
            "packages/meow-demo/package.json": json.dumps({"description": "Other."}),
            "packages/meow-demo/README.md": PACKAGE_PAGE.replace("a thing", "another thing"),
        }
        for named, text in cases.items():
            with self.subTest(copy=named):
                tmp, root = fixture()
                self.addCleanup(tmp.cleanup)
                (root / named).write_text(text)
                found = copies.check(root)
                self.assertTrue(any(line.startswith(named) and "REQ-3196" in line for line in found), found)

    def test_an_edited_manifest_is_named_through_the_copies_it_leaves_behind(self):
        """TSK-5683 criterion 2, REQ-3196: the manifest is the source, so the three copies that no longer match it are named."""
        (self.root / "plugins/meow-demo/.claude-plugin/plugin.json").write_text(json.dumps({"description": "Changed."}))
        found = copies.check(self.root)
        self.assertEqual(3, len(found), found)

    def test_a_package_page_that_lacks_a_section_is_named(self):
        """TSK-5683 criterion 3, REQ-4622: a package page with a section removed fails naming it."""
        (self.root / "packages/meow-demo/README.md").write_text(PACKAGE_PAGE.replace("## Bind your stages\n\nBind them.\n", ""))
        found = copies.check(self.root)
        self.assertEqual(1, len(found), found)
        self.assertIn("Bind your stages", found[0])
        self.assertIn("REQ-4622", found[0])

    def test_a_section_marked_host_specific_may_be_absent(self):
        """TSK-5683 criterion 3, REQ-4622: the Hooks section is marked, so its absence is no finding, and unmarked it is."""
        self.assertEqual([], copies.check(self.root))
        (self.root / "plugins/meow-demo/README.md").write_text(PAGE.replace("<!-- host-specific: claude -->\n\n", ""))
        found = copies.check(self.root)
        self.assertEqual(1, len(found), found)
        self.assertIn("Hooks", found[0])

    def test_a_heading_with_the_host_substitutions_matches(self):
        """TSK-5683 criterion 3, REQ-4622: 'Have Claude Code ...' on the unit page matches 'Have Pi ...' on the package page."""
        (self.root / "plugins/meow-demo/README.md").write_text(PAGE + "\n## Have Claude Code do it\n\nText.\n")
        self.assertEqual(1, len(copies.check(self.root)))
        (self.root / "packages/meow-demo/README.md").write_text(PACKAGE_PAGE + "\n## Have Pi do it\n\nText.\n")
        self.assertEqual([], copies.check(self.root))

    def test_a_run_over_no_unit_fails(self):
        """TSK-5683, REQ-3196: a check that read nothing is no pass."""
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(1, len(copies.check(Path(empty))))

    def test_the_repository_agrees(self):
        """TSK-5683 criteria 2 and 3, REQ-3196, REQ-4622: every unit of this repository passes."""
        self.assertEqual([], copies.check())


if __name__ == "__main__":
    unittest.main()
