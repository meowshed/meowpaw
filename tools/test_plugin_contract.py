# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the parts of SPC-1080's "Each unit is a plugin" the tree
already holds: the install through the platform (REQ-1480), the major
version (REQ-2994), the install root nothing writes at run time (REQ-3000,
REQ-1484), the one configuration format (REQ-1494) and the secrets rule
(REQ-1488)."""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_SUFFIXES = (".toml",)
EXEMPT = (".claude-plugin", "hooks")


def units():
    return sorted(p for p in (ROOT / "plugins").iterdir() if p.is_dir())


class Versions(unittest.TestCase):
    def test_every_version_is_major_zero(self):
        """REQ-2994: every version's major number stays zero while the public interface still moves."""
        for manifest in sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
            major = int(json.loads(manifest.read_text(encoding="utf-8"))["version"].split(".")[0])
            self.assertEqual(major, 0, f"{manifest.parent.parent.name} is at major {major}")


class InstallRoot(unittest.TestCase):
    def test_no_fixture_writes_under_its_unit(self):
        """REQ-3000, REQ-1484: a unit's fixtures run against a read-only copy of the unit and write nothing there."""
        for unit in units():
            tests = unit / "tests"
            if not tests.is_dir():
                continue
            with tempfile.TemporaryDirectory() as tmp:
                copy = Path(tmp) / unit.name
                shutil.copytree(unit, copy)
                for path in copy.rglob("*"):
                    if path.is_file() or path.is_symlink():
                        path.chmod(stat.S_IRUSR | stat.S_IXUSR)
                    if path.is_dir():
                        path.chmod(stat.S_IXUSR | stat.S_IRUSR)
                copy.chmod(stat.S_IXUSR | stat.S_IRUSR)
                env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}
                done = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", str(copy / "tests")],
                    capture_output=True, text=True, env=env, cwd=tmp,
                )
                self.assertNotIn("PermissionError", done.stderr,
                                 f"{unit.name}'s fixtures write under the unit's own directory:\n{done.stderr}")


class Configuration(unittest.TestCase):
    def test_every_configuration_file_is_toml(self):
        """REQ-1494: a file of configuration the harness owns is TOML, apart from the platform's JSON manifests and hooks and the record's YAML front matter."""
        for unit in units():
            for path in unit.rglob("*"):
                if not path.is_file() or "bin" in path.relative_to(unit).parts:
                    continue
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                name = path.name
                if name in ("hooks.json", "plugin.json", "settings.json"):
                    continue
                if path.suffix in (".md", ".py", ".sh", ".json", ".txt", ".html", ".yml", ".yaml", ".svg", ".png", ".zip"):
                    continue
                if path.suffix == ".toml":
                    continue
                text = path.read_text(encoding="utf-8")
                # A program starts with a shebang, and a record document's
                # front matter is YAML the platform reads; every other file a
                # unit ships as configuration is TOML.
                if text.startswith("#!"):
                    continue
                self.assertTrue(
                    text.lstrip().startswith("---") or name in ("LICENSE", "LICENCE"),
                    f"{path} ships configuration in no format the harness declares (REQ-1494)",
                )


class PinnedSuites(unittest.TestCase):
    EXEMPT = {
        # Their subject is how a launcher finds its binary, so the preference
        # itself is what they measure.
        "tools/test_launchers.py",
        "tools/test_shared_binary.py",
        "plugins/meow-unattended/tests/test_posture.py",
        # It never executes a launcher; the paths it holds are fixture text.
        "tools/test_check_standalone.py",
    }

    def test_every_launcher_running_suite_pins_the_data_directory(self):
        """REQ-2928: a suite that runs a launcher pins the launcher's data directory, so it measures the checkout's build."""
        for path in sorted((ROOT / "plugins").glob("*/tests/test_*.py")) + sorted((ROOT / "tools").glob("test_*.py")):
            rel = str(path.relative_to(ROOT))
            text = path.read_text(encoding="utf-8")
            if "subprocess" not in text or not re.search(r"bin/meow-|bin/paw|MEOW_[A-Z]+_BIN", text):
                continue
            if rel in self.EXEMPT:
                continue
            self.assertIn("CLAUDE_PLUGIN_DATA", text, f"{rel} runs a launcher and pins no data directory (REQ-2928)")


class Secrets(unittest.TestCase):
    def test_no_shipped_file_holds_a_home_path_or_a_credential(self):
        """REQ-1488: machine-specific or secret configuration lives in the user's own settings, never in a unit's files."""
        import re

        home = re.compile(r"(?<![\w$])(/Users/\w+|/home/\w+|C:\\Users\\\w+)")
        credential = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})")
        for unit in units():
            for path in unit.rglob("*"):
                if not path.is_file() or "bin" in path.relative_to(unit).parts:
                    continue
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                if path.suffix in (".png", ".zip"):
                    continue
                raw = path.read_bytes()
                if b"\x00" in raw[:8192]:
                    continue
                text = raw.decode("utf-8", errors="replace")
                for found in credential.finditer(text):
                    self.fail(f"{path} holds what reads as a credential: {found.group(0)[:8]}...")
                for found in home.finditer(text):
                    self.fail(f"{path} holds the absolute home path {found.group(0)} (REQ-1488)")


if __name__ == "__main__":
    unittest.main()
