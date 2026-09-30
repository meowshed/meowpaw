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
INDEX = """Start here.

<!-- check_docs index -->
<!-- /check_docs index -->

## Planned

- a second demo.

## Not written

- `tutorial`: the demo has one step.
- `how-to`: the page carries it.
- `explanation`: nothing to explain.
- `troubleshooting`: nothing fails.
"""
ROUTE = """# demo

> A demo harness.

## Documentation

- [Introduction](docs/README.md): where to start
"""
PAGE = "---\nreader: someone running {unit}\nanswers: what {unit} does\nkind: reference\ndescribes: [{unit}@{version}]\n---\n\n# {unit}\n\n{body}\n"


class Tree:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.unit("meow-demo", "1.0.0")
        (self.root / "docs").mkdir()
        self.write("docs/README.md", PAGE.format(unit="meow-demo", version="1.0.0", body=INDEX).replace("kind: reference", "kind: introduction"))
        self.write("llms.txt", ROUTE)
        self.index()

    def index(self):
        subprocess.run([sys.executable, str(CHECK), "--root", str(self.root), "--write"], capture_output=True, text=True)

    def unit(self, name, version, page=True, body="It runs the demo."):
        manifest = self.root / "plugins" / name / ".claude-plugin" / "plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps(self.manifest(name, version)), encoding="utf-8")
        (manifest.parent.parent / "budget.toml").write_text("permanent_characters = 1200\n", encoding="utf-8")
        if page:
            self.write(f"plugins/{name}/README.md", PAGE.format(unit=name, version=version, body=body))

    @staticmethod
    def manifest(name, version, **changes):
        data = {"name": name, "version": version,
                "description": "Runs the demo. It keeps up to 1,200 characters in context on every turn.",
                "homepage": f"https://example.org/blob/main/plugins/{name}/README.md",
                "repository": "https://example.org", "license": "Apache-2.0", "keywords": ["demo"]}
        data.update(changes)
        return {key: value for key, value in data.items() if value is not None}

    def change_manifest(self, name, **changes):
        manifest = self.root / "plugins" / name / ".claude-plugin" / "plugin.json"
        data = {**json.loads(manifest.read_text(encoding="utf-8")), **changes}
        manifest.write_text(json.dumps({key: value for key, value in data.items() if value is not None}), encoding="utf-8")

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
        tree.change_manifest("meow-demo", version="1.1.0")
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

    def test_a_manifest_without_its_licence_fails(self):
        """REQ-3162: an entry carries every field the platform shows before an install."""
        tree = self.tree()
        tree.change_manifest("meow-demo", license=None)
        self.assertFails(tree, "meow-demo: plugin.json lacks license")

    def test_a_homepage_outside_the_unit_fails(self):
        """REQ-3160: the entry links to the unit's own page."""
        tree = self.tree()
        tree.change_manifest("meow-demo", homepage="https://example.org/blob/main/docs/meow-demo.md")
        self.assertFails(tree, "meow-demo: homepage doesn't point at plugins/meow-demo/README.md")

    def test_a_description_without_the_ceiling_fails(self):
        """REQ-3164: the description says what keeping the unit installed costs."""
        tree = self.tree()
        tree.change_manifest("meow-demo", description="Runs the demo.")
        self.assertFails(tree, "meow-demo: the description doesn't name its ceiling, 1,200 characters")

    def test_a_page_missing_from_the_index_fails(self):
        """REQ-3154: the index says what every page answers and who it is for."""
        tree = self.tree()
        tree.write("docs/usage.md", PAGE.format(unit="meow-demo", version="1.0.0", body="Use it.").replace("kind: reference", "kind: how-to"))
        self.assertFails(tree, "docs/README.md: the table is out of date; run --write")

    def test_a_kind_neither_carried_nor_recorded_fails(self):
        """REQ-3140: a kind the project doesn't carry is recorded as absent with its reason."""
        tree = self.tree()
        index = tree.root / "docs/README.md"
        index.write_text(index.read_text(encoding="utf-8").replace("- `explanation`: nothing to explain.\n", ""), encoding="utf-8")
        self.assertFails(tree, "docs/README.md: no page is explanation, and Not written doesn't list it")

    def test_an_index_without_its_planned_section_fails(self):
        """REQ-3134: the index says which parts are planned and unbuilt."""
        tree = self.tree()
        index = tree.root / "docs/README.md"
        index.write_text(index.read_text(encoding="utf-8").replace("## Planned\n\n- a second demo.\n\n", ""), encoding="utf-8")
        self.assertFails(tree, "docs/README.md: has no Planned section")

    def test_a_route_link_to_a_missing_file_fails(self):
        """REQ-3144: the route file links the documentation, and a link resolves."""
        tree = self.tree()
        tree.write("llms.txt", ROUTE + "- [Gone](docs/gone.md)\n")
        self.assertFails(tree, "llms.txt:8: links to docs/gone.md, which doesn't exist")

    def test_a_route_file_without_its_heading_fails(self):
        """REQ-3144: the route file follows the published format, H1 first."""
        tree = self.tree()
        tree.write("llms.txt", ROUTE.replace("# demo\n\n", ""))
        self.assertFails(tree, "llms.txt: lacks its H1")

    def test_prose_in_the_route_file_fails(self):
        """REQ-3146: the route file links material and restates none of it."""
        tree = self.tree()
        tree.write("llms.txt", ROUTE + "\nThe demo runs checks and reports them.\n")
        self.assertFails(tree, "llms.txt:9: neither a heading, the summary nor a link")

    SKILL = ("---\nname: method\ndescription: The method's steps.\n---\n\n<steps name=\"run a step\">\n"
             "1. Name the step. The steps, in order, are\n   research, requirements, design, spec, epic, implement and"
             " review. The route\n   skill runs first.\n</steps>\n")

    def with_method(self, tree):
        tree.write("plugins/meow-demo/skills/method/SKILL.md", self.SKILL)

    def test_a_page_stating_the_wrong_step_count_fails(self):
        """TSK-3840 criterion 1, REQ-3632: a page saying ten steps while the method names seven fails, by page and line."""
        tree = self.tree()
        self.with_method(tree)
        tree.write("README.md", "# Demo\n\nEvery change moves through\nthe same ten steps, in order.\n")
        self.assertFails(tree, "README.md:4: states ten steps, and the method names seven")

    def test_a_page_stating_the_methods_step_count_passes(self):
        """REQ-3632: the right count passes, in words or digits, and so does a count of something else."""
        tree = self.tree()
        self.with_method(tree)
        tree.write("README.md", "# Demo\n\nAll move through the same seven steps. The method's 7 steps. Install it in"
                   " three steps.\nEach tutorial follows the same three steps. Adding a pack costs two steps.\n"
                   "The old text said `the method's ten steps`. <!-- the method's ten steps -->\n")
        done = tree.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_wrong_count_is_reported_once_at_the_line_of_the_number(self):
        """REQ-3632: one statement matching two forms is one failure, named at the line the number is on."""
        tree = self.tree()
        self.with_method(tree)
        tree.write("README.md", "It runs the method: ten steps from research to review.\n\nThe method's\nten\nsteps.\n")
        done = tree.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertEqual(done.stdout.count("states ten steps"), 2, done.stdout)
        self.assertIn("README.md:1: states ten steps, and the method names seven", done.stdout)
        self.assertIn("README.md:4: states ten steps, and the method names seven", done.stdout)

    def test_each_written_form_of_a_wrong_count_is_caught(self):
        """REQ-3632: digits, emphasis, a quoted block, a curly apostrophe and a count above twelve are all read."""
        for text in ("through the same 10 steps", "the method's **ten** steps", "> the method\n> has ten steps",
                     "the method\u2019s ten steps", "through the same thirteen steps", "the ten-step chain",
                     "a harness that demands ten steps"):
            with self.subTest(text=text):
                tree = self.tree()
                self.with_method(tree)
                tree.write("README.md", f"# Demo\n\n{text}\n")
                done = tree.check()
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("and the method names seven", done.stdout)

    def test_a_skill_with_no_readable_step_list_fails(self):
        """REQ-3632: a method skill whose list can't be read is a failure, never a count that agreed."""
        for change, said in ((("The steps, in order, are", "The chain is"), "names no step list"),
                             (("design, spec", "design and spec"), 'names the step "design and spec"')):
            with self.subTest(said=said):
                tree = self.tree()
                tree.write("plugins/meow-demo/skills/method/SKILL.md", self.SKILL.replace(*change))
                self.assertFails(tree, f"plugins/meow-demo/skills/method/SKILL.md: {said}")

    def test_a_rewrapped_step_list_is_still_read(self):
        """REQ-3632: the list is read however the sentence wraps, and with a colon after it."""
        tree = self.tree()
        tree.write("plugins/meow-demo/skills/method/SKILL.md",
                   self.SKILL.replace("The steps, in order, are\n   research", "The steps, in\n   order, are: research"))
        tree.write("README.md", "through the same ten steps\n")
        self.assertFails(tree, "README.md:1: states ten steps, and the method names seven")

    def test_a_page_that_is_not_utf8_is_a_failure_and_no_crash(self):
        """REQ-3632: a file that can't be read is named, and the check goes on."""
        tree = self.tree()
        self.with_method(tree)
        (tree.root / "CLAUDE.md").write_bytes(b"caf\xe9 the method's ten steps")
        self.assertFails(tree, "CLAUDE.md: isn't UTF-8")

    def test_the_step_count_is_read_from_the_skill(self):
        """REQ-3632: the count comes from the method skill, so a skill naming six makes seven the wrong count."""
        tree = self.tree()
        tree.write("plugins/meow-demo/skills/method/SKILL.md", self.SKILL.replace("epic, implement and", "implement and"))
        tree.write("CLAUDE.md", "A method costing seven steps for a typo.\n")
        tree.write("README.md", "through the same six steps\n")
        self.assertFails(tree, "CLAUDE.md:1: states seven steps, and the method names six")

    def test_a_unit_page_and_the_route_are_checked_for_the_count(self):
        """REQ-3632: unit pages, pages under docs and the route file are read, and fenced text is not."""
        tree = self.tree()
        self.with_method(tree)
        tree.write("llms.txt", ROUTE + "- [Demo](plugins/meow-demo/README.md): runs the method's nine steps\n")
        tree.write("project/vision.md", "# Vision\n\n```text\nNine steps run in a chain\n```\n\nTen steps run in a chain.\n")
        page = (tree.root / "plugins/meow-demo/README.md").read_text(encoding="utf-8")
        tree.write("plugins/meow-demo/README.md", page + "\nIt runs the method's eight steps.\n")
        tree.write("docs/guide.md", PAGE.format(unit="meow-demo", version="1.0.0", body="The method has six steps."))
        tree.index()
        done = tree.check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertRegex(done.stdout, r"llms\.txt:\d+: states nine steps, and the method names seven")
        self.assertRegex(done.stdout, r"plugins/meow-demo/README\.md:\d+: states eight steps, and the method names seven")
        self.assertRegex(done.stdout, r"docs/guide\.md:\d+: states six steps, and the method names seven")
        self.assertIn("project/vision.md:7: states ten steps, and the method names seven", done.stdout)
        self.assertNotIn("project/vision.md:4", done.stdout)

    def test_no_method_skill_means_no_count_to_hold(self):
        """REQ-3632: a repository shipping no method skill has no count, so nothing is reported."""
        tree = self.tree()
        tree.write("README.md", "through the same ten steps.\n")
        done = tree.check()
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_an_identifier_in_code_is_an_example(self):
        """REQ-3130: a unit that reads the record shows its syntax in code, which isn't a citation."""
        tree = self.tree()
        tree.write("docs/usage.md", PAGE.format(unit="meow-demo", version="1.0.0", body="Run `paw show REQ-0010`.\n\n```text\nTSK-0001 done\n```"))
        tree.index()
        done = tree.check()
        self.assertEqual(done.returncode, 0, done.stdout)


if __name__ == "__main__":
    unittest.main()
