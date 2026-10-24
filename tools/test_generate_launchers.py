# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""A unit's launcher and Pi extension equal what its generator writes (TSK-5683, REQ-4624)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_launchers as gen  # noqa: E402

ROOT = gen.ROOT


class Generated(unittest.TestCase):
    def scratch(self):
        """A scratch root holding what the generator writes."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for path, text in gen.expected(root).items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def test_committed_files_equal_the_generator(self):
        """TSK-5683 criterion 1, REQ-4624: no committed launcher or extension differs from what is written."""
        self.assertEqual([], [str(p.relative_to(ROOT)) for p in gen.differing()])

    def test_an_edited_launcher_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: the check names the unit whose launcher was edited and no other."""
        root = self.scratch()
        edited = root / "plugins" / "meow-go" / "bin" / "meow-go"
        edited.write_text(edited.read_text(encoding="utf-8") + "# hand-written\n", encoding="utf-8")
        self.assertEqual([edited], gen.differing(root))

    def test_an_edited_extension_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: the check names a Pi extension that was edited."""
        root = self.scratch()
        edited = root / "packages" / "meow-lua" / "extensions" / "bin.ts"
        edited.write_text("// edited\n", encoding="utf-8")
        self.assertEqual([edited], gen.differing(root))

    def test_a_missing_file_is_named(self):
        """TSK-5683 criterion 1, REQ-4624: a launcher that was deleted differs."""
        root = self.scratch()
        gone = root / "packages" / "meow-scm" / "bin" / "meow-scm"
        gone.unlink()
        self.assertEqual([gone], gen.differing(root))

    def test_every_launcher_and_launcher_only_extension_is_declared(self):
        """TSK-5683 criterion 1, REQ-4624: a hand-written launcher no fact table declares cannot hide."""
        written = set(gen.expected())
        found = set()
        for tree in ("plugins", "packages"):
            for launcher in (ROOT / tree).glob("*/bin/*"):
                if launcher.is_file():
                    found.add(launcher)
        found |= set((ROOT / "packages").glob("*/extensions/bin.ts"))
        self.assertEqual([], sorted(str(p.relative_to(ROOT)) for p in found - written))

    def test_the_launcher_of_one_unit_is_unchanged_by_the_template(self):
        """TSK-5683 criterion 4, REQ-4624: the generated launcher of meow-go keeps the guard a missing binary hits."""
        text = gen.expected()[ROOT / "plugins" / "meow-go" / "bin" / "meow-go"]
        self.assertIn('exec "$binary" go "$@"', text)
        self.assertIn("status | bind | check | toolchain)", text)


if __name__ == "__main__":
    unittest.main()
