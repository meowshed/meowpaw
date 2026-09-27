# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for `check_docs.py`, one scratch tree per failure path SPC-1110 states.

`CHECK_DOCS` names the program to test, so the fixtures can first run against
one that reports nothing and be seen failing (REQ-2072).
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = Path(os.environ.get("CHECK_DOCS", Path(__file__).resolve().parent / "check_docs.py"))
PAGE = "---\nreader: someone running {unit}\nanswers: what {unit} does\nkind: reference\ndescribes: [{unit}@{version}]\n---\n\n# {unit}\n\n{body}\n"


class Tree:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.unit("meow-demo", "1.0.0")
        (self.root / "docs").mkdir()
        self.write("docs/README.md", PAGE.format(unit="meow-demo", version="1.0.0", body="Start here.").replace("kind: reference", "kind: introduction"))

    def unit(self, name, version, page=True, body="It runs the demo."):
        manifest = self.root / "plugins" / name / ".claude-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"name": name, "version": version}), encoding="utf-8")
        if page:
            self.write(f"plugins/{name}/README.md", PAGE.format(unit=name, version=version, body=body))

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self):
        return subprocess.run([sys.executable, str(CHECK), "--root", str(self.root)],
                              capture_output=True, text=True)


class CheckDocs(unittest.TestCase):
    def tree(self):
        tree = Tree()
        self.addCleanup(tree.tmp.cleanup)
        return tree

    def assertFails(self, tree, expected):
        done = tree.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(expected, done.stdout)

    def test_a_clean_tree_passes(self):
        done = self.tree().check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_unit_without_a_page_fails(self):
        """REQ-3136 and REQ-3138: every unit ships a page of its own inside itself."""
        tree = self.tree()
        tree.unit("meow-bare", "0.1.0", page=False)
        self.assertFails(tree, "meow-bare: has no README.md")

    def test_a_page_without_its_reader_fails(self):
        """REQ-3142: every page names the reader it is written for."""
        tree = self.tree()
        page = tree.root / "plugins/meow-demo/README.md"
        page.write_text(page.read_text(encoding="utf-8").replace("reader: someone running meow-demo\n", ""), encoding="utf-8")
        self.assertFails(tree, "plugins/meow-demo/README.md: front matter lacks reader")

    def test_a_page_describing_an_older_version_fails(self):
        """REQ-2838 and REQ-3152: a version bump fails until the page is restamped."""
        tree = self.tree()
        manifest = tree.root / "plugins/meow-demo/.claude-plugin/plugin.json"
        manifest.write_text(json.dumps({"name": "meow-demo", "version": "1.1.0"}), encoding="utf-8")
        self.assertFails(tree, "plugins/meow-demo/README.md: describes meow-demo@1.0.0, the unit is at 1.1.0")

    def test_a_page_citing_a_record_identifier_fails(self):
        """REQ-3130: a user-facing page carries no record identifier."""
        tree = self.tree()
        tree.write("docs/guide.md", PAGE.format(unit="meow-demo", version="1.0.0", body="REQ-0010 says so."))
        self.assertFails(tree, "docs/guide.md:10: cites the record: REQ-0010")

    def test_a_page_carrying_a_record_status_fails(self):
        """REQ-3130: a user-facing page carries no record status."""
        tree = self.tree()
        page = tree.root / "docs/README.md"
        page.write_text(page.read_text(encoding="utf-8").replace("---\nreader", "---\nstatus: draft\nreader", 1), encoding="utf-8")
        self.assertFails(tree, "docs/README.md: front matter carries the record's status")

    def test_a_page_linking_into_the_record_fails(self):
        """REQ-3148: a page never sends its reader into the record for an explanation."""
        tree = self.tree()
        tree.write("project/vision.md", "# Vision\n")
        tree.write("docs/why.md", PAGE.format(unit="meow-demo", version="1.0.0", body="See [the vision](../project/vision.md).").replace("kind: reference", "kind: explanation"))
        self.assertFails(tree, "docs/why.md:10: cites the record: ../project/vision.md")

    def test_a_wrapped_describes_list_is_read_whole(self):
        """REQ-2838: a formatter wrapping the list onto several lines changes nothing."""
        tree = self.tree()
        page = tree.root / "docs/README.md"
        page.write_text(page.read_text(encoding="utf-8").replace("describes: [meow-demo@1.0.0]", "describes:\n  [\n    meow-demo@0.9.0,\n  ]"), encoding="utf-8")
        self.assertFails(tree, "docs/README.md: describes meow-demo@0.9.0, the unit is at 1.0.0")

    def test_an_identifier_in_code_is_an_example(self):
        """REQ-3130: a unit that reads the record shows its syntax in code, which isn't a citation."""
        tree = self.tree()
        tree.write("docs/usage.md", PAGE.format(unit="meow-demo", version="1.0.0", body="Run `paw show REQ-0010`.\n\n```text\nTSK-0001 done\n```"))
        done = tree.check()
        self.assertEqual(done.returncode, 0, done.stdout)


if __name__ == "__main__":
    unittest.main()
