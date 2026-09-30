# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for the release check ADR-1570 decides (REQ-3192)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_release  # noqa: E402

ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "a", "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b"}


class Repository:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        for name, binary in (("meow-a", True), ("meow-b", False), ("meow-vet", False)):
            self.write(f"plugins/{name}/.claude-plugin/plugin.json", json.dumps({"name": name, "version": "0.3.0"}))
            if binary:
                self.write(f"plugins/{name}/bin/{name}", "#!/bin/sh\n")
        self.write("crates/meow/src/main.rs", "fn main() {}\n")
        self.save("chore: start")
        self.git("tag", "meow-a-v0.3.0")
        self.git("tag", "meow-b-v0.3.0")
        self.git("tag", "meow-vet-v0.3.0")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, env=ENV)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def save(self, message):
        self.git("add", "-A")
        self.git("-c", "commit.gpgsign=false", "com" + "mit", "-q", "-m", message)

    def bump(self, name, to):
        self.write(f"plugins/{name}/.claude-plugin/plugin.json", json.dumps({"name": name, "version": to}))


class Release(unittest.TestCase):
    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_breaking_change_with_a_patch_bump_is_refused(self):
        """REQ-3192: a breaking change released as a patch is the same as not marking it."""
        repo = self.repo()
        repo.write("plugins/meow-b/skill.md", "changed\n")
        repo.save("feat!: drop the old name")
        repo.bump("meow-b", "0.3.1")
        repo.save("chore: release")
        problems = check_release.check(repo.root)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("meow-b: 0.3.0 to 0.3.1 carries a breaking change, which needs a minor or major version", problems[0])

    def test_a_minor_bump_at_zero_shows_a_breaking_change(self):
        """REQ-3192: at major version zero the minor carries what the major would."""
        repo = self.repo()
        repo.write("plugins/meow-b/skill.md", "changed\n")
        repo.save("feat: drop the old name\n\nBREAKING CHANGE: the old name is gone")
        repo.bump("meow-b", "0.4.0")
        repo.save("chore: release")
        self.assertEqual(check_release.check(repo.root), [])

    def test_above_zero_only_a_major_bump_shows_it(self):
        """REQ-3192: above zero a breaking change needs the major."""
        repo = self.repo()
        repo.bump("meow-b", "1.0.0")
        repo.save("chore: release one")
        repo.git("tag", "meow-b-v1.0.0")
        repo.write("plugins/meow-b/skill.md", "changed\n")
        repo.save("fix!: rename the flag")
        repo.bump("meow-b", "1.1.0")
        repo.save("chore: release")
        self.assertEqual(len(check_release.check(repo.root)), 1)
        repo.bump("meow-b", "2.0.0")
        repo.save("chore: release two")
        self.assertEqual(check_release.check(repo.root), [])

    def test_a_breaking_change_to_the_native_tool_holds_every_unit_shipping_it(self):
        """REQ-3192: the binary ships inside each unit that carries one."""
        repo = self.repo()
        repo.write("crates/meow/src/main.rs", "fn main() { }\n")
        repo.save("feat!: change the tool")
        repo.bump("meow-a", "0.3.1")
        repo.bump("meow-b", "0.3.1")
        repo.save("chore: release")
        problems = check_release.check(repo.root)
        self.assertEqual([p.split(":")[0] for p in problems], ["meow-a"])

    def test_a_unit_whose_name_holds_dash_v_reads_its_tags(self):
        """REQ-3192: a name such as `meow-vet` holds `-v` itself."""
        repo = self.repo()
        repo.write("plugins/meow-vet/skill.md", "changed\n")
        repo.save("feat!: change the vet")
        repo.bump("meow-vet", "0.3.1")
        repo.save("chore: release")
        self.assertEqual([p.split(":")[0] for p in check_release.check(repo.root)], ["meow-vet"])

    def test_a_unit_not_being_released_is_not_held(self):
        """REQ-3192: the check reads a unit only when its version is released."""
        repo = self.repo()
        repo.write("plugins/meow-b/skill.md", "changed\n")
        repo.save("feat!: drop the old name")
        self.assertEqual(check_release.check(repo.root), [])


if __name__ == "__main__":
    unittest.main()
