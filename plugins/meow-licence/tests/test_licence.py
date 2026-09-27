# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every failure path SPC-1120 states for `meow-licence check`.

Each fixture builds a scratch git repository and runs the check in it.
`MEOW_LICENCE_BIN` names the launcher to test, so the same fixtures can first
run against a program that reports nothing and be seen failing (REQ-2072).
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_LICENCE_BIN", UNIT / "bin" / "meow-licence"))
HEADER = "# SPDX-FileCopyrightText: 2026 A Person <a@example.org>\n# SPDX-License-Identifier: MIT\n"
REUSE = '''version = 1

[[annotations]]
path = ["docs/**"]
SPDX-FileCopyrightText = "2026 A Person <a@example.org>"
SPDX-License-Identifier = "MIT"
'''


class Repository:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=env)
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=env)

    def check(self):
        return subprocess.run([str(BIN), "check"], cwd=self.root, capture_output=True, text=True)


class Check(unittest.TestCase):
    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_covered_repository_passes(self):
        done = self.repo({"REUSE.toml": REUSE, "docs/guide.md": "# Guide\n", "run.sh": HEADER + "echo hi\n",
                          "LICENSE": "MIT License\n"}).check()
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("0 licensing findings", done.stdout)

    def test_a_file_nothing_covers_fails(self):
        """REQ-3058: every file the project owns is covered by a declaration."""
        done = self.repo({"REUSE.toml": REUSE, "run.sh": "echo hi\n"}).check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("run.sh: no licensing declaration covers it", done.stdout)

    def test_a_header_missing_its_identifier_fails(self):
        """REQ-1022: a declaration carries both the copyright and the licence identifier."""
        done = self.repo({"run.sh": "# SPDX-FileCopyrightText: 2026 A Person <a@example.org>\necho hi\n",
                          "ok.sh": HEADER}).check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("run.sh: the header names a copyright and no licence identifier", done.stdout)

    def test_an_annotation_missing_its_copyright_fails(self):
        """REQ-1022: an annotation carries both halves too."""
        done = self.repo({"REUSE.toml": 'version = 1\n\n[[annotations]]\npath = "docs/**"\nSPDX-License-Identifier = "MIT"\n',
                          "docs/guide.md": "# Guide\n"}).check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("REUSE.toml: an annotation names a licence and no copyright", done.stdout)

    def test_an_unused_licence_text_fails(self):
        """REQ-3062: the licence directory holds only licences in use."""
        done = self.repo({"run.sh": HEADER, "LICENSES/MIT.txt": "MIT\n", "LICENSES/GPL-3.0-only.txt": "GPL\n"}).check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("LICENSES/GPL-3.0-only.txt: no declaration uses GPL-3.0-only", done.stdout)

    def test_a_licence_in_use_without_its_text_fails(self):
        """REQ-3062: an identifier in use has its text, where the directory is kept."""
        done = self.repo({"run.sh": HEADER, "LICENSES/Apache-2.0.txt": "Apache\n",
                          "other.sh": HEADER.replace("MIT", "Apache-2.0")}).check()
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("LICENSES/: MIT is in use and has no text", done.stdout)

    def test_a_repository_declaring_nothing_is_undeclared(self):
        """REQ-3066: an undeclared repository is reported as undeclared, never as covered."""
        done = self.repo({"run.sh": "echo hi\n"}).check()
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("licensing is undeclared", done.stdout)

    def test_the_report_names_no_author(self):
        """REQ-3064: the check reports licensing alone, never authorship."""
        done = self.repo({"run.sh": HEADER, "bare.sh": "echo hi\n"}).check()
        self.assertNotIn("A Person", done.stdout)
        self.assertNotIn("a@example.org", done.stdout)

    def test_outside_a_repository_it_is_unchecked(self):
        with tempfile.TemporaryDirectory() as empty:
            done = subprocess.run([str(BIN), "check"], cwd=empty, capture_output=True, text=True,
                                  env={**os.environ, "GIT_CEILING_DIRECTORIES": str(Path(empty).parent)})
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("unchecked", done.stdout)


if __name__ == "__main__":
    unittest.main()
