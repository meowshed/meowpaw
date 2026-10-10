# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Checks that the marketplace ships no unit the chain no longer uses, as
TSK-3870 asks for `meow-method` and TSK-4070 for the `meow-verbs` stub
(REQ-3654, ADR-2300, ADR-2360)."""

import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETIRED = ("meow-method",)


class RetiredUnits(unittest.TestCase):
    def test_the_marketplace_lists_no_retired_unit(self):
        """TSK-3870 criterion 1: `.claude-plugin/marketplace.json` has no entry for a retired unit."""
        listed = {p["name"] for p in json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"]}
        for unit in RETIRED:
            self.assertNotIn(unit, listed)

    def test_no_retired_unit_is_in_the_tree(self):
        """TSK-3870 criterion 2: `plugins/<unit>` doesn't exist for a retired unit."""
        for unit in RETIRED:
            self.assertFalse((ROOT / "plugins" / unit).exists(), unit)

    def test_the_test_verb_runs_no_retired_unit(self):
        """TSK-3870 criterion 3: the profile's `test` verb names no retired unit's tests."""
        with open(ROOT / ".meowpaw/profile.toml", "rb") as handle:
            test = tomllib.load(handle)["stages"]["test"]
        for unit in RETIRED:
            self.assertNotIn(f"plugins/{unit}", test)


class RemovedStub(unittest.TestCase):
    """TSK-4070, ADR-2360: the `meow-verbs` stub left the marketplace after its one release (REQ-3004, REQ-3654)."""

    def test_the_marketplace_lists_no_meow_verbs(self):
        """Criterion 1: `.claude-plugin/marketplace.json` has no `meow-verbs` entry."""
        listed = {p["name"] for p in json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"]}
        self.assertNotIn("meow-verbs", listed)

    def test_git_tracks_nothing_under_meow_verbs(self):
        """Criterion 2: no file under `plugins/meow-verbs` is tracked, whatever an ignored build left there."""
        tracked = subprocess.run(["git", "ls-files", "--", "plugins/meow-verbs"],
                                 cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(tracked.stdout, "")


LIVE = ("plugins", "docs", "tools", "crates", ".claude-plugin", ".meowpaw", ".github", "README.md", "llms.txt",
        "CLAUDE.md", "mise.toml", "REUSE.toml", "project/specs", "project/vision.md", "project/README.md")


class Renamed(unittest.TestCase):
    """TSK-3850, ADR-2300: `meow-verbs` is `meow-checks`. ADR-2360 ended the stub the old name kept for one release."""

    def plugins(self):
        return {p["name"]: p for p in json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"]}

    def test_the_marketplace_ships_meow_checks(self):
        """Criterion 1, REQ-3634: the unit installs as `meow-checks`, with its skill and its program under that name."""
        self.assertIn("meow-checks", self.plugins())
        unit = ROOT / "plugins" / "meow-checks"
        manifest = json.loads((unit / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], "meow-checks")
        self.assertTrue((unit / "skills/verify/SKILL.md").is_file())
        self.assertEqual(sorted(p.name for p in (unit / "bin").iterdir() if p.is_file()), ["meow-checks"])

    def test_only_the_stub_names_the_old_unit(self):
        """TSK-4070 criterion 3, REQ-3634: outside frozen records, the old name appears only in the page that tells
        an install to move, in the specification's sentence about the rename, and in these checks."""
        allowed = ("tools/test_marketplace.py", "docs/troubleshooting.md", "tools/check_terms.py", "tools/test_check_terms.py")
        # Lines that name the old unit, and nothing else in their file. The README line is a frozen
        # record's title (ADR-1480), which keeps the name, so it is not a fourth file naming the unit.
        named = {"project/specs/SPC-1040-the-five-verbs.md": "it was `meow-verbs`",
                 "project/README.md": "ADR-1480"}
        tracked = subprocess.run(["git", "ls-files", "--", *LIVE], cwd=ROOT, capture_output=True, text=True, check=True)
        found = []
        for name in tracked.stdout.splitlines():
            if name.startswith(allowed):
                continue
            try:
                text = (ROOT / name).read_text(encoding="utf-8")
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            lines = text.splitlines()
            for number, line in enumerate(lines, 1):
                before = lines[number - 2] if number > 1 else ""
                if "meow-verbs" in line and named.get(name, "\0") not in line + before:
                    found.append(f"{name}:{number}")
        self.assertEqual(found, [])


def archive(name):
    return {"source": "archive", "url": f"https://example.test/{name}.zip", "sha256": "0" * 64}


class ReleasedFile(unittest.TestCase):
    """TSK-5240, BUG-1520: the released `marketplace.json` holds an archive for every unit (REQ-1485)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "tools"))
        import marketplace_release
        cls.tool = marketplace_release

    def doc(self, **sources):
        return {"name": "meowpaw", "plugins": [{"name": n, "source": s} for n, s in sources.items()]}

    def test_a_single_unit_run_keeps_the_other_units_archives(self):
        """Criterion 1: a tag run packs `meow-b` alone, and filling from the published file leaves an archive
        for each of the three units."""
        packed = self.doc(**{"meow-a": "./plugins/meow-a", "meow-b": archive("meow-b"), "meow-c": "./plugins/meow-c"})
        previous = self.doc(**{"meow-a": archive("meow-a"), "meow-b": archive("old-b"), "meow-c": archive("meow-c")})
        filled = self.tool.fill(packed, previous)
        self.assertEqual({p["name"]: p["source"] for p in filled["plugins"]},
                         {"meow-a": archive("meow-a"), "meow-b": archive("meow-b"), "meow-c": archive("meow-c")})
        self.assertEqual(self.tool.relative_entries(filled), [])

    def test_a_unit_the_previous_file_lacks_stays_relative(self):
        """Criterion 1: fill invents no archive, so the check still names a unit nobody packed."""
        packed = self.doc(**{"meow-a": archive("meow-a"), "meow-new": "./plugins/meow-new"})
        previous = self.doc(**{"meow-a": archive("meow-a")})
        self.assertEqual(self.tool.relative_entries(self.tool.fill(packed, previous)), ["meow-new"])

    def test_the_check_exits_1_and_names_the_relative_entry(self):
        """Criterion 2: one string `source` fails the check, and the output names that unit and no other."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "marketplace.json"
            path.write_text(json.dumps(self.doc(**{"meow-a": archive("meow-a"), "meow-flow": "./plugins/meow-flow"})))
            run = subprocess.run([sys.executable, str(ROOT / "tools/marketplace_release.py"), "check", str(path)],
                                 capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertIn("meow-flow", run.stdout + run.stderr)
        self.assertNotIn("meow-a", run.stdout + run.stderr)

    def test_the_check_exits_0_where_every_entry_is_an_archive(self):
        """Criterion 3: a file with only archives passes the check the workflow runs before it publishes."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "marketplace.json"
            path.write_text(json.dumps(self.doc(**{"meow-a": archive("meow-a"), "meow-b": archive("meow-b")})))
            run = subprocess.run([sys.executable, str(ROOT / "tools/marketplace_release.py"), "check", str(path)],
                                 capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_fill_rewrites_the_file_and_tolerates_no_published_file(self):
        """Criterion 1: the command the workflow runs fills from a published file, and leaves the file alone
        where the release has none yet."""
        tool = str(ROOT / "tools/marketplace_release.py")
        with tempfile.TemporaryDirectory() as tmp:
            path, previous = Path(tmp) / "marketplace.json", Path(tmp) / "previous.json"
            path.write_text(json.dumps(self.doc(**{"meow-a": "./plugins/meow-a"})))
            previous.write_text(json.dumps(self.doc(**{"meow-a": archive("meow-a")})))
            run = subprocess.run([sys.executable, tool, "fill", str(path), str(Path(tmp) / "absent.json")],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(self.tool.relative_entries(json.loads(path.read_text())), ["meow-a"])
            run = subprocess.run([sys.executable, tool, "fill", str(path), str(previous)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(self.tool.relative_entries(json.loads(path.read_text())), [])

    def test_the_workflow_checks_the_file_before_it_publishes(self):
        """Criterion 3: `claude-release.yml` runs the check between packing and the `Publish` step."""
        text = (ROOT / ".github/workflows/claude-release.yml").read_text()
        self.assertIn("tools/marketplace_release.py check dist/marketplace.json", text)
        self.assertLess(text.index("marketplace_release.py check"), text.index("- name: Publish"))


if __name__ == "__main__":
    unittest.main()
