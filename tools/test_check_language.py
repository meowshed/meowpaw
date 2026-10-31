# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the language check: the method names no language (TSK-5015, ADR-2640)."""

import io
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_language  # noqa: E402

READ = ("meow-method",)
PACKS = ("meow-rust",)


class Language(unittest.TestCase):
    def tree(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name in ("meow-method", "meow-rust"):
            (root / "plugins" / name).mkdir(parents=True)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def run_check(self, root):
        out = io.StringIO()
        with redirect_stdout(out):
            status = check_language.main(root, READ, PACKS)
        return status, out.getvalue()

    def test_a_method_skill_naming_a_language_fails_with_file_line_and_word(self):
        """Criterion 1, REQ-0070: the check prints the file, the line and the word, and exits 1."""
        root = self.tree({"plugins/meow-method/skills/x/SKILL.md": "Run the tests.\nUse Rust for the build.\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 1, said)
        self.assertIn("plugins/meow-method/skills/x/SKILL.md:2: names Rust", said)

    def test_a_framework_a_package_manager_and_an_extension_fail(self):
        """Criterion 1, REQ-0070: every kind of name on the list is caught."""
        root = self.tree({"plugins/meow-method/README.md": "Install with npm.\nEdit `main.py` now.\nA Django view.\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 1, said)
        for word in ("npm", ".py", "Django"):
            self.assertIn(f"names {word}", said)

    def test_a_pack_readme_naming_the_language_is_not_read(self):
        """Criterion 2, REQ-0072: a pack exists to know a language."""
        root = self.tree({"plugins/meow-method/README.md": "Nothing here.\n",
                          "plugins/meow-rust/README.md": "Rust and cargo.\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 0, said)
        self.assertIn("1 method files read, 0 findings", said)

    def test_a_fence_naming_the_pack_whose_output_it_shows_is_exempt(self):
        """Criterion 2, REQ-0084: only the fence's lines are exempt, and the prose after it is read again."""
        page = "Output:\n\n```text meow-rust\ncargo test\n```\n\nThen cargo again.\n"
        root = self.tree({"plugins/meow-method/skills/x/SKILL.md": page})
        status, said = self.run_check(root)
        self.assertEqual(status, 1, said)
        self.assertIn("SKILL.md:7: names cargo", said)
        self.assertNotIn("SKILL.md:4", said)

    def test_a_fence_naming_no_pack_is_read(self):
        """REQ-0070: an info string that names no pack buys no exemption."""
        root = self.tree({"plugins/meow-method/skills/x/SKILL.md": "```bash\ncargo test\n```\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 1, said)
        self.assertIn("SKILL.md:2: names cargo", said)

    def test_a_units_program_is_not_read(self):
        """ADR-1070: the program a unit ships may be written in any language."""
        root = self.tree({"plugins/meow-method/README.md": "Fine.\n",
                          "plugins/meow-method/bin/tool.py": "import cargo\n",
                          "plugins/meow-method/tests/test_x.py": "rust\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 0, said)

    def test_a_unit_in_neither_list_fails(self):
        """REQ-0070: a new unit cannot escape the check by joining no list."""
        root = self.tree({"plugins/meow-method/README.md": "Fine.\n", "plugins/meow-new/README.md": "x\n"})
        status, said = self.run_check(root)
        self.assertEqual(status, 1, said)
        self.assertIn("plugins/meow-new: in neither READ nor PACKS", said)

    def test_a_run_that_reads_no_file_fails(self):
        """A check over nothing is no pass."""
        status, said = self.run_check(self.tree({}))
        self.assertEqual(status, 1, said)

    def test_this_repository_passes_and_reads_files(self):
        """Criterion 3: the repository's own method names no language, and the run read files."""
        out = io.StringIO()
        with redirect_stdout(out):
            status = check_language.main()
        self.assertEqual(status, 0, out.getvalue())
        self.assertNotRegex(out.getvalue(), r"(?m)^0 method files read")

    def test_the_lists_agree_with_each_unit_s_declared_layer(self):
        """REQ-0072: a unit is a pack exactly where its requires.toml says layer = "pack"."""
        for unit in sorted(p for p in (check_language.ROOT / "plugins").iterdir() if p.is_dir()):
            layer = re.search(r'^layer *= *"(\w+)"', (unit / "requires.toml").read_text(encoding="utf-8"), re.M)
            self.assertIsNotNone(layer, unit.name)
            self.assertEqual(unit.name in check_language.PACKS, layer.group(1) == "pack", unit.name)
            self.assertEqual(unit.name in check_language.READ, layer.group(1) != "pack", unit.name)


if __name__ == "__main__":
    unittest.main()
