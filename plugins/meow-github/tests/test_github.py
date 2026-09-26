# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for meow-github: the history read through a stand-in gh (ADR-1290)."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_GITHUB_BIN", UNIT / "bin" / "meow-github"))

ISSUE = {"number": 1, "title": "Refuse an empty title", "body": "It must refuse one.", "state": "open",
         "user": {"login": "ada"}, "html_url": "https://github.com/o/r/issues/1", "labels": [{"name": "bug"}]}
MERGED = dict(ISSUE, number=2, title="Refuse it", body="Closes #1", state="closed", pull_request={},
              html_url="https://github.com/o/r/pull/2", labels=[])
REJECTED = dict(MERGED, number=3, title="Warn instead", html_url="https://github.com/o/r/pull/3")
LISTINGS = {
    "repos/o/r/issues?state=all&per_page=100": [[ISSUE, MERGED], [REJECTED]],
    "repos/o/r/pulls?state=all&per_page=100": [[{"number": 2, "merged_at": "2026-01-01T00:00:00Z"},
                                               {"number": 3, "merged_at": None}]],
    "repos/o/r/issues/comments?per_page=100": [[{"issue_url": "https://api.github.com/repos/o/r/issues/3", "user": {"login": "bo"},
                                                "body": "A warning is ignored.", "html_url": "https://github.com/o/r/pull/3#c1"}]],
    "repos/o/r/pulls/comments?per_page=100": [[{"pull_request_url": "https://api.github.com/repos/o/r/pulls/2", "path": "a.txt",
                                               "user": {"login": "bo"}, "body": "Why here?", "html_url": "https://github.com/o/r/pull/2#r1"}]],
}
STAND_IN = """#!/bin/sh
printf '%s\\n' "$*" >> "$GH_LOG"
if [ "$1" = "api" ] && [ "$2" = "$GH_REFUSE" ]; then
  echo "HTTP 403: Resource not accessible by integration" >&2
  exit 1
fi
exec python3 -c 'import json, sys; print(json.dumps(json.load(open(sys.argv[1]))[sys.argv[2]]))' "$GH_DATA" "$2"
"""


class History(unittest.TestCase):
    def run_history(self, listings=LISTINGS, refuse=""):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "gh").write_text(STAND_IN, encoding="utf-8")
        (root / "gh").chmod(0o755)
        (root / "data.json").write_text(json.dumps(listings), encoding="utf-8")
        env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}", "GH_DATA": str(root / "data.json"),
               "GH_LOG": str(root / "log"), "GH_REFUSE": refuse}
        done = subprocess.run([str(BIN), "history", "o/r"], cwd=root, capture_output=True, text=True, env=env)
        calls = (root / "log").read_text(encoding="utf-8").splitlines() if (root / "log").exists() else []
        return done, calls

    def test_history_reads_every_listing_and_page(self):
        done, calls = self.run_history()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        history = json.loads(done.stdout)
        self.assertEqual([(i["number"], i["kind"], i["merged"]) for i in history["issues"]],
                         [(1, "issue", None), (2, "pull request", True), (3, "pull request", False)])
        self.assertEqual(history["issues"][0]["labels"], ["bug"])
        self.assertEqual(history["comments"], [{"on": 3, "author": "bo", "body": "A warning is ignored.", "url": "https://github.com/o/r/pull/3#c1"}])
        self.assertEqual(history["review_comments"][0]["on"], 2)
        self.assertEqual(len(calls), 4)
        for call in calls:
            self.assertTrue(call.endswith("--paginate --slurp --cache 1h"), call)

    def test_a_missing_field_fails_by_name(self):
        listings = dict(LISTINGS)
        listings["repos/o/r/issues?state=all&per_page=100"] = [[{k: v for k, v in ISSUE.items() if k != "title"}]]
        done, _ = self.run_history(listings)
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("lacks the field `title`", done.stdout)
        self.assertNotIn('"issues"', done.stdout)

    def test_a_refused_listing_leaves_the_history_unread(self):
        done, _ = self.run_history(refuse="repos/o/r/issues/comments?per_page=100")
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn("meow-github history: unread: conversation comments, repos/o/r/issues/comments?per_page=100: HTTP 403", done.stdout)
        self.assertIn("read before it stopped: issues and pull requests, pull requests;", done.stdout)
        self.assertNotIn('"issues"', done.stdout)


class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-github"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-github").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "history"], cwd=tmp, capture_output=True, text=True)
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("unread", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("reinstall the unit", done.stdout)


if __name__ == "__main__":
    unittest.main()
