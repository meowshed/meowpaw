# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for meow-github: the history read, the projection and the upgrade through a stand-in gh (ADR-1290, ADR-1810, ADR-3090)."""

import calendar
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
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
# ADR-1810: under `--include` the stand-in prints a status line and a header block before the body, with a `Link`
# header naming the next page, and a refused call's block too, as RES-0290 saw gh 2.101.0 do.
STAND_IN = """#!/usr/bin/env python3
import email.utils, json, os, sys
args = sys.argv[1:]
open(os.environ["GH_LOG"], "a").write(" ".join(args) + "\\n")
path = args[1].removeprefix("https://api.github.com/")
base, _, page = path.partition("&page=")
page = int(page or 1)
link = None
if path == os.environ["GH_REFUSE"]:
    status, body = 403, {"message": "Resource not accessible by integration"}
else:
    pages = json.load(open(os.environ["GH_DATA"]))[base]
    status, body = 200, pages[page - 1]
    if page < len(pages):
        link = f'<https://api.github.com/{base}&page={page + 1}>; rel="next"'
if "--include" in args:
    print(f"HTTP/2.0 {status} {'OK' if status == 200 else 'Forbidden'}")
    print("Date: " + email.utils.formatdate(usegmt=True))
    if link:
        print("Link: " + link)
    print()
print(json.dumps(body))
if status >= 400:
    print(f"gh: {body['message']} (HTTP {status})", file=sys.stderr)
    sys.exit(1)
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
        # ADR-1810: one page a call, following `Link`, and every read but the run's first through the cache.
        self.assertEqual(len(calls), 5, calls)
        self.assertIn("repos/o/r/issues?state=all&per_page=100&page=2", calls[1])
        self.assertTrue(calls[0].endswith(" --include"), calls[0])
        for call in calls[1:]:
            self.assertTrue(call.endswith(" --include --cache 1h"), call)

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
        self.assertIn("meow-github history: unread: conversation comments: refused: GET "
                      "repos/o/r/issues/comments?per_page=100 needs ", done.stdout)
        self.assertIn("read before it stopped: issues and pull requests, pull requests;", done.stdout)
        self.assertNotIn('"issues"', done.stdout)

    def test_the_document_names_the_credential_and_the_budget(self):
        """TSK-2950 criterion 6, REQ-2568, REQ-2582: the document carries `credential`, the form, and `budget`, the
        budget lines naming the four counts, and every field onboarding reads is as it was."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        # The layered stand-in and its runner, defined below with the request layer's checks.
        Layered.stand_in(self, root, {"listings": SINGLE_PAGES})
        done = Layered.meow_github(self, root, "history", "o/r", credential={})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        document = json.loads(done.stdout)
        self.assertEqual(document.get("credential"), FORMS[None], document.keys())
        budget = document.get("budget")
        self.assertIsInstance(budget, list, budget)
        self.assertTrue(all(isinstance(line, str) for line in budget), budget)
        for count in COUNTS:
            self.assertEqual(len([line for line in budget if count in line]), 1, (count, budget))
        read = {k: v for k, v in document.items() if k not in ("credential", "budget")}
        issue = {"number": 1, "kind": "issue", "title": ISSUE["title"], "body": ISSUE["body"], "state": "open",
                 "merged": None, "author": "ada", "url": ISSUE["html_url"], "labels": ["bug"]}
        pull = {"number": 2, "kind": "pull request", "title": MERGED["title"], "body": MERGED["body"],
                "state": "closed", "merged": True, "author": "ada", "url": MERGED["html_url"], "labels": []}
        self.assertEqual(read, {"repository": "o/r", "issues": [issue, pull], "comments": [], "review_comments": []})


TRACKER = """#!/usr/bin/env python3
import json, os, sys
state_path = os.environ["GH_STATE"]
state = json.load(open(state_path)) if os.path.exists(state_path) else {"issues": {}, "calls": []}
args = sys.argv[1:]
state["calls"].append(args)
fields = {}
method = "GET"
i = 2
while i < len(args):
    if args[i] == "-X":
        method = args[i + 1]; i += 2
    elif args[i] == "-f":
        key, _, value = args[i + 1].partition("="); fields[key] = value; i += 2
    else:
        i += 1
path = args[1]
parts = path.split("/")
if method == "POST":
    number = len(state["issues"]) + 1
    state["issues"][str(number)] = {"number": number, "state": "open", **fields}
    out = state["issues"][str(number)]
elif method == "PATCH":
    state["issues"][parts[-1]].update(fields)
    out = state["issues"][parts[-1]]
elif parts[-1].startswith("issues?"):
    out = list(state["issues"].values())
else:
    out = state["issues"][parts[-1]]
json.dump(state, open(state_path, "w"))
if "--include" in args:
    import email.utils
    print(f"HTTP/2.0 {201 if method == 'POST' else 200} OK")
    print("Date: " + email.utils.formatdate(usegmt=True))
    print()
print(json.dumps(out))
"""

# The read-back listing `project` sends after its last create (SPC-1080), with `since` as a UTC time.
LISTING = r"^repos/o/r/issues\?state=all&since=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)&per_page=100$"

DECISION = """---
id: ADR-0001
artifact: adr
status: {status}
revised: 2026-01-01
addresses: [REQ-0001, REQ-0002]
issue:
---

# Refuse an empty title

Text.

## Plan

1. Refuse it.
"""

DEFECT = """---
id: BUG-0001
artifact: bug
status: {status}
revised: 2026-01-01
violates: [REQ-0004]
issue:
---

# A defect

## Plan

1. Restore the behaviour.
"""

RECORD = "project/adrs/ADR-0001-a-choice.md"


class Project(unittest.TestCase):
    def repository(self, status="approved", tracker='[tracker]\nkind = "github"\n'):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".meowpaw").mkdir()
        (root / ".meowpaw" / "profile.toml").write_text(tracker, encoding="utf-8")
        (root / "project" / "adrs").mkdir(parents=True)
        (root / RECORD).write_text(DECISION.format(status=status), encoding="utf-8")
        (root / "bin").mkdir()
        (root / "bin" / "gh").write_text(TRACKER, encoding="utf-8")
        (root / "bin" / "gh").chmod(0o755)
        return root

    def project(self, root, *extra, target="ADR-0001"):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json")}
        return subprocess.run([str(BIN), "project", target, "o/r", *extra], cwd=root, capture_output=True, text=True, env=env)

    def state(self, root):
        return json.loads((root / "state.json").read_text(encoding="utf-8"))

    def text(self, root, name=RECORD):
        return (root / name).read_text(encoding="utf-8")

    def retitle(self, root):
        path = root / RECORD
        path.write_text(path.read_text(encoding="utf-8").replace("# Refuse an empty title", "# Refuse a blank title"), encoding="utf-8")

    def test_an_approved_decision_projects_one_issue(self):
        """REQ-4002: one record is one issue, whose body names its requirements and carries its plan."""
        root = self.repository()
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issues = self.state(root)["issues"]
        self.assertEqual([i["title"] for i in issues.values()], ["ADR-0001: Refuse an empty title"])
        body = issues["1"]["body"]
        self.assertIn("The work of ADR-0001.", body)
        self.assertIn("Names REQ-0001, REQ-0002.", body)
        self.assertIn("## Plan\n\n1. Refuse it.", body)
        self.assertRegex(body, r"<!-- meow-github: projected from ADR-0001 at [0-9a-f]{12} -->$")
        text = self.text(root)
        self.assertIn("\nissue: 1\n", text)
        self.assertRegex(text, r"\nprojected: [0-9a-f]{12}\ntracked: [0-9a-f]{12}\n---\n")
        self.assertRegex(done.stdout, r"(?m)^ADR-0001: projected to issue #1 at [0-9a-f]{12}, read back$")
        gets = [c for c in self.state(root)["calls"] if "-X" not in c]
        self.assertEqual(len(gets), 1, gets)
        self.assertRegex(gets[0][1], LISTING)

    def test_the_fingerprint_is_reproducible_by_hand(self):
        root = self.repository()
        self.project(root)
        issue = self.state(root)["issues"]["1"]
        body = issue["body"].rsplit("\n\n", 1)[0]
        by_hand = hashlib.sha256(f"{issue['title']}\n{body}".encode()).hexdigest()[:12]
        self.assertIn(f"\nprojected: {by_hand}\n", self.text(root))

    def test_a_replay_changes_nothing(self):
        root = self.repository()
        self.project(root)
        before = (self.state(root), self.text(root))
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(len(self.state(root)["issues"]), 1)
        self.assertFalse([c for c in self.state(root)["calls"][len(before[0]["calls"]):] if "-X" in c])
        self.assertEqual(before[1], self.text(root))
        self.assertIn("ADR-0001: unchanged, issue #1 at", done.stdout)

    def test_a_record_with_no_issue_field_gets_one_and_a_replay_opens_nothing(self):
        """REQ-4002: the mapping is written on the record even where the field was missing, so a replay is no action."""
        root = self.repository()
        path = root / RECORD
        path.write_text(path.read_text(encoding="utf-8").replace("issue:\n", "", 1), encoding="utf-8")
        self.project(root)
        self.assertRegex(self.text(root), r"\nissue: 1\nprojected: [0-9a-f]{12}\ntracked: [0-9a-f]{12}\n---\n")
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(len(self.state(root)["issues"]), 1)
        self.assertIn("ADR-0001: unchanged, issue #1 at", done.stdout)

    def writes(self, root, since=0):
        return [c for c in self.state(root)["calls"][since:] if "-X" in c]

    def test_a_changed_record_updates_its_issue(self):
        root = self.repository()
        self.project(root)
        before = self.text(root)
        self.retitle(root)
        calls = len(self.state(root)["calls"])
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "ADR-0001: Refuse a blank title")
        self.assertEqual([c[:4] for c in self.writes(root, calls)], [["api", "repos/o/r/issues/1", "-X", "PATCH"]])
        self.assertNotEqual(before.split("projected: ")[1][:12], self.text(root).split("projected: ")[1][:12])

    def test_an_issue_edited_on_github_is_reported_and_left(self):
        root = self.repository()
        self.project(root)
        state = self.state(root)
        state["issues"]["1"]["body"] = "Rewritten by a person."
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        done = self.project(root)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001: issue #1 was edited on GitHub since it was projected", done.stdout)
        self.assertEqual(self.state(root)["issues"]["1"]["body"], "Rewritten by a person.")
        self.assertFalse(self.writes(root, len(state["calls"])))

    def test_a_closed_issue_on_an_open_record_is_reported_and_check_writes_nothing(self):
        root = self.repository()
        self.project(root)
        state = self.state(root)
        state["issues"]["1"]["state"] = "closed"
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        self.retitle(root)
        before = self.text(root)
        done = self.project(root, "--check")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001: issue #1 is closed on GitHub while the decision isn't done", done.stdout)
        self.assertIn("ADR-0001: changed since it was projected at", done.stdout)
        self.assertIn("would be updated", done.stdout)
        self.assertFalse(self.writes(root, len(state["calls"])))
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "ADR-0001: Refuse an empty title")
        self.assertEqual(self.text(root), before)

    def test_a_repository_declaring_no_tracker_projects_nothing(self):
        root = self.repository(tracker="[verbs]\n")
        done = self.project(root)
        self.assertEqual(done.returncode, 3, done.stdout)
        self.assertIn(".meowpaw/profile.toml declares no tracker, so nothing is projected; declare `[tracker] kind = \"github\"`", done.stdout)
        self.assertFalse((root / "state.json").exists())
        self.assertNotIn("issue: 1", self.text(root))

    def test_project_groups_an_issue_nowhere(self):
        """TSK-2910 criterion 4, REQ-4002: `project` passes no grouping argument and no grouping field, so an issue
        sits under nothing on the tracker."""
        root = self.repository()
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.state(root)["calls"]
        self.assertTrue(self.writes(root), calls)
        # ADR-1810: every call ends with the request layer's `--include`, which groups nothing; the shape is read
        # without it.
        for call in calls:
            self.assertEqual(call[-1], "--include", call)
        calls = [call[:-1] for call in calls]
        for call in calls:
            for flag in ("--milestone", "--parent", "--project", "--label"):
                self.assertFalse([a for a in call if a == flag or a.startswith(flag + "=")], call)
            fields = [call[i + 1].partition("=")[0] for i, a in enumerate(call[:-1]) if a in ("-f", "-F", "--field", "--raw-field")]
            self.assertLessEqual(set(fields), {"title", "body"}, call)
            # BUG-1301: each call has exactly one of the three shapes `project` sends, so a grouping sent through
            # `--input`, an `--add-` flag or an extra argument of any other kind fails here.
            self.assertEqual(call[0], "api", call)
            self.assertRegex(call[1], r"^repos/o/r/issues(/\d+|\?state=all&since=[^&]+&per_page=100)?$", call)
            if len(call) > 2:
                self.assertEqual(len(call), 8, call)
                self.assertIn(call[2:4], (["-X", "POST"], ["-X", "PATCH"]), call)
                self.assertEqual([call[4], call[6]], ["-f", "-f"], call)
                self.assertTrue(call[5].startswith("title=") and call[7].startswith("body="), call)

    def test_a_draft_decision_projects_nothing(self):
        """REQ-4002: a draft waits for its approval."""
        root = self.repository(status="draft")
        done = self.project(root)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001 is draft, and it is projected only once it is approved", done.stdout)
        self.assertFalse((root / "state.json").exists())

    def test_a_done_decision_projects_like_an_approved_one(self):
        """TSK-5190 criterion 2, REQ-3678: done remains a post-approval projection input."""
        root = self.repository(status="done")
        done = self.project(root)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("issue: 1", self.text(root))

    def test_a_retired_kind_maps_to_no_issue(self):
        """ADR-3090: only a decision or a defect maps to an issue, so a task or an epic is refused before any call."""
        root = self.repository()
        for target in ("TSK-0001", "EPC-0001"):
            done = self.project(root, target=target)
            self.assertEqual(done.returncode, 1, done.stdout)
            self.assertIn(f"{target} is no decision or defect, and only those map to an issue", done.stdout)
        self.assertFalse((root / "state.json").exists())

    def defect(self, root, status="approved"):
        (root / "project" / "bugs").mkdir()
        (root / "project" / "bugs" / "BUG-0001-a-defect.md").write_text(DEFECT.format(status=status), encoding="utf-8")

    def test_an_approved_defect_projects_one_issue_and_replays_nothing(self):
        """TSK-5180 criteria 1-2, REQ-4002: a BUG target shares the durable issue mapping and the replay."""
        root = self.repository()
        self.defect(root)
        done = self.project(root, target="BUG-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issue = self.state(root)["issues"]["1"]
        self.assertEqual(issue["title"], "BUG-0001: A defect")
        body = issue["body"].rsplit("\n\n<!-- meow-github:", 1)[0]
        self.assertEqual(body, "The work of BUG-0001.\n\nNames REQ-0004.\n\n## Plan\n\n1. Restore the behaviour.")
        self.assertIn("\nissue: 1\n", self.text(root, "project/bugs/BUG-0001-a-defect.md"))
        calls = len(self.state(root)["calls"])
        replay = self.project(root, target="BUG-0001")
        self.assertEqual(replay.returncode, 0, replay.stdout)
        self.assertFalse(self.writes(root, calls))

    def test_a_defects_status_decides_whether_a_closed_issue_agrees(self):
        """TSK-5180 criterion 3, REQ-3678: the record, not the tracker's state, decides done."""
        root = self.repository()
        self.defect(root)
        self.project(root, target="BUG-0001")
        state = self.state(root)
        state["issues"]["1"]["state"] = "closed"
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        calls = len(state["calls"])
        still_open = self.project(root, "--check", target="BUG-0001")
        self.assertEqual(still_open.returncode, 1, still_open.stdout)
        self.assertIn("is closed on GitHub while the defect isn't done", still_open.stdout)
        self.assertFalse(self.writes(root, calls))
        calls = len(self.state(root)["calls"])
        bug = root / "project" / "bugs" / "BUG-0001-a-defect.md"
        bug.write_text(bug.read_text(encoding="utf-8").replace("status: approved", "status: done"), encoding="utf-8")
        closed = self.project(root, "--check", target="BUG-0001")
        self.assertEqual(closed.returncode, 0, closed.stdout)
        self.assertNotIn("isn't done", closed.stdout)
        self.assertFalse(self.writes(root, calls))

    def test_the_shipped_surfaces_name_a_defect_projection_target(self):
        """TSK-5180 criterion 4, REQ-4002: launcher and reference expose BUG targets."""
        launcher = (UNIT / "bin" / "meow-github").read_text(encoding="utf-8")
        page = (UNIT / "README.md").read_text(encoding="utf-8")
        self.assertIn("project <decision|defect>", launcher)
        self.assertIn("meow-github project BUG-1210", page)


# ADR-1810: the stand-in `gh` the request layer's checks run against. It prints a status line and a header block
# before the body under `--include`, as RES-0290 saw gh 2.101.0 do, and prints a refused call's block too. Its `Date`
# is the injected local clock, the file MEOW_GITHUB_CLOCK names, less GH_SKEW seconds. The run under test reads the
# same file as its clock and sleeps by adding the seconds to it, so no check waits in real time. GH_SCRIPT names a
# JSON file: `responses` holds, for each "<METHOD> <path>", the answers to give in turn before the default one,
# `listings` holds each listing's body, `bare` leaves every rate-limit header out, `headers` replaces rate-limit
# headers on every response, and `cached` gives the age, `remaining` and reset of the headers a call sent with
# `--cache` replays. A `null` among the `responses` lets that call through to the default answer. Each issue holds
# the time on GitHub's clock it was written at, and the read-back listing answers with the issues written at or after
# its `since`. A create writes its issue `lag` seconds before the `Date` of its answer, `lag` being one number for
# every create or a list with one for each, and its answer carries the issue's `updated_at` unless `no_updated_at`
# is set. The listing leaves out the numbers `omit` names, with the body of each number `alter` names changed and the title of each number
# `retitle` names changed, and a read of one issue by number shows the body of each number `read_alter` names changed and the title of each
# number `read_retitle` names changed, and `page_size`
# at a time where the script sets it, each page but the last naming the next in a `Link` header.
LAYERED = """#!/usr/bin/env python3
import calendar, email.utils, json, os, sys, time
state_path = os.environ["GH_STATE"]
state = json.load(open(state_path)) if os.path.exists(state_path) else {"issues": {}, "calls": [], "used": {}}
script = json.load(open(os.environ["GH_SCRIPT"]))
now = float(open(os.environ["MEOW_GITHUB_CLOCK"]).read())
github_now = now - float(os.environ.get("GH_SKEW", "0"))
args = sys.argv[1:]
state["calls"].append({"args": args, "at": now})
method, fields, path, i = "GET", {}, None, 1
while i < len(args):
    a = args[i]
    if a in ("-X", "--method"):
        method = args[i + 1]; i += 2
    elif a.startswith("--method="):
        method = a.split("=", 1)[1]; i += 1
    elif a in ("-f", "-F", "--field", "--raw-field"):
        key, _, value = args[i + 1].partition("="); fields[key] = value; i += 2
    elif a in ("--cache", "-H", "--header", "-q", "--jq", "--input", "-t", "--template"):
        i += 2
    elif a.startswith("-"):
        i += 1
    else:
        path = path or a.removeprefix("https://api.github.com/"); i += 1
key = f"{method} {path}"
headers = {"Date": email.utils.formatdate(github_now, usegmt=True)}
if not script.get("bare"):
    headers.update({"X-Ratelimit-Limit": "5000", "X-Ratelimit-Remaining": "4990", "X-Ratelimit-Used": "10",
                    "X-Ratelimit-Resource": "core", "X-Ratelimit-Reset": str(int(github_now) + 3600)})
    headers.update(script.get("headers", {}))
cached = script.get("cached")
if cached and "--cache" in args:
    stored = github_now - cached["age"]
    headers.update({"Date": email.utils.formatdate(stored, usegmt=True),
                    "X-Ratelimit-Remaining": str(cached["remaining"]),
                    "X-Ratelimit-Reset": str(int(github_now) + cached["reset_in"])})
queue = script.get("responses", {}).get(key, [])
used = state["used"].get(key, 0)
answer = None
if used < len(queue):
    state["used"][key] = used + 1
    answer = queue[used]
if answer is not None:
    status, body = answer["status"], answer.get("body", {"message": "scripted"})
    headers.update(answer.get("headers", {}))
elif method == "POST":
    number = len(state["issues"]) + 1
    lag = script.get("lag", 0)
    written = github_now - (lag[number - 1] if isinstance(lag, list) and number <= len(lag) else
                            lag if not isinstance(lag, list) else 0)
    state["issues"][str(number)] = {"number": number, "state": "open", "written": written, **fields}
    if not script.get("no_updated_at"):
        state["issues"][str(number)]["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(written))
    status, body = 201, state["issues"][str(number)]
elif method == "PATCH":
    state["issues"][path.split("/")[-1]].update(fields, written=github_now)
    status, body = 200, state["issues"][path.split("/")[-1]]
elif path.startswith("repos/o/r/issues?state=all&since="):
    since = calendar.timegm(time.strptime(path.split("since=")[1].split("&")[0], "%Y-%m-%dT%H:%M:%SZ"))
    listed = [dict(issue, body="Rewritten.") if issue["number"] in script.get("alter", []) else
              dict(issue, title="Retitled.") if issue["number"] in script.get("retitle", []) else issue
              for issue in state["issues"].values()
              if issue["written"] >= since and issue["number"] not in script.get("omit", [])]
    size = script.get("page_size", len(listed) or 1)
    page = int(path.split("&page=")[1]) if "&page=" in path else 1
    if page * size < len(listed):
        following = "https://api.github.com/" + path.split("&page=")[0] + f"&page={page + 1}"
        headers["Link"] = f'<{following}>; rel="next"'
    status, body = 200, listed[(page - 1) * size:page * size]
elif path in script.get("listings", {}):
    status, body = 200, script["listings"][path]
elif path.split("/")[-1] in state["issues"]:
    status, body = 200, state["issues"][path.split("/")[-1]]
    if body["number"] in script.get("read_alter", []):
        body = dict(body, body="Rewritten.")
    if body["number"] in script.get("read_retitle", []):
        body = dict(body, title="Retitled.")
else:
    status, body = 404, {"message": "Not Found"}
json.dump(state, open(state_path, "w"))
if "--include" in args:
    reason = {200: "OK", 201: "Created", 403: "Forbidden", 404: "Not Found", 429: "Too Many Requests"}.get(status, "")
    print(f"HTTP/2.0 {status} {reason}")
    for name, value in headers.items():
        print(f"{name}: {value}")
    print()
print(json.dumps([body] if "--slurp" in args else body))
if status >= 400:
    print(f"gh: {body.get('message', '')} (HTTP {status})", file=sys.stderr)
    sys.exit(1)
"""

# The local clock every layered check starts at: the moment RES-0290 read `date -u +%s`, 14:30:37 UTC on 2026-09-29.
START = 1790692237
SECONDARY = {"message": "You have exceeded a secondary rate limit. Please wait a few minutes before you try again."}


class Sync(unittest.TestCase):
    """TSK-5320 and TSK-5321, ADR-2890, ADR-3090: a record and its issue are synchronised by a fingerprint of each side."""

    repository = Project.repository
    state = Project.state
    text = Project.text
    retitle = Project.retitle
    writes = Project.writes

    def run_tool(self, root, command, *extra):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json")}
        return subprocess.run([str(BIN), command, "ADR-0001", "o/r", *extra], cwd=root, capture_output=True, text=True, env=env)

    def synced(self):
        """A projected decision."""
        root = self.repository()
        self.run_tool(root, "project")
        return root

    def edit_issue(self, root, number, **fields):
        state = self.state(root)
        state["issues"][str(number)].update(fields)
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")

    def test_project_writes_the_tracker_fingerprint_beside_the_record_s(self):
        """TSK-5320 criterion 1, REQ-4002: `projected` and `tracked` are both on the record after `project`."""
        self.assertRegex(self.text(self.synced()), r"\nprojected: [0-9a-f]{12}\ntracked: [0-9a-f]{12}\n---\n")

    def test_a_mapping_with_the_record_side_only_gains_the_tracker_side(self):
        """TSK-5320 criterion 2, REQ-4002: an older mapping is read, and the next `project` adds `tracked`, nothing else."""
        root = self.synced()
        path = root / RECORD
        older = re.sub(r"\ntracked: [0-9a-f]{12}", "", path.read_text(encoding="utf-8"))
        path.write_text(older, encoding="utf-8")
        done = self.run_tool(root, "project")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertRegex(path.read_text(encoding="utf-8"), r"\nprojected: [0-9a-f]{12}\ntracked: [0-9a-f]{12}\n---\n")
        self.assertEqual(re.sub(r"\ntracked: [0-9a-f]{12}", "", path.read_text(encoding="utf-8")), older)

    def test_a_replay_of_an_unchanged_record_writes_nothing(self):
        """REQ-4002: where neither side changed, the run says so and sends no write."""
        root = self.synced()
        calls = len(self.state(root)["calls"])
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ADR-0001: unchanged, issue #1", done.stdout)
        self.assertFalse(self.writes(root, calls))

    def test_a_title_changed_in_the_record_only_updates_the_issue(self):
        """TSK-5321 criterion 2, REQ-4002: the record's change is applied to the issue where only it changed."""
        root = self.synced()
        self.retitle(root)
        calls = len(self.state(root)["calls"])
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "ADR-0001: Refuse a blank title")
        self.assertEqual([c[:4] for c in self.writes(root, calls)], [["api", "repos/o/r/issues/1", "-X", "PATCH"]])

    def test_where_both_sides_changed_the_record_wins(self):
        """TSK-5321 criterion 3, REQ-4002: a conflict is won by the file, and the issue holds the record's text."""
        root = self.synced()
        self.retitle(root)
        self.edit_issue(root, 1, title="ADR-0001: Reject an empty title")
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("both sides changed", done.stdout)
        self.assertEqual(self.state(root)["issues"]["1"]["title"], "ADR-0001: Refuse a blank title")
        self.assertIn("\n# Refuse a blank title\n", self.text(root))

    def test_an_approved_record_is_never_reworded_from_the_tracker(self):
        """TSK-5321 criterion 4, REQ-4002: the difference is printed, the file is not written, nothing is sent."""
        root = self.synced()
        before = self.text(root)
        self.edit_issue(root, 1, title="ADR-0001: Refuse a blank title")
        calls = len(self.state(root)["calls"])
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("never written", done.stdout)
        self.assertEqual(self.text(root), before)
        self.assertFalse(self.writes(root, calls))

    def test_an_issue_closed_on_the_tracker_is_reported_while_the_record_is_open(self):
        """REQ-3678: the record decides when its work is done, so a closed issue changes nothing in it."""
        root = self.synced()
        self.edit_issue(root, 1, state="closed")
        before = self.text(root)
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001: issue #1 is closed on GitHub while ADR-0001 isn't done", done.stdout)
        self.assertEqual(self.text(root), before)

    def test_a_done_record_agrees_with_a_closed_issue(self):
        """REQ-3678: the same closed issue is no finding once the record stores `done`."""
        root = self.synced()
        self.edit_issue(root, 1, state="closed")
        (root / RECORD).write_text(self.text(root).replace("status: approved", "status: done"), encoding="utf-8")
        done = self.run_tool(root, "sync")
        self.assertNotIn("isn't done", done.stdout)

    def test_a_draft_is_not_synchronised(self):
        """REQ-4002: a record maps to an issue once it is approved."""
        root = self.repository(status="draft")
        done = self.run_tool(root, "sync")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("ADR-0001 is draft, and it is synchronised only once it is approved", done.stdout)
        self.assertFalse((root / "state.json").exists())

    def test_check_writes_nothing(self):
        """REQ-4002: `--check` computes the difference on demand and changes neither side."""
        root = self.synced()
        self.retitle(root)
        before = self.text(root)
        calls = len(self.state(root)["calls"])
        done = self.run_tool(root, "sync", "--check")
        self.assertEqual(self.text(root), before)
        self.assertFalse(self.writes(root, calls))
        self.assertIn("(would)", done.stdout)


class Layered:
    """Runs `meow-github` against the stand-in above, with an injected clock and sleep."""

    def stand_in(self, root, script):
        (root / "bin").mkdir(exist_ok=True)
        (root / "bin" / "gh").write_text(LAYERED, encoding="utf-8")
        (root / "bin" / "gh").chmod(0o755)
        (root / "script.json").write_text(json.dumps(script), encoding="utf-8")
        (root / "clock").write_text(str(START), encoding="utf-8")

    def meow_github(self, root, *args, skew=0, credential=None):
        env = {**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}", "GH_STATE": str(root / "state.json"),
               "GH_SCRIPT": str(root / "script.json"), "MEOW_GITHUB_CLOCK": str(root / "clock"), "GH_SKEW": str(skew)}
        if credential is not None:
            # The variables that name the credential's form are set only as the check states, whatever the shell
            # running the checks, CI's included, carries.
            env = {k: v for k, v in env.items() if k not in ("GH_TOKEN", "GITHUB_TOKEN", "GITHUB_ACTIONS")}
            env.update(credential)
        return subprocess.run([str(BIN), *args], cwd=root, capture_output=True, text=True, env=env)

    def calls(self, root):
        path = root / "state.json"
        return json.loads(path.read_text(encoding="utf-8"))["calls"] if path.exists() else []

    def clock(self, root):
        return float((root / "clock").read_text(encoding="utf-8"))

    def throttled_line(self, done):
        lines = [line for line in done.stdout.splitlines() if "throttled" in line]
        self.assertTrue(lines, done.stdout + done.stderr)
        return lines[0]

    def retry_after(self, line):
        """The UTC time and the header a `throttled` line names, as `retry after <UTC time> (<header>)` states."""
        found = re.search(r"retry after (.+?) \(([^)]+)\)", line)
        self.assertTrue(found, line)
        for form in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S UTC", "%Y-%m-%dT%H:%M:%S+00:00", "%a, %d %b %Y %H:%M:%S GMT"):
            try:
                return calendar.timegm(time.strptime(found.group(1), form)), found.group(2).lower()
            except ValueError:
                continue
        self.fail(f"no UTC time in {line!r}")


def create(call):
    return call["args"][:2] == ["api", "repos/o/r/issues"] and "POST" in call["args"]


class Throttle(Layered, unittest.TestCase):
    """ADR-1810: a throttled `project` stops at the stated wait, or sleeps it under `--wait`, never past an hour."""

    def throttled_project(self, *answers):
        root = Project.repository(self)
        self.stand_in(root, {"responses": {"POST repos/o/r/issues": list(answers)}})
        return root

    def test_a_stated_wait_stops_the_run(self):
        """TSK-2940 criterion 1, REQ-2566: a 403 with `retry-after: 30` prints `throttled`, the method, the endpoint
        and the UTC time 30 seconds after the response, exits 3 and sends no further call."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        line = self.throttled_line(done)
        self.assertIn("POST repos/o/r/issues", line)
        self.assertEqual(self.retry_after(line), (START + 30, "retry-after"))
        calls = self.calls(root)
        self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
        self.assertTrue(create(calls[-1]), calls)

    def test_wait_resends_no_earlier_than_the_stated_time(self):
        """TSK-2940 criterion 2, REQ-2566: under `--wait` the refused call is sent again no earlier than the
        `retry-after` time, on the injected clock."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "ADR-0001", "o/r", "--wait")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        creates = [c for c in self.calls(root) if create(c)]
        self.assertGreaterEqual(len(creates), 2, creates)
        self.assertGreaterEqual(creates[1]["at"], creates[0]["at"] + 30, creates)

    def test_wait_stops_once_the_waits_would_pass_an_hour(self):
        """TSK-2940 criterion 3, REQ-2566: under `--wait`, 3,540 seconds are slept, and a second throttle of 120
        seconds, which would take the waits past an hour, starts no sleep and stops the run as throttled."""
        root = self.throttled_project({"status": 403, "headers": {"Retry-After": "3540"}, "body": SECONDARY},
                                      {"status": 403, "headers": {"Retry-After": "120"}, "body": SECONDARY})
        done = self.meow_github(root, "project", "ADR-0001", "o/r", "--wait")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.throttled_line(done)
        creates = [c for c in self.calls(root) if create(c)]
        self.assertEqual(len(creates), 2, creates)
        self.assertGreaterEqual(creates[1]["at"], START + 3540, creates)
        self.assertTrue(create(self.calls(root)[-1]), self.calls(root))
        self.assertGreaterEqual(self.clock(root), START + 3540)
        self.assertLess(self.clock(root), START + 3540 + 120, "a second sleep was started")

    def test_an_unparsed_wait_is_unknown_and_stops_the_run(self):
        """TSK-2940 criterion 5, REQ-2578: a `retry-after` that isn't a number of seconds gives an unknown wait, and
        the run sends no further call and exits 3, under `--wait` as without it, sleeping nothing."""
        for extra in ((), ("--wait",)):
            with self.subTest(extra=extra):
                root = self.throttled_project(
                    {"status": 403, "headers": {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}, "body": SECONDARY})
                done = self.meow_github(root, "project", "ADR-0001", "o/r", *extra)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                line = self.throttled_line(done)
                self.assertIn("POST repos/o/r/issues", line)
                self.assertIn("unknown", line)
                calls = self.calls(root)
                self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
                self.assertTrue(create(calls[-1]), calls)
                self.assertEqual(self.clock(root), START)


SINGLE_PAGES = {
    "repos/o/r/issues?state=all&per_page=100": [ISSUE, MERGED],
    "repos/o/r/pulls?state=all&per_page=100": [{"number": 2, "merged_at": "2026-01-01T00:00:00Z"}],
    "repos/o/r/issues/comments?per_page=100": [],
    "repos/o/r/pulls/comments?per_page=100": [],
}


class Limits(Layered, unittest.TestCase):
    """ADR-1810: the layer reads every response's limit headers, and never reads a replay's as current."""

    def history(self, script, skew=0):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.stand_in(root, {"listings": SINGLE_PAGES, **script})
        return root, self.meow_github(root, "history", "o/r", skew=skew)

    def test_a_response_with_no_limit_header_lets_the_run_go_on(self):
        """TSK-2940 criterion 6, REQ-2566: responses carrying no rate-limit header, read through `--include`, are
        taken as carrying none, not as a limit reached, and the run reads every listing."""
        root, done = self.history({"bare": True})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("throttled", done.stdout)
        self.assertEqual([i["number"] for i in json.loads(done.stdout)["issues"]], [1, 2])
        calls = self.calls(root)
        self.assertEqual(len(calls), 4, calls)
        for call in calls:
            self.assertIn("--include", call["args"], call)

    def test_a_stale_replay_is_not_read_as_current(self):
        """TSK-2940 criterion 7, REQ-2566: a cached response whose `Date` is ten minutes old carries
        `x-ratelimit-remaining: 0`; read as current it would hold the next read, so the run reading every listing
        shows its `remaining` wasn't taken as current."""
        root, done = self.history({"cached": {"age": 600, "remaining": 0, "reset_in": 1800}})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("throttled", done.stdout)
        self.assertEqual(json.loads(done.stdout)["repository"], "o/r")
        calls = self.calls(root)
        self.assertEqual(len(calls), 4, calls)
        self.assertNotIn("--cache", calls[0]["args"], calls[0])
        for call in calls:
            self.assertIn("--include", call["args"], call)
        for call in calls[1:]:
            self.assertIn("--cache", call["args"], call)

    def test_a_skewed_clock_leaves_a_fresh_response_current(self):
        """TSK-2940 criterion 7, REQ-2566: with the local clock two minutes ahead of the stand-in's `Date`, a fresh
        cached response is current, so its `remaining: 0` holds the next read to the same resource and the run
        stops as throttled at the reset; the run's first call carries no `--cache`."""
        root, done = self.history({"cached": {"age": 0, "remaining": 0, "reset_in": 1800}}, skew=120)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        line = self.throttled_line(done)
        self.assertIn("GET repos/o/r/issues/comments?per_page=100", line)
        self.assertEqual(self.retry_after(line), (START - 120 + 1800, "x-ratelimit-reset"))
        calls = self.calls(root)
        self.assertEqual(len(calls), 2, calls)
        self.assertNotIn("--cache", calls[0]["args"], calls[0])
        self.assertIn("--cache", calls[1]["args"], calls[1])


# ADR-1810, SPC-1080 "The GitHub request layer": the four counts the layer keeps, named on a report's last lines.
COUNTS = ("primary requests", "secondary points", "content creation", "spacing")
FORMS = {"GH_TOKEN": "GH_TOKEN from the environment", "GITHUB_TOKEN": "GITHUB_TOKEN from the environment",
         None: "gh's stored credential"}
ACTIONS = ", inside a GitHub Actions workflow"
# A token value no check's output may carry. It is shaped like no real token, so a kept run carrying it by mistake
# trips no secret scan.
SENTINEL = "meow-sentinel-6d1f0b7e"


# The open pull requests `meow-github upgrade` reads.
OPEN_PULLS = "repos/o/r/pulls?state=open&per_page=100"


def many_folded(test, count):
    """A repository whose archive holds `count` open tasks with no issue, each folded into a decision of its own
    with no issue yet, so `meow-github upgrade` creates `count` issues in one run."""
    root = Project.repository(test)
    (root / RECORD).unlink()
    tasks = root / "project" / "archive" / "tasks"
    tasks.mkdir(parents=True)
    for n in range(1, count + 1):
        (root / "project" / "adrs" / f"ADR-{n:04d}-a-choice.md").write_text(
            DECISION.format(status="approved").replace("ADR-0001", f"ADR-{n:04d}"), encoding="utf-8")
        (tasks / f"TSK-{n:04d}-task.md").write_text(archived(f"TSK-{n:04d}", "approved", "", f"ADR-{n:04d}"), encoding="utf-8")
    return root


def archived(ident, status, issue, folded=""):
    """An archived task as `paw upgrade` leaves it."""
    lines = ["---", f"id: {ident}", "artifact: task", f"status: {status}", "revised: 2026-01-01"]
    lines += [f"issue: {issue}"] if issue else []
    lines += [f"folded-into: {folded}"] if folded else []
    return "\n".join(lines + ["---", "", f"# {ident}", ""])


class Budgets(Layered, unittest.TestCase):
    """ADR-1810: the layer keeps the four counts, spaces the writes, and stops before a request past a ceiling."""

    run_of_501 = None

    def five_hundred_and_one(self):
        """One `upgrade` run creating the issues of 501 decisions, shared by the checks that read it: its result and
        the calls the stand-in recorded, read before the first check's repository is removed."""
        if Budgets.run_of_501 is None:
            root = many_folded(self, 501)
            self.stand_in(root, {"listings": {OPEN_PULLS: []}})
            done = self.meow_github(root, "upgrade", "o/r", credential={})
            Budgets.run_of_501 = (done, self.calls(root))
        return Budgets.run_of_501

    def test_content_creation_stops_the_run_at_500_an_hour(self):
        """TSK-2950 criterion 1, REQ-2568: with 501 unmapped decisions the stand-in records 500 creates, and the run
        stops before the 501st, naming content creation at 500 of 500 this hour, and exits 3."""
        done, calls = self.five_hundred_and_one()
        self.assertEqual(done.returncode, 3, done.stdout[-2000:] + done.stderr)
        self.assertEqual(len([c for c in calls if create(c)]), 500, done.stdout[-2000:])
        self.assertIn("(content creation: 500 of 500 this hour)", self.throttled_line(done))

    def test_writes_are_a_second_apart(self):
        """TSK-2950 criterion 2, REQ-2568: in the same run, every write the stand-in records is at least one second
        after the previous one, on the injected clock."""
        done, calls = self.five_hundred_and_one()
        writes = [c for c in calls if "-X" in c["args"] or any(a.startswith("--method") for a in c["args"])]
        self.assertGreater(len(writes), 1, done.stdout[-2000:])
        close = [(a["at"], b["at"]) for a, b in zip(writes, writes[1:]) if b["at"] - a["at"] < 1]
        self.assertEqual(len(close), 0, f"writes less than a second after the previous one, the first {close[:1]}")

    def test_the_budget_lines_name_the_four_counts(self):
        """TSK-2950 criterion 3, REQ-2568: with `x-ratelimit-limit: 1000` and `GITHUB_ACTIONS=true`, the last lines
        of `project`'s report name primary requests with 1,000 as the limit, read from the header and never assumed
        from the credential's form, then secondary points, content creation and spacing."""
        # 1234 is a limit no credential's form implies, so a limit assumed from the form can't pass for one read.
        for limit, shown in (("1000", "1,000"), ("1234", "1,234")):
            with self.subTest(limit=limit):
                root = Project.repository(self)
                self.stand_in(root, {"headers": {"X-Ratelimit-Limit": limit}})
                done = self.meow_github(root, "project", "ADR-0001", "o/r", credential={"GITHUB_ACTIONS": "true"})
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                tail = done.stdout.splitlines()[-len(COUNTS):]
                self.assertEqual([line.split(":")[0] for line in tail], list(COUNTS), tail)
                creates = len([c for c in self.calls(root) if create(c)])
                reads = len(self.calls(root)) - creates
                self.assertGreater(creates, 0)
                self.assertGreater(reads, 0)
                self.assertTrue(tail[0].startswith(
                    f"primary requests: {creates + reads} sent; core limit {shown}, 4,990 remaining, resets "), tail)
                self.assertEqual(tail[1:], [
                    f"secondary points: {reads + 5 * creates} of 900 this minute",
                    f"content creation: {creates} of 80 this minute, {creates} of 500 this hour",
                    f"spacing: {creates} write, each at least one second after the previous one"])


def groups(test, done):
    """The three groups of the one `partial:` line a report holds, each as the text after its name."""
    lines = [line for line in done.stdout.splitlines() if line.startswith("partial: ")]
    test.assertEqual(len(lines), 1, done.stdout + done.stderr)
    found = re.fullmatch(r"partial: projected (.+); created, not read back (.+); not projected (.+)", lines[0])
    test.assertTrue(found, lines[0])
    return found.groups()


def listings(calls):
    """The read-back listings among the recorded calls, each as the `since` it carries."""
    sent = [re.match(LISTING, call["args"][1]) for call in calls if call["args"][0] == "api"]
    return [found.group(1) for found in sent if found]


class Partial(Layered, unittest.TestCase):
    """ADR-1810: a created issue is read back in one listing, and a run that stops part way says what it did."""

    REFUSED = {"status": 422, "body": {"message": "Validation Failed"}}

    def run_project(self, script, skew=0):
        root = Project.repository(self)
        self.stand_in(root, script)
        return root, self.meow_github(root, "project", "ADR-0001", "o/r", skew=skew)

    def test_a_failed_write_reports_partial(self):
        """TSK-2960 criterion 1, REQ-2572: with the create failing, `project` has nothing to read back, names the
        record as not projected, and exits 3."""
        root, done = self.run_project({"responses": {"POST repos/o/r/issues": [self.REFUSED]}})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
        self.assertEqual(listings(calls), [], calls)
        self.assertEqual(groups(self, done), ("none", "none", "ADR-0001"))

    def test_the_listing_starts_at_githubs_date(self):
        """TSK-2960 criterion 2, REQ-2572: with the local clock two minutes ahead of the stand-in's `Date`, the
        listing's `since` is the `Date` of the run's first response, and the created issue is read back. The
        stand-in lists only the issues written at or after `since`, so a `since` taken from the local clock reads
        nothing back. Its create answer carries no `updated_at`, so the start comes from the `Date` (ADR-2320)."""
        root, done = self.run_project({"no_updated_at": True}, skew=120)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        first = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(START - 120))
        self.assertEqual(listings(self.calls(root)), [first])
        self.assertRegex(done.stdout, r"(?m)^ADR-0001: projected to issue #1 at [0-9a-f]{12}, read back$")

    def test_a_throttle_sends_no_listing(self):
        """TSK-2960 criterion 3, REQ-2572: with the create answered by a secondary throttle, `project` sends no
        listing, names the record as not projected, and exits 3."""
        throttle = {"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY}
        root, done = self.run_project({"responses": {"POST repos/o/r/issues": [throttle]}})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(listings(calls), [])
        self.assertTrue(create(calls[-1]), calls)
        self.assertEqual(groups(self, done), ("none", "none", "ADR-0001"))

    def test_an_issue_the_listing_omits_is_not_read_back(self):
        """TSK-2960 criterion 4 and TSK-4040 criterion 2, REQ-2572, REQ-3322: where the listing shows a created issue
        with another body or another title, or omits it and its read by number shows another body, its record goes
        under `created, not read back` with the reason, and the record keeps `issue:`."""
        shown = (({"omit": [1], "read_alter": [1]}, "reads differently from what was written"),
                 ({"omit": [1], "read_retitle": [1]}, "reads differently from what was written"),
                 ({"alter": [1]}, "reads differently from what was written"),
                 ({"retitle": [1]}, "reads differently from what was written"))
        for script, reason in shown:
            with self.subTest(script=script):
                root, done = self.run_project(script)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertEqual(len(listings(self.calls(root))), 1)
                self.assertEqual(groups(self, done), ("none", f"ADR-0001 (issue #1, {reason})", "none"))
                self.assertIn("\nissue: 1\n", Project.text(self, root))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root writes a read-only file")
    def test_an_updated_issue_is_projected_though_its_record_file_is_not_written(self):
        """TSK-2960, REQ-2572: a mapped record whose issue was updated counts as projected where its file then can't
        be written, because its issue was updated, and the run exits 1 and prints no `partial:` line."""
        root = Project.repository(self)
        self.stand_in(root, {})
        first = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        Project.retitle(self, root)
        (root / RECORD).chmod(0o444)
        done = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("ADR-0001: issue #1 updated, and the mapping couldn't be written", done.stdout)
        self.assertEqual([line for line in done.stdout.splitlines() if line.startswith("partial:")], [])

    def test_a_created_issue_is_read_back_from_every_page_of_one_listing(self):
        """TSK-2960 criterion 5, REQ-2572: with a second decision created in the same second as the first and the
        listing answering one issue a page, the stand-in records one read-back listing of two pages and no read of a
        single created issue, and the report holds no `partial:` line, so a run reading only the first page fails."""
        root = Project.repository(self)
        (root / "project" / "adrs" / "ADR-0002-another.md").write_text(
            DECISION.format(status="approved").replace("ADR-0001", "ADR-0002"), encoding="utf-8")
        self.stand_in(root, {"page_size": 1})
        first = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.stand_in(root, {"page_size": 1})
        before = len(self.calls(root))
        done = self.meow_github(root, "project", "ADR-0002", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.calls(root)[before:]
        self.assertEqual(len([c for c in calls if create(c)]), 1, calls)
        self.assertEqual(len(listings(calls)), 1, calls)
        pages = [c["args"][1] for c in calls if "issues?state=all&since=" in c["args"][1]]
        self.assertEqual(len(pages), 2, calls)
        self.assertTrue(pages[1].endswith("&per_page=100&page=2"), pages)
        self.assertEqual([c for c in calls if re.fullmatch(r"repos/o/r/issues/\d+", c["args"][1])], [], calls)
        self.assertEqual([line for line in done.stdout.splitlines() if line.startswith("partial:")], [])
        self.assertEqual(len([line for line in done.stdout.splitlines() if line.endswith(", read back")]), 1, done.stdout)


class ReadBack(Layered, unittest.TestCase):
    """ADR-2340: a created issue the read-back listing leaves out is read by its number before it is reported."""

    def test_an_issue_the_listing_leaves_out_is_read_by_number(self):
        """TSK-4040 criterion 1, REQ-3322: with the created issue left out of the listing and answered by number, the
        record reads back, one read by number is sent, no `partial:` line is printed, and the run exits 0."""
        root = Project.repository(self)
        self.stand_in(root, {"omit": [1]})
        done = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.splitlines()
        self.assertEqual(len([line for line in lines if line.startswith("ADR-0001: projected to issue #1 at ")
                              and line.endswith(", read back")]), 1, done.stdout)
        reads = [c["args"][1] for c in self.calls(root) if re.fullmatch(r"repos/o/r/issues/\d+", c["args"][1])]
        self.assertEqual(reads, ["repos/o/r/issues/1"])
        self.assertEqual([line for line in lines if line.startswith("partial:")], [])

    def test_the_listing_starts_at_the_issues_own_time(self):
        """TSK-4020 criterion 1, REQ-3322: with the issue written two seconds before its create's answer and the
        repository named, the listing starts at its `updated_at`, finds it with no read by number, and the run
        exits 0. A start at the first response's `Date` misses the issue and reads it by number."""
        root = Project.repository(self)
        self.stand_in(root, {"lag": [2]})
        done = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        calls = self.calls(root)
        self.assertEqual(listings(calls), [time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(START - 2))])
        self.assertEqual([c for c in calls if re.fullmatch(r"repos/o/r/issues/\d+", c["args"][1])], [])
        self.assertEqual([line for line in done.stdout.splitlines() if line.startswith("partial:")], [])

    def test_with_no_updated_at_the_listing_starts_at_the_first_date(self):
        """TSK-4020 criterion 2, REQ-3322: where no create's answer carries `updated_at`, the listing starts at the
        `Date` of the run's first response, on GitHub's clock: the local clock runs two minutes ahead of the
        stand-in's, so a start taken from the local clock fails."""
        root = Project.repository(self)
        self.stand_in(root, {"lag": 1, "no_updated_at": True})
        done = self.meow_github(root, "project", "ADR-0001", "o/r", skew=120)
        self.assertEqual(listings(self.calls(root)),
                         [time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(START - 120))], done.stdout + done.stderr)

    def test_a_failed_read_by_number_leaves_the_issue_unread(self):
        """TSK-4040 criterion 4, REQ-3322, REQ-3326: with the created issue left out of the listing, a secondary
        throttle or a 401 answering the read by number leaves it under `created, not read back` with `no read ran`,
        and any other failure with `couldn't be read`. Each run sends no request after it and exits 3."""
        throttle = {"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY}
        rejected = {"status": 401, "body": {"message": "Bad credentials"}}
        failed = {"status": 422, "body": {"message": "Unprocessable"}}
        stopped = ("none", "ADR-0001 (issue #1, no read ran)", "none")
        for answer, expected in ((throttle, stopped), (rejected, stopped),
                                 (failed, ("none", "ADR-0001 (issue #1, couldn't be read)", "none"))):
            with self.subTest(status=answer["status"]):
                root = Project.repository(self)
                self.stand_in(root, {"omit": [1], "responses": {"GET repos/o/r/issues/1": [answer]}})
                done = self.meow_github(root, "project", "ADR-0001", "o/r")
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertEqual(self.calls(root)[-1]["args"][1], "repos/o/r/issues/1")
                self.assertEqual(groups(self, done), expected)


class Refusal(Layered, unittest.TestCase):
    """ADR-1810: a refused call is reported with its method, its endpoint and the permission GitHub named."""

    def refused_create(self, status, headers, message):
        """A `project` run whose first create is answered with `status`, `headers` and `message`, as its result
        and the lines it printed."""
        root = Project.repository(self)
        answer = {"status": status, "headers": headers, "body": {"message": message}}
        self.stand_in(root, {"responses": {"POST repos/o/r/issues": [answer]}})
        done = self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertNotIn("throttled", done.stdout)
        self.assertEqual(len([c for c in self.calls(root) if create(c)]), 1)
        return done.stdout.splitlines()

    def test_a_403_names_the_github_permission(self):
        """TSK-2970 criterion 1, REQ-2574: a create answered 403 with `X-Accepted-GitHub-Permissions: issues=write`
        prints `refused: POST repos/o/r/issues needs issues=write` and exits 3. The answer also carries the scope
        headers, so a layer that tries the scopes first fails."""
        lines = self.refused_create(403, {"X-Accepted-GitHub-Permissions": "issues=write",
                                          "X-Accepted-OAuth-Scopes": "repo", "X-OAuth-Scopes": "gist"},
                                    "Resource not accessible by personal access token")
        # TSK-4030 criterion 1, REQ-3324: the line ends with GitHub's own reason.
        self.assertEqual(lines.count('refused: POST repos/o/r/issues needs issues=write; GitHub said '
                                     '"Resource not accessible by personal access token"'), 1, lines)

    def test_a_403_names_the_oauth_scopes(self):
        """TSK-2970 criterion 2, REQ-2574: a 403 carrying only `X-Accepted-OAuth-Scopes` and `X-OAuth-Scopes` names
        the accepted scopes and the credential's own, and `none` where the credential states no scope."""
        for own, holds in (("read:org, gist", "read:org, gist"), (None, "none")):
            with self.subTest(own=own):
                headers = {"X-Accepted-OAuth-Scopes": "repo", **({"X-OAuth-Scopes": own} if own else {})}
                lines = self.refused_create(403, headers, "Must have admin rights to Repository.")
                self.assertEqual(lines.count(
                    f"refused: POST repos/o/r/issues needs one of the scopes repo; the credential holds {holds}; "
                    'GitHub said "Must have admin rights to Repository."'), 1, lines)

    def test_a_403_naming_nothing_quotes_github(self):
        """TSK-2970 criterion 3 and TSK-4030 criterion 4, REQ-2574, REQ-3324: a 403 carrying neither header says
        `GitHub named no permission` and quotes GitHub's message once, with no second quotation after it."""
        lines = self.refused_create(403, {}, "Must have admin rights to Repository.")
        self.assertEqual(lines.count(
            'refused: POST repos/o/r/issues needs a permission: GitHub named no permission and said '
            '"Must have admin rights to Repository."'), 1, lines)

    def test_a_404_on_a_mapped_issue_may_be_hidden(self):
        """TSK-2970 criterion 4, REQ-2574: a 404 on a record's mapped issue is reported as a refusal, with
        `, or it is hidden from this credential` added, and the run exits 3, whether the read of the issue or
        the update of a changed record's issue gets it."""
        for call in ("GET", "PATCH"):
            with self.subTest(call=call):
                root = Project.repository(self)
                self.stand_in(root, {})
                first = self.meow_github(root, "project", "ADR-0001", "o/r")
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                if call == "PATCH":
                    Project.retitle(self, root)
                missing = {"status": 404, "body": {"message": "Not Found"}}
                self.stand_in(root, {"responses": {f"{call} repos/o/r/issues/1": [missing]}})
                done = self.meow_github(root, "project", "ADR-0001", "o/r")
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertEqual(done.stdout.splitlines().count(
                    f'refused: {call} repos/o/r/issues/1 needs a permission: GitHub named no permission and said '
                    '"Not Found", or it is hidden from this credential'), 1, done.stdout)

    def test_a_404_on_an_unmapped_object_is_no_refusal(self):
        """TSK-2970, REQ-2574: a 404 on a create, which names no object the record maps, stays as GitHub's answer
        and is reported as no refusal."""
        lines = self.refused_create(404, {}, "Not Found")
        self.assertEqual([line for line in lines if line.startswith("refused:")], [], lines)
        self.assertEqual(lines.count("ADR-0001: not projected: repos/o/r/issues: HTTP 404: Not Found"), 1, lines)

    def test_a_401_is_unauthenticated(self):
        """TSK-2970 criterion 5 and TSK-4030 criterion 2, REQ-2574, REQ-3324: a 401 prints
        `unauthenticated: <method> <endpoint>; GitHub said "<message>"` and exits 3."""
        lines = self.refused_create(401, {}, "Bad credentials")
        # TSK-4030 criterion 2, REQ-3324.
        self.assertEqual(lines.count('unauthenticated: POST repos/o/r/issues; GitHub said "Bad credentials"'), 1, lines)

    def test_a_401_ends_the_run(self):
        """TSK-4030 criterion 3, REQ-3326: a 401 is the last request the run sends, wherever it lands: the read of a
        mapped issue, the update of a changed one, a create, or the read-back listing. The run prints the `partial:`
        line with the record in the group the stop leaves it in, and exits 3."""
        rejected = {"status": 401, "body": {"message": "Bad credentials"}}
        since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(START))
        listing = f"repos/o/r/issues?state=all&since={since}&per_page=100"
        cases = (
            ("read", True, {"GET repos/o/r/issues/1": [rejected]}, ["repos/o/r/issues/1"],
             ("none", "none", "ADR-0001")),
            ("update", True, {"PATCH repos/o/r/issues/1": [rejected]}, ["repos/o/r/issues/1"] * 2,
             ("none", "none", "ADR-0001")),
            ("create", False, {"POST repos/o/r/issues": [rejected]}, ["repos/o/r/issues"],
             ("none", "none", "ADR-0001")),
            ("listing", False, {f"GET {listing}": [rejected]}, ["repos/o/r/issues", listing],
             ("none", "ADR-0001 (issue #1, the listing's credential was rejected)", "none")),
        )
        for where, mapped, responses, every, expected in cases:
            with self.subTest(where=where):
                root = Project.repository(self)
                self.stand_in(root, {})
                if mapped:
                    first = self.meow_github(root, "project", "ADR-0001", "o/r")
                    self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                    if where == "update":
                        Project.retitle(self, root)
                before = len(self.calls(root))
                self.stand_in(root, {"responses": responses})
                done = self.meow_github(root, "project", "ADR-0001", "o/r")
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                sent = [call["args"][1] for call in self.calls(root)[before:]]
                self.assertEqual(sent, every)
                self.assertEqual(len([line for line in done.stdout.splitlines()
                                      if line.startswith("unauthenticated: ")
                                      and line.endswith('; GitHub said "Bad credentials"')]), 1, done.stdout)
                self.assertEqual(groups(self, done), expected)

    def test_history_reports_a_refusal_as_unread(self):
        """TSK-2970, REQ-2574: `history` reports a refused listing as unread, naming the listing, with the same
        permission text, and prints no document."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        refused = {"status": 403, "headers": {"X-Accepted-GitHub-Permissions": "pull_requests=read"},
                   "body": {"message": "Resource not accessible by personal access token"}}
        self.stand_in(root, {"listings": SINGLE_PAGES,
                             "responses": {"GET repos/o/r/pulls?state=all&per_page=100": [refused]}})
        done = self.meow_github(root, "history", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual(done.stdout.splitlines().count(
            "meow-github history: unread: pull requests: refused: GET repos/o/r/pulls?state=all&per_page=100 "
            'needs pull_requests=read; GitHub said "Resource not accessible by personal access token"'), 1, done.stdout)
        self.assertNotIn('"issues"', done.stdout)


class Credential(Layered, unittest.TestCase):
    """ADR-1810: every run names the credential's form, read from whether a variable is set, never its value."""

    def test_the_first_line_names_the_form(self):
        """TSK-2950 criterion 4, REQ-2582: `GH_TOKEN` set, then only `GITHUB_TOKEN` set, then neither, name
        `GH_TOKEN from the environment`, `GITHUB_TOKEN from the environment` and `gh's stored credential` on the
        first line of `project`'s report, `GH_TOKEN` winning where both are set, and `GITHUB_ACTIONS=true` adds
        `, inside a GitHub Actions workflow`."""
        cases = (({"GH_TOKEN": "x"}, FORMS["GH_TOKEN"]), ({"GH_TOKEN": "x", "GITHUB_TOKEN": "y"}, FORMS["GH_TOKEN"]),
                 ({"GITHUB_TOKEN": "y"}, FORMS["GITHUB_TOKEN"]), ({}, FORMS[None]))
        for variables, form in cases:
            for actions in (False, True):
                with self.subTest(variables=sorted(variables), actions=actions):
                    root = Project.repository(self)
                    self.stand_in(root, {})
                    credential = dict(variables, **({"GITHUB_ACTIONS": "true"} if actions else {}))
                    done = self.meow_github(root, "project", "ADR-0001", "o/r", credential=credential)
                    first = (done.stdout.splitlines() or [""])[0]
                    self.assertIn(form + (ACTIONS if actions else ""), first, done.stdout + done.stderr)
                    if not actions:
                        self.assertNotIn("GitHub Actions", first)

    def test_the_token_value_is_never_printed(self):
        """TSK-2950 criterion 5, REQ-2582: a sentinel value in `GH_TOKEN` or `GITHUB_TOKEN` appears nowhere in the
        standard output or standard error of `project` or `history`. Each run is also read for the form it names,
        on `project`'s first line and in `history`'s `credential`, so the output that could carry the value is
        there to be read and a run naming no credential doesn't pass for one that keeps it out."""
        for variable in ("GH_TOKEN", "GITHUB_TOKEN"):
            for command in ("project", "history"):
                with self.subTest(variable=variable, command=command):
                    root = Project.repository(self)
                    self.stand_in(root, {"listings": SINGLE_PAGES})
                    args = ("project", "ADR-0001", "o/r") if command == "project" else ("history", "o/r")
                    done = self.meow_github(root, *args, credential={variable: SENTINEL})
                    self.assertNotIn(SENTINEL, done.stdout, "the token's value is on standard output")
                    self.assertNotIn(SENTINEL, done.stderr, "the token's value is on standard error")
                    if command == "project":
                        self.assertIn(FORMS[variable], (done.stdout.splitlines() or [""])[0], done.stdout)
                    else:
                        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                        self.assertEqual(json.loads(done.stdout).get("credential"), FORMS[variable], done.stdout)


class Upgrade(Layered, unittest.TestCase):
    """ADR-3090 "Open tasks and issues": `meow-github upgrade` retires the issues of archived tasks, one row each."""

    def repository(self, tasks, issues, pulls=()):
        """A record whose archive holds `tasks`, each `(id, status, issue, folded-into)`, on a tracker holding
        `issues`, each `(number, state)` and numbered from 1, and one approved decision with no issue yet."""
        root = Project.repository(self)
        directory = root / "project" / "archive" / "tasks"
        directory.mkdir(parents=True)
        for ident, status, issue, folded in tasks:
            (directory / f"{ident}-a-task.md").write_text(archived(ident, status, issue, folded), encoding="utf-8")
        state = {"issues": {str(n): {"number": n, "title": f"Issue {n}", "body": "The old body.", "state": s,
                                     "written": START} for n, s in issues},
                 "calls": [], "used": {}}
        (root / "state.json").write_text(json.dumps(state), encoding="utf-8")
        self.stand_in(root, {"listings": {OPEN_PULLS: list(pulls)}})
        return root

    def issue(self, root, number):
        return json.loads((root / "state.json").read_text(encoding="utf-8"))["issues"][str(number)]

    def writes(self, root):
        return [c["args"] for c in self.calls(root) if "-X" in c["args"]]

    def test_a_done_task_closes_its_open_issue_as_completed(self):
        """Row 1: the notice and the state land in one call, above the issue's own body."""
        root = self.repository([("TSK-0001", "done", "1", "")], [(1, "open")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issue = self.issue(root, 1)
        self.assertEqual((issue["state"], issue["state_reason"]), ("closed", "completed"))
        self.assertTrue(issue["body"].startswith("TSK-0001 is done and archived (ADR-3090)."), issue["body"])
        self.assertTrue(issue["body"].endswith("The old body."), issue["body"])
        self.assertEqual(len(self.writes(root)), 1, self.writes(root))
        self.assertIn("TSK-0001: closed issue #1 as completed", done.stdout)

    def test_a_dropped_task_closes_its_open_issue_as_not_planned(self):
        """Row 2: withdrawn, rejected and superseded all read as work nobody did."""
        for status in ("withdrawn", "rejected", "superseded"):
            with self.subTest(status=status):
                root = self.repository([("TSK-0001", status, "1", "")], [(1, "open")])
                done = self.meow_github(root, "upgrade", "o/r")
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                issue = self.issue(root, 1)
                self.assertEqual((issue["state"], issue["state_reason"]), ("closed", "not_planned"))
                self.assertIn("TSK-0001 was dropped and is archived", issue["body"])

    def test_a_folded_task_creates_its_carriers_issue_first_and_names_it(self):
        """Row 3: the carrier's issue is created before the closing call, whose body names it as `ADR-x (#n)`."""
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001")], [(1, "open")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        writes = self.writes(root)
        self.assertEqual([(w[1], w[w.index("-X") + 1]) for w in writes],
                         [("repos/o/r/issues", "POST"), ("repos/o/r/issues/1", "PATCH")], writes)
        self.assertIn("\nissue: 2\n", Project.text(self, root))
        issue = self.issue(root, 1)
        self.assertEqual((issue["state"], issue["state_reason"]), ("closed", "not_planned"))
        self.assertIn("ADR-0001 (#2) carries its work", issue["body"])

    def test_a_folded_task_finds_the_issue_its_carrier_already_has(self):
        """Row 3: a carrier with an issue keeps it, so no second one opens."""
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001")], [(1, "open")])
        self.meow_github(root, "project", "ADR-0001", "o/r")
        self.assertEqual(self.issue(root, 2)["state"], "open")
        before = len(self.writes(root))
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        writes = self.writes(root)[before:]
        self.assertEqual([w[w.index("-X") + 1] for w in writes], ["PATCH"], writes)
        self.assertIn("ADR-0001 (#2) carries its work", self.issue(root, 1)["body"])

    def test_an_orphan_is_left_open_and_reported(self):
        """Row 4: nothing authorises the work, so nothing writes to its issue, and the run exits 1."""
        root = self.repository([("TSK-0001", "approved", "1", "")], [(1, "open")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.writes(root), [])
        self.assertEqual(self.issue(root, 1)["state"], "open")
        self.assertIn("TSK-0001: issue #1 is left as it is, and TSK-0001 needs a decision", done.stdout)

    def test_a_closed_issue_gets_no_write(self):
        """The table's right column: a closed issue is left alone, and a folded task and an orphan are reported."""
        root = self.repository([("TSK-0001", "done", "1", ""), ("TSK-0002", "withdrawn", "2", ""),
                                ("TSK-0003", "approved", "3", "ADR-0001"), ("TSK-0004", "approved", "4", "")],
                               [(1, "closed"), (2, "closed"), (3, "closed"), (4, "closed")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        closing = [w for w in self.writes(root) if w[1] != "repos/o/r/issues"]
        self.assertEqual(closing, [])
        for number in (1, 2, 3, 4):
            self.assertEqual(self.issue(root, number)["body"], "The old body.")
        self.assertIn("TSK-0003: issue #3 is closed, and ADR-0001 carries the work", done.stdout)
        self.assertIn("TSK-0004: issue #4 is left as it is, and TSK-0004 needs a decision", done.stdout)

    def test_an_issue_no_archived_task_maps_gets_no_call(self):
        """ADR-3090: it is the repository's own, so it is never read, let alone written."""
        root = self.repository([("TSK-0001", "done", "1", "")], [(1, "open"), (2, "open")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual([c["args"] for c in self.calls(root) if c["args"][1] == "repos/o/r/issues/2"], [])
        self.assertEqual(self.issue(root, 2), {"number": 2, "title": "Issue 2", "body": "The old body.",
                                               "state": "open", "written": START})

    def test_check_reports_each_row_and_writes_nothing(self):
        """ADR-3090: `--check` previews the table with no write, and leaves the record as it is."""
        root = self.repository([("TSK-0001", "done", "1", ""), ("TSK-0002", "withdrawn", "2", ""),
                                ("TSK-0003", "approved", "3", "ADR-0001"), ("TSK-0004", "approved", "4", "")],
                               [(1, "open"), (2, "open"), (3, "open"), (4, "open")])
        before = Project.text(self, root)
        done = self.meow_github(root, "upgrade", "--check", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.writes(root), [])
        self.assertEqual(Project.text(self, root), before)
        self.assertIn("TSK-0001: would close issue #1 as completed", done.stdout)
        self.assertIn("TSK-0002: would close issue #2 as not_planned", done.stdout)
        self.assertIn("TSK-0003: would close issue #3 as not_planned", done.stdout)
        self.assertIn("ADR-0001: not projected yet", done.stdout)
        self.assertIn("TSK-0004: issue #4 is left as it is", done.stdout)

    def test_an_open_pull_request_naming_a_folded_task_is_reported_and_left(self):
        """ADR-3090: a branch in flight is somebody's work, so it is listed, and no call writes to it."""
        pulls = ({"number": 9, "title": "Finish TSK-0001", "body": ""}, {"number": 8, "title": "Other", "body": "It names TSK-0002."},
                 {"number": 7, "title": "Unrelated", "body": None})
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001"), ("TSK-0002", "done", "2", "")],
                               [(1, "open"), (2, "open")], pulls)
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("pull request #9 names TSK-0001, which is folded", done.stdout)
        self.assertNotIn("pull request #8", done.stdout)
        self.assertNotIn("pull request #7", done.stdout)
        self.assertEqual([w for w in self.writes(root) if "/pulls" in w[1]], [])

    def test_an_issue_a_live_record_owns_gets_no_write(self):
        """ADR-3090: a defect's issue stays its issue, so an archived task sharing it changes nothing."""
        root = self.repository([("TSK-0001", "done", "1", "")], [(1, "open")])
        Project.defect(self, root)
        path = root / "project" / "bugs" / "BUG-0001-a-defect.md"
        path.write_text(path.read_text(encoding="utf-8").replace("issue:\n", "issue: 1\n"), encoding="utf-8")
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.writes(root), [])
        self.assertEqual(self.issue(root, 1)["state"], "open")
        self.assertIn("TSK-0001: issue #1 is BUG-0001's own", done.stdout)

    def test_the_least_finished_task_decides_a_shared_issue(self):
        """ADR-3090: a done task beside an orphan leaves the issue open with no write, and beside a folded task
        closes it as not planned, because work nobody did never reads as done."""
        orphaned = self.repository([("TSK-0001", "done", "1", ""), ("TSK-0002", "approved", "1", "")], [(1, "open")])
        done = self.meow_github(orphaned, "upgrade", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.writes(orphaned), [])
        self.assertEqual(self.issue(orphaned, 1)["state"], "open")
        self.assertIn("TSK-0002 needs a decision", done.stdout)
        folded = self.repository([("TSK-0001", "done", "1", ""), ("TSK-0002", "approved", "1", "ADR-0001")], [(1, "open")])
        done = self.meow_github(folded, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        issue = self.issue(folded, 1)
        self.assertEqual((issue["state"], issue["state_reason"]), ("closed", "not_planned"))
        self.assertIn("TSK-0002 is archived, and ADR-0001 (#2) carries its work", issue["body"])

    def test_a_folded_task_whose_carrier_is_a_draft_gets_no_write(self):
        """ADR-3090: a draft carrier gets no issue, so the closing notice would name nothing and the issue stays."""
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001")], [(1, "open")])
        path = root / RECORD
        path.write_text(path.read_text(encoding="utf-8").replace("status: approved", "status: draft"), encoding="utf-8")
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.writes(root), [])
        self.assertEqual(self.issue(root, 1)["state"], "open")
        self.assertIn("TSK-0001: issue #1 is left open, because ADR-0001 has no issue to name", done.stdout)

    def test_a_throttled_carrier_create_stops_the_run(self):
        """ADR-1810, ADR-3090: where the carrier's issue can't be created the run stops, and no issue is closed."""
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001"), ("TSK-0002", "done", "2", "")],
                               [(1, "open"), (2, "open")])
        throttle = {"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY}
        self.stand_in(root, {"listings": {OPEN_PULLS: []}, "responses": {"POST repos/o/r/issues": [throttle]}})
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual([w for w in self.writes(root) if "PATCH" in w], [])
        self.assertIn("ADR-0001 has no issue yet, so nothing is closed", done.stdout)

    def test_open_pull_requests_on_a_second_page_are_reported(self):
        """ADR-3090: every page of the listing is read, so a repository with many open pull requests hides none."""
        following = f"https://api.github.com/{OPEN_PULLS}&page=2"
        root = self.repository([("TSK-0001", "approved", "1", "ADR-0001")], [(1, "open")])
        first = {"status": 200, "body": [{"number": 6, "title": "Other", "body": ""}],
                 "headers": {"Link": f'<{following}>; rel="next"'}}
        self.stand_in(root, {"listings": {f"{OPEN_PULLS}&page=2": [{"number": 5, "title": "Finish TSK-0001", "body": ""}]},
                             "responses": {f"GET {OPEN_PULLS}": [first]}})
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("pull request #5 names TSK-0001, which is folded", done.stdout)

    def test_a_throttled_pull_request_listing_stops_the_run(self):
        """ADR-1810: a throttled listing sends nothing after it, so no issue is read or closed."""
        root = self.repository([("TSK-0001", "done", "1", "")], [(1, "open")])
        throttle = {"status": 403, "headers": {"Retry-After": "30"}, "body": SECONDARY}
        self.stand_in(root, {"responses": {f"GET {OPEN_PULLS}": [throttle]}})
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual(self.calls(root)[-1]["args"][1], OPEN_PULLS)
        self.assertEqual(self.writes(root), [])

    def test_a_second_run_writes_nothing(self):
        """REQ-5314: an interrupted or repeated run skips what is already closed."""
        root = self.repository([("TSK-0001", "done", "1", ""), ("TSK-0002", "withdrawn", "2", ""),
                                ("TSK-0003", "approved", "3", "ADR-0001")], [(1, "open"), (2, "open"), (3, "open")])
        first = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        before = len(self.writes(root))
        self.assertEqual(before, 4, self.writes(root))
        second = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(self.writes(root)[before:], [])

    def test_an_empty_archive_says_the_record_comes_first(self):
        """ADR-3090: the issues change after the record's pull request merges, so no archive means no call."""
        root = self.repository([], [(1, "open")])
        done = self.meow_github(root, "upgrade", "o/r")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("no archived task; merge `paw upgrade --write` first", done.stdout)
        self.assertEqual(self.calls(root), [])


class Guard(unittest.TestCase):
    """ADR-1810: the hook asks before a Bash command's `gh` changes governance, and passes a read in silence."""

    def guard(self, command):
        """`meow-github governance-guard` run on a Bash tool call holding `command`, as the hook runs it."""
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
        # An empty data directory, so the launcher runs the binary built beside it and not an installed one.
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}
            return subprocess.run([str(BIN), "governance-guard"], input=json.dumps(event), capture_output=True,
                                  text=True, env=env)

    def asked(self, done):
        """The reason of an `ask` answer, failing where the answer is anything else."""
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        answer = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual(answer["hookEventName"], "PreToolUse")
        self.assertEqual(answer["permissionDecision"], "ask")
        return answer["permissionDecisionReason"]

    def test_a_governance_change_is_asked(self):
        """TSK-2980 criterion 4, REQ-2576: each command that changes governance is answered `ask`, with a reason
        naming the method and the endpoint and nothing else of the command, however the command is written."""
        put = "gh api PUT repos/o/r/branches/main/protection"
        cases = (
            ("gh api -X PUT repos/o/r/branches/main/protection", put),
            ("gh api repos/o/r/rulesets -f name=x", "gh api POST repos/o/r/rulesets"),
            ("gh api repos/o/r/rulesets --input rs.json", "gh api POST repos/o/r/rulesets"),
            ("gh repo edit --visibility private", "gh repo edit"),
            ("gh repo archive", "gh repo archive"),
            ("gh api graphql -f query='mutation { x }'", "gh api POST graphql"),
            ("GH_TOKEN=x gh api -X PUT repos/o/r/branches/main/protection", put),
            ("env GH_TOKEN=x gh repo delete o/r", "gh repo delete"),
            ("git status && gh api -X PUT repos/o/r/rulesets/1", "gh api PUT repos/o/r/rulesets/1"),
            # Review of TSK-2980: forms that hid the method, the endpoint or `gh` itself.
            ("gh api \\\n  -X PUT repos/o/r/branches/main/protection", put),
            ("gh \\\n repo delete o/r", "gh repo delete"),
            ("gh api --hostname github.com -X PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api -iX PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api -iXPUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api repos/o/r/rulesets -fname=x", "gh api POST repos/o/r/rulesets"),
            ("gh api 2>/dev/null -X PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api -X PUT /repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            # A global flag before the subcommand, which gh accepts, doesn't hide it (BUG-1562).
            ("gh -R o/r api -X PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh --repo o/r repo edit --visibility private", "gh repo edit"),
            ("gh --repo=o/r secret set TOKEN", "gh secret set"),
            ("gh api /graphql -f query='mutation { x }'", "gh api POST graphql"),
            ("gh api https://api.github.com/graphql -f query='mutation { x }'", "gh api POST graphql"),
            ("gh api -X POST orgs/o/rulesets -f name=x", "gh api POST orgs/o/rulesets"),
            ("gh api graphql -f query=\"$(cat m.graphql)\"", "gh api POST graphql"),
            ("if true; then gh repo delete o/r; fi", "gh repo delete"),
            ("command gh repo delete o/r", "gh repo delete"),
            ("/usr/bin/gh repo delete o/r", "gh repo delete"),
            ("gh secret remove FOO", "gh secret remove"),
            # The second review: redirects that use `&`, a short flag with `=`, and more leading shell words.
            ("gh api 2>&1 -X PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api &>/dev/null -X PUT repos/o/r/hooks/1", "gh api PUT repos/o/r/hooks/1"),
            ("gh api graphql -f=query='mutation { x }'", "gh api POST graphql"),
            ("{ gh repo delete o/r; }", "gh repo delete"),
            ("command -p gh repo delete o/r", "gh repo delete"),
            ("nohup gh repo delete o/r", "gh repo delete"),
            ("gh api -X PUT 'repos/o/r/hooks/1?a=http://h/x'", "gh api PUT repos/o/r/hooks/1"),
        )
        for command, named in cases:
            with self.subTest(command=command):
                self.assertEqual(self.asked(self.guard(command)), f"meow-github: {named} changes how the repository "
                                                                  "is governed, which a person approves (REQ-2576)")

    def test_a_read_passes_in_silence(self):
        """TSK-2980 criterion 5, REQ-2576: a read, or a command with no `gh` in it, prints nothing and exits 0."""
        for command in ("gh api repos/o/r/issues", "gh api graphql -f query='{ viewer { login } }'",
                        "gh api graphql -f query='query($n:String!){ repository(name:$n){id} }' -f n=x",
                        "gh api -X PUT 'repos/x?a=https://h/repos/o/r/hooks/1'",
                        "git status", "echo gh is fine"):
            with self.subTest(command=command):
                done = self.guard(command)
                self.assertEqual((done.returncode, done.stdout, done.stderr), (0, "", ""))

    def test_the_token_is_never_echoed(self):
        """TSK-2980 criterion 6, REQ-2576: a token anywhere in a command the guard asks about, in front of it, in
        the endpoint's query or in place of the method, appears nowhere in its answer."""
        for command in (f"GH_TOKEN={SENTINEL} gh api -X PUT repos/o/r/branches/main/protection",
                        f"env GITHUB_TOKEN={SENTINEL} gh repo delete o/r",
                        f"gh api -X PUT 'repos/o/r/hooks/1?access_token={SENTINEL}'",
                        f"gh api -X {SENTINEL} repos/o/r/hooks/1"):
            with self.subTest(command=command):
                done = self.guard(command)
                self.asked(done)
                self.assertNotIn(SENTINEL, done.stdout + done.stderr)

    def test_the_hook_runs_the_guard_on_bash(self):
        """TSK-2980 criterion 7: `hooks.json` declares one `PreToolUse` command hook matching Bash that runs
        `meow-github governance-guard`. TSK-5150 adds `irreversible-guard` beside it (ADR-2750), so the unit
        declares those two command hooks and no other."""
        hooks = json.loads((UNIT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(list(hooks), ["PreToolUse"])
        self.assertEqual(len(hooks["PreToolUse"]), 1)
        entry = hooks["PreToolUse"][0]
        self.assertEqual(entry["matcher"], "Bash")
        self.assertEqual([hook["type"] for hook in entry["hooks"]], ["command", "command"])
        self.assertEqual([hook["command"] for hook in entry["hooks"]],
                         ['"${CLAUDE_PLUGIN_ROOT}"/bin/meow-github governance-guard',
                          '"${CLAUDE_PLUGIN_ROOT}"/bin/meow-github irreversible-guard'])


class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-github"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-github").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "history"], cwd=tmp, env={"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}, capture_output=True, text=True)
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("unread", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("install meow-core", done.stdout)

    def test_a_missing_binary_denies_every_bash_call_and_says_how_to_install(self):
        """TSK-5165, REQ-1426, ADR-2710: with no binary for the machine, the hook's `governance-guard` denies with
        exit 2 and a reason naming the unit, the machine and the install command, because a launcher with no
        binary can't tell which call its program would have let through."""
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-github"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-github").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            event = json.dumps({"tool_input": {"command": "gh repo delete o/r"}})
            done = subprocess.run(["sh", str(launcher), "governance-guard"], input=event, cwd=tmp, env={"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"},
                                  capture_output=True, text=True)
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual((done.returncode, done.stdout), (2, ""), done.stderr)
            self.assertIn("meow-github", done.stderr)
            self.assertIn(machine, done.stderr)
            self.assertIn("claude plugin install meow-core@meowpaw", done.stderr)


if __name__ == "__main__":
    unittest.main()
