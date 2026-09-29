# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1070 states, and ADR-1100's checks.

Each fixture writes a small record that every check passes into a temporary
repository, plants one defect, and runs the launcher there. `MEOW_FLOW_BIN`
names the launcher to test, so the same fixtures can first run against a
program that returns nothing and be seen failing (REQ-2072).
"""

import hashlib
import re
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_FLOW_BIN", UNIT / "bin" / "paw"))


def record(kind, ident, fields, sections, body=""):
    lines = ["---", f"id: {ident}", f"artifact: {kind}", f"status: {fields.pop('status', 'approved')}",
             "revised: 2026-01-01"]
    lines += [f"{key}: {value}" for key, value in fields.items()]
    lines += ["---", "", f"# {ident}", ""]
    for section in sections:
        lines += [f"## {section}", "", "Text.", ""]
    return "\n".join(lines) + body


def index(ident, names):
    return f"---\nid: {ident}\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n# Index\n\n" + \
        "".join(f"- {name}\n" for name in names)


CLEAN = {
    "vision.md": "---\nid: vision\nartifact: vision\nstatus: live\nrevised: 2026-01-01\n---\n\n# Vision\n",
    "README.md": index("index", ["SPC-0001", "EPC-0001", "BUG-0001"]),
    "specs/SPC-0001-a-part.md": record(
        "spec", "SPC-0001", {"status": "live", "states": "[REQ-0001]", "checked-at": ""},
        ["Scope", "Boundary", "Behaviour", "Failure paths"]),
    "research/RES-0001-synthesis.md": record(
        "research", "RES-0001", {}, ["Summary", "Conclusions", "Sources"], "\nIt indexes RES-0002.\n"),
    "research/RES-0002-a-finding.md": record(
        "research", "RES-0002", {"elaborates": "RES-0001"}, ["Summary", "Method", "Conclusions", "Sources"]),
    "requirements/README.md": index("index", ["REQ-0001"]),
    "requirements/REQ-0001-an-obligation.md": record(
        "requirement", "REQ-0001",
        {"topic": "a", "class": "functional", "verification": "static", "elaborates": "RES-0002"}, []),
    "adrs/README.md": index("index", ["ADR-0001"]),
    "adrs/ADR-0001-a-choice.md": record(
        "adr", "ADR-0001", {"addresses": "[REQ-0001]"},
        ["Decision", "Why", "Alternatives", "What it costs", "What would reverse it", "Consequences"]),
    "epics/EPC-0001-a-plan.md": record(
        "epic", "EPC-0001", {"realises": "ADR-0001", "checked-at": ""},
        ["Acceptance criteria", "Tasks", "Coverage", "Not covered"]),
    "tasks/TSK-0001-a-task.md": record(
        "task", "TSK-0001", {"epic": "EPC-0001", "closes": "\n  [\n    REQ-0001,\n  ]"},
        ["What to do", "Depends on", "Evidence", "Left alone"], "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n"),
    "bugs/BUG-0001-a-defect.md": record(
        "bug", "BUG-0001", {"violates": "REQ-0001", "severity": "minor", "found": "2026-01-01"},
        ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]),
}

CLEAN["adrs/ADR-0001-a-choice.md"] = CLEAN["adrs/ADR-0001-a-choice.md"].replace(
    "## Alternatives\n\nText.", "## Alternatives\n\n| Option | Why it lost |\n| ------ | ----------- |\n| Nothing | It costs more |")


class Repository:
    def __init__(self, profile=None, root="project"):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "repository"
        self.path.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.path, check=True)
        if profile is not None:
            (self.path / ".meowpaw").mkdir()
            (self.path / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")
        self.root = (self.path / root).resolve() if not Path(root).is_absolute() else Path(root)
        for name, text in CLEAN.items():
            self.write(name, text)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def edit(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding="utf-8")
        assert old in text, (name, old)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def run(self, *args):
        return subprocess.run([str(BIN), *args], cwd=self.path, capture_output=True, text=True)


class Checks(unittest.TestCase):
    def repo(self, **kwargs):
        repository = Repository(**kwargs)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def found(self, done, check, line):
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(line, done.stdout)
        self.assertIn(f"{check}: 1 finding\n", done.stdout)

    def test_a_clean_record_passes_every_check(self):
        done = self.repo().run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for check in ("front-matter", "identifiers", "relations", "index", "coverage", "shape", "rules"):
            self.assertIn(f"{check}: 0 findings", done.stdout)

    def test_front_matter_reports_a_status_outside_the_vocabulary(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        self.found(repository.run("check"), "front-matter",
                   "project/tasks/TSK-0001-a-task.md:4: status done is not one a task stores")

    def test_two_findings_are_counted_in_the_plural(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: done")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("front-matter: 2 findings\n", done.stdout)

    def test_a_defect_may_name_no_requirement(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "violates: REQ-0001\n", "")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("front-matter: 0 findings", done.stdout)

    def test_front_matter_reports_a_missing_field(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]\n", "")
        done = repository.run("check", "front-matter")
        self.found(done, "front-matter", "project/adrs/ADR-0001-a-choice.md: front matter has no addresses")

    def test_identifiers_reports_a_name_and_id_that_disagree(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "id: BUG-0001", "id: BUG-0002")
        self.found(repository.run("check", "identifiers"), "identifiers",
                   "project/bugs/BUG-0001-a-defect.md:2: declares id BUG-0002, where its name says BUG-0001")

    def test_identifiers_reports_a_cited_requirement_with_no_file(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nIt meets REQ-0999.")
        self.found(repository.run("check", "identifiers"), "identifiers",
                   "project/tasks/TSK-0001-a-task.md:25: cites REQ-0999, which has no file")

    def test_relations_reports_an_identifier_that_does_not_resolve(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: ADR-0001, ADR-0009")
        self.found(repository.run("check", "relations"), "relations",
                   "project/epics/EPC-0001-a-plan.md:6: realises names ADR-0009, which has no file")

    def test_relations_reports_a_link_whose_target_is_missing(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "EPC-0001-a-plan.md", "EPC-0001-gone.md")
        self.found(repository.run("check", "relations"), "relations",
                   "project/tasks/TSK-0001-a-task.md:31: links to ../epics/EPC-0001-gone.md, which doesn't exist")

    def test_a_relation_is_bare_identifiers(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "elaborates: RES-0002",
                        "elaborates: [RES-0002](../research/RES-0002-a-finding.md)")
        self.found(repository.run("check", "relations"), "relations",
                   "project/requirements/REQ-0001-an-obligation.md:9: elaborates holds more than bare identifiers")

    def test_index_reports_an_artifact_its_index_does_not_list(self):
        repository = self.repo()
        repository.write("requirements/README.md", index("index", []))
        self.found(repository.run("check", "index"), "index",
                   "project/requirements/README.md: doesn't list REQ-0001")

    def test_index_reports_an_entry_with_no_file(self):
        repository = self.repo()
        repository.write("adrs/README.md", index("index", ["ADR-0001", "ADR-0002"]))
        self.found(repository.run("check", "index"), "index",
                   "project/adrs/README.md:11: lists ADR-0002, which has no file")

    def test_coverage_reports_a_requirement_in_no_task(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "REQ-0001,", "")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/epics/EPC-0001-a-plan.md: REQ-0001 lands in no task")

    def test_coverage_reports_a_requirement_no_specification_states(self):
        repository = self.repo()
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/adrs/ADR-0001-a-choice.md: REQ-0001 is stated in no specification")

    def test_shape_reports_research_without_its_conclusions(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Conclusions", "## Thoughts")
        self.found(repository.run("check", "shape"), "shape",
                   "project/research/RES-0002-a-finding.md: has no Conclusions section")

    def test_a_draft_decision_carries_the_drafts_sections_and_an_approved_one_not(self):
        repository = self.repo()
        self.assertEqual(repository.run("check", "shape").returncode, 0)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = repository.run("check", "shape")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md: has no How I will know it was realised section, "
                      "which a draft decision carries", done.stdout)
        self.assertIn("has no What this does not settle section", done.stdout)

    def test_research_opens_with_its_summary(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Summary\n\nText.\n\n## Method", "## Method\n\nText.\n\n## Summary")
        self.found(repository.run("check", "shape"), "shape",
                   "project/research/RES-0002-a-finding.md: opens with Method, where a research opens with Summary")

    def test_research_carries_a_method_and_its_index_is_exempt(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Method\n\nText.\n\n", "")
        done = repository.run("check", "shape")
        self.found(done, "shape", "project/research/RES-0002-a-finding.md: has no Method section, which a research carries")
        self.assertNotIn("RES-0001", done.stdout)

    def test_a_requirement_never_carries_a_priority(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "topic: a", "topic: a\npriority: high")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/requirements/REQ-0001-an-obligation.md:7: carries priority, which a requirement never does")

    def test_a_decision_must_address_or_postpone_a_requirement(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: []")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:6: addresses no requirement and postpones none", done.stdout)

    def test_a_defect_carries_its_triage_and_no_priority(self):
        repository = self.repo()
        repository.edit("bugs/BUG-0001-a-defect.md", "## Triage", "## Thoughts")
        self.found(repository.run("check", "shape"), "shape",
                   "project/bugs/BUG-0001-a-defect.md: has no Triage section, which a defect carries")
        repository.edit("bugs/BUG-0001-a-defect.md", "severity: minor", "severity: minor\npriority: p1")
        self.assertIn("carries priority, which a defect never does", repository.run("check", "front-matter").stdout)

    def test_the_living_vision_stores_only_live(self):
        repository = self.repo()
        repository.edit("vision.md", "status: live", "status: approved")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/vision.md:4: status approved is not one a vision stores: live")

    def test_an_observed_status_is_never_stored(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: verified")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/epics/EPC-0001-a-plan.md:4: status verified is not one a epic stores")

    def test_a_numbered_kind_is_named_for_its_identifier(self):
        repository = self.repo()
        repository.write("research/a-loose-note.md", CLEAN["research/RES-0002-a-finding.md"].replace("RES-0002", "RES-0003"))
        done = repository.run("check", "identifiers")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/research/a-loose-note.md: the name doesn't have the form RES-NNNN-<slug>.md", done.stdout)

    def test_a_research_draft_dates_each_source_and_an_approved_one_need_not(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Sources\n\nText.",
                        "## Sources\n\n- [A page](https://example.org), read 2026-01-01\n- [Another](https://example.org)")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/research/RES-0002-a-finding.md:26: names a source without the date it was read")

    def test_a_research_draft_cites_no_requirement(self):
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "## Method\n\nText.", "## Method\n\nAs REQ-0001 asks.")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/research/RES-0002-a-finding.md:17: cites REQ-0001, and research cites no requirement")

    def test_a_judged_requirement_draft_names_its_verifier(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: judgement")
        self.assertEqual(repository.run("check", "rules").returncode, 0)
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: draft")
        self.found(repository.run("check", "rules"), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:8: is verified by judgement and names no verifier")
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: judgement", "verification: judgement\nverifier: agent")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_an_epic_realises_exactly_one_record(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: ADR-0001, BUG-0001")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:6: realises 2 records, where an epic realises exactly one decision or defect")

    def test_a_decision_says_why_each_alternative_lost(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "| Option | Why it lost |", "| Option | Notes |")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0001-a-choice.md:21: has no column saying why each alternative lost")

    def mark(self, repository, mark, extra=""):
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        f"## Tasks\n\n- [{mark}] T-001 TSK-0001 the task\n      closes: REQ-0001{extra}")

    def test_a_task_marked_parallel_and_done_carries_evidence(self):
        """BUG-1180: a task marked [P] is read with its mark, so its evidence is checked."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        "## Tasks\n\n- [x] T-001 [P] TSK-0001 the task\n      closes: REQ-0001")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.found(repository.run("check", "rules"), "rules",
                   'project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 done, and its Evidence section holds nothing past "Not yet."')

    def test_a_task_marked_done_carries_evidence(self):
        repository = self.repo()
        self.mark(repository, "x")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.found(repository.run("check", "rules"), "rules",
                   'project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 done, and its Evidence section holds nothing past "Not yet."')
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nNot yet.", "## Evidence\n\nNot yet.\n\nThe fixture passed.")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_task_with_evidence_left_unmarked_is_reported(self):
        repository = self.repo()
        self.mark(repository, " ")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/epics/EPC-0001-a-plan.md:18: leaves TSK-0001 unmarked, and its Evidence section is written")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet. Postponed by the owner.")
        self.assertEqual(repository.run("check", "coverage").returncode, 0)

    def test_a_task_closing_a_withdrawn_requirement_in_an_open_epic_is_reported(self):
        repository = self.repo()
        self.mark(repository, "x")
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        # A living specification stating a withdrawn requirement is a finding of its own (ADR-1470).
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/tasks/TSK-0001-a-task.md:7: closes REQ-0001, which is withdrawn, in EPC-0001, which is not verified")
        repository.edit("epics/EPC-0001-a-plan.md", 'checked-at: ', 'checked-at: "#1"')
        self.assertEqual(repository.run("check", "coverage").returncode, 0)

    def test_a_draft_body_naming_a_missing_identifier_is_reported(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        repository.edit("tasks/TSK-0001-a-task.md", "## Left alone\n\nText.", "## Left alone\n\nADR-0009 and `ADR-0008`.\n\n```text\nADR-0007\n```")
        done = repository.run("check", "relations")
        self.found(done, "relations", "project/tasks/TSK-0001-a-task.md:29: names ADR-0009, which has no file")
        self.assertNotIn("ADR-0008", done.stdout)
        self.assertNotIn("ADR-0007", done.stdout)
        repository.edit("tasks/TSK-0001-a-task.md", "status: draft", "status: approved")
        self.assertEqual(repository.run("check", "relations").returncode, 0)

    def verified(self, repository):
        self.mark(repository, "x")
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#1"')

    def test_show_derives_a_requirements_state(self):
        repository = self.repo()
        self.verified(repository)
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("State\n  verified\n  TSK-0001 done in EPC-0001, verified under #1\n", done.stdout)
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("State\n  checked by nothing\n\n", repository.run("show", "REQ-0002").stdout)

    def test_status_counts_requirements_by_derived_state(self):
        repository = self.repo()
        self.verified(repository)
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("Requirements\n  2 in force: 1 verified, 0 closed and not yet verified, 0 in a task not yet done, 0 postponed, 1 checked by nothing\n",
                      repository.run("status").stdout)

    def test_status_withholds_verified_from_an_epic_check_reports_on(self):
        repository = self.repo()
        self.verified(repository)
        self.assertIn("realised: EPC-0001 verified under #1", repository.run("status").stdout)
        repository.edit("tasks/TSK-0001-a-task.md", "## Left alone\n\nText.", "## Left alone\n\n[Gone](gone.md).")
        done = repository.run("status").stdout
        self.assertIn("drifted: EPC-0001 was verified under #1, and check reports 1 finding on it now", done)
        self.assertNotIn("realised: EPC-0001", done)

    def test_status_says_a_record_under_no_version_control_is_local(self):
        repository = self.repo()
        self.assertNotIn("local to this machine", repository.run("status").stdout)
        shutil.rmtree(repository.path / ".git")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("The record is local to this machine: ", done.stdout)

    INSIGHT = ("---\nid: INS-0001\nartifact: insight\nstatus: approved\nrevised: 2026-01-01\n---\n\n"
               "# A cache keyed by path misses after a rename\n\nText.\n\n## Evidence\n\n41 of 50 runs missed.\n\n"
               "## What looked right\n\nNone did.\n\n## The pattern\n\nKey a cache by content.\n")

    def insight(self, old="", new=""):
        repository = self.repo()
        repository.write("insights/INS-0001-a-lesson.md", self.INSIGHT.replace(old, new, 1))
        return repository

    def test_an_insight_meeting_each_rule_passes(self):
        repository = self.insight()
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("rules: 0 findings\n", done.stdout)
        self.assertTrue(repository.run("show", "INS-0001").stdout.startswith("INS-0001 insight, approved: "))

    def test_an_insight_title_states_a_claim(self):
        self.found(self.insight("A cache keyed by path misses after a rename", "Notes 2026-01-01").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:8: has a title carrying a date, where an insight's title states its claim")
        self.found(self.insight("A cache keyed by path misses after a rename", "Caching").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:8: has a title of 1 word, where an insight's title states its claim in at least four")

    def test_an_insight_carries_measured_evidence(self):
        self.found(self.insight("41 of 50 runs missed.", "Most runs missed.").run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:12: has evidence with no number, measurement or reproducible block")
        done = self.insight("41 of 50 runs missed.", "```text\n$ run\n```").run("check", "rules")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_an_insight_ends_with_its_pattern(self):
        repository = self.insight("## The pattern\n\nKey a cache by content.\n", "## The pattern\n\nKey a cache by content.\n\n## Notes\n\nMore.\n")
        self.found(repository.run("check", "rules"), "rules",
                   "project/insights/INS-0001-a-lesson.md:24: ends with Notes, where an insight ends with The pattern")

    def test_an_insight_is_allocated_and_templated(self):
        repository = self.repo()
        self.assertEqual(repository.run("new", "insight").stdout, "INS-0001\n")
        template = repository.run("template", "insight")
        self.assertEqual(template.returncode, 0, template.stderr)
        self.assertTrue(template.stdout.strip().endswith("templates/insight.md"), template.stdout)
        self.assertIn("## The pattern", Path(template.stdout.strip()).read_text(encoding="utf-8"))

    def test_the_specifications_index_lists_each_after_what_it_cites(self):
        repository = self.repo()
        spec = (repository.root / "specs/SPC-0001-a-part.md").read_text(encoding="utf-8")
        repository.write("specs/SPC-0002-a-layer.md", spec.replace("SPC-0001", "SPC-0002"))
        repository.edit("specs/SPC-0001-a-part.md", "## Scope\n\nText.", "## Scope\n\nText, built on SPC-0002.")
        repository.edit("README.md", "- SPC-0001\n", "- SPC-0001\n- SPC-0002\n")
        self.found(repository.run("check", "index"), "index", "project/README.md:10: lists SPC-0001 before SPC-0002, which it cites")
        repository.edit("README.md", "- SPC-0001\n- SPC-0002\n", "- SPC-0002\n- SPC-0001\n")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings\n", done.stdout)

    def test_a_living_document_collects_a_withdrawn_citation(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        repository.edit("specs/SPC-0001-a-part.md", "## Behaviour\n\nText.", "## Behaviour\n\nIt holds REQ-0001.")
        self.found(repository.run("check", "shape"), "shape",
                   "project/specs/SPC-0001-a-part.md:22: cites REQ-0001, which is withdrawn, outside a Withdrawn section")
        repository.edit("specs/SPC-0001-a-part.md", "## Behaviour\n\nIt holds REQ-0001.", "## Behaviour\n\nText.")
        repository.edit("specs/SPC-0001-a-part.md", "## Failure paths\n\nText.", "## Failure paths\n\nText.\n\n## Withdrawn\n\nREQ-0001, by ADR-0001.")
        done = repository.run("check", "shape")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("shape: 0 findings\n", done.stdout)

    def test_nothing_is_kept_in_an_archive_directory(self):
        repository = self.repo()
        research = (repository.root / "research/RES-0002-a-finding.md").read_text(encoding="utf-8")
        repository.write("research/archive/RES-0003-old.md", research.replace("RES-0002", "RES-0003"))
        self.assertIn("project/research/archive/RES-0003-old.md: sits in research/archive, a directory named for an archive; "
                      "freeze the record or discard it with a reason", repository.run("check", "shape").stdout)

    def statement(self, text, status="draft"):
        repository = self.repo()
        path = repository.root / "requirements/REQ-0001-an-obligation.md"
        body = path.read_text(encoding="utf-8").replace("status: approved", f"status: {status}")
        head, _, _ = body.partition("# REQ-0001")
        repository.write("requirements/REQ-0001-an-obligation.md", head + "# REQ-0001\n\n" + text + "\n\nWhy it holds.\n")
        return repository.run("check", "rules")

    def test_a_draft_requirement_carries_one_obligation(self):
        self.found(self.statement("The check MUST run and MUST NOT write."), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:14: carries more than one keyword, where a requirement carries one obligation: MUST, MUST NOT")
        self.assertEqual(self.statement("The check MUST NOT write.").returncode, 0)

    def test_a_draft_requirement_stands_alone(self):
        self.found(self.statement("Such a record MUST be kept."), "rules",
                   "project/requirements/REQ-0001-an-obligation.md:14: leans on a neighbour: Such a record")

    def test_a_draft_requirement_prohibits_with_must_not(self):
        self.found(self.statement("No step MUST write."), "rules",
                   'project/requirements/REQ-0001-an-obligation.md:14: negates a requirement with "No ... MUST", where a prohibition is MUST NOT: No step MUST')

    def test_an_approved_requirement_keeps_the_rules_it_was_approved_under(self):
        for text in ("The check MUST run and MUST NOT write.", "Such a record MUST be kept.", "No step MUST write."):
            done = self.statement(text, status="approved")
            self.assertEqual(done.returncode, 0, done.stdout)
            self.assertIn("rules: 0 findings\n", done.stdout)

    def test_a_retired_name_is_refused_in_a_record(self):
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: proposed")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/adrs/ADR-0001-a-choice.md:4: status proposed is retired: replaced by draft")
        repository.edit("adrs/ADR-0001-a-choice.md", "status: proposed", "status: approved\nunit: meow-core")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/adrs/ADR-0001-a-choice.md:5: carries unit, a retired field: the unit of work is named by the relations the record carries")

    def test_a_retired_name_is_refused_in_the_layout(self):
        repository = self.repo()
        layout = self.tmp_layout()
        text = (UNIT / "lib" / "layout.toml").read_text(encoding="utf-8")
        layout.write_text(text.replace('statuses = ["live"]\nindex = "README.md"', 'statuses = ["live", "current"]\nindex = "README.md"', 1), encoding="utf-8")
        done = subprocess.run([str(BIN), "check", "front-matter"], cwd=repository.path, capture_output=True, text=True,
                              env={**os.environ, "MEOW_LAYOUT": str(layout)})
        self.assertIn("the layout: the kind specification declares current, a retired name\n", done.stdout)
        self.assertEqual(done.returncode, 1, done.stdout)

    def tmp_layout(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return Path(directory.name) / "layout.toml"

    def test_count_prints_each_kind_by_status_and_the_identifiers(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        first = repository.run("count")
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn("requirement: 1: 1 withdrawn\n", first.stdout)
        self.assertIn("research: 1: 1 approved\n", first.stdout)
        self.assertIn("insight: 0\n", first.stdout)
        self.assertTrue(first.stdout.endswith("identifiers: 8\n"), first.stdout)
        self.assertEqual(first.stdout, repository.run("count").stdout)

    def test_an_empty_record_reports_its_coverage_as_zero(self):
        repository = self.repo()
        for path in (repository.root / "requirements").glob("REQ-*.md"):
            path.unlink()
        done = repository.run("check", "coverage")
        self.assertIn("coverage: 0 of 0 requirements in force land in a task; an empty record's coverage is zero, not complete\n", done.stdout)
        self.assertIn("Requirements\n  none in force, so coverage is zero, not complete\n", repository.run("status").stdout)

    def test_coverage_counts_the_requirements_that_land_in_a_task(self):
        done = self.repo().run("check", "coverage")
        self.assertIn("coverage: 1 of 1 requirements in force land in a task\n", done.stdout)

    REPORT = ("---\nid: onboarding\nartifact: onboarding\nstatus: draft\nrevised: 2026-01-01\n---\n\n# Onboarding\n\nText.\n\n"
              "## Verbs\n\nText.\n\n## Conventions\n\nText.\n\n## Documents\n\n"
              "| Document | Outcome | Where, or why |\n| --- | --- | --- |\n"
              "| `docs/guide.md` | migrated | SPC-0001 |\n| `notes.txt` | discarded | a scratch list nobody reads |\n\n"
              "## Gaps\n\nText.\n\n## Adoption\n\n1. Declare the verbs.\n")

    def onboarded(self, old="", new=""):
        repository = self.repo()
        (repository.path / "docs").mkdir()
        (repository.path / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (repository.path / "notes.txt").write_text("notes\n", encoding="utf-8")
        repository.write("onboarding.md", self.REPORT.replace(old, new, 1))
        return repository

    def test_an_onboarding_report_placing_every_document_passes(self):
        done = self.onboarded().run("check", "coverage")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("coverage: 0 findings\n", done.stdout)

    def test_an_onboarding_report_places_every_document_once(self):
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |\n", "").run("check", "coverage"), "coverage",
                   "project/onboarding.md: doesn't place notes.txt, a document the repository has")
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |\n",
                                  "| `notes.txt` | discarded | a scratch list nobody reads |\n| `notes.txt` | cited | SPC-0001 |\n").run("check", "coverage"),
                   "coverage", "project/onboarding.md:26: places notes.txt 2 times")

    def test_an_onboarding_outcome_is_one_of_four_with_a_reason(self):
        self.found(self.onboarded("| `notes.txt` | discarded |", "| `notes.txt` | archived |").run("check", "coverage"), "coverage",
                   "project/onboarding.md:25: gives notes.txt the outcome archived, where an outcome is migrated, cited, superseded or discarded")
        self.found(self.onboarded("| `notes.txt` | discarded | a scratch list nobody reads |", "| `notes.txt` | discarded | |").run("check", "coverage"),
                   "coverage", "project/onboarding.md:25: marks notes.txt discarded with no destination or reason")

    def converted(self, status="approved", guide="SPC-0001"):
        repository = self.repo()
        for name in ("docs/guide.md", "notes.txt", "old.md", "source.md"):
            (repository.path / name).parent.mkdir(parents=True, exist_ok=True)
            (repository.path / name).write_text("text\n", encoding="utf-8")
        rows = (f"| `docs/guide.md` | migrated | {guide} |\n| `notes.txt` | discarded | a scratch list nobody reads |\n"
                "| `old.md` | superseded | ADR-0001 |\n| `source.md` | cited | SPC-0001 |\n")
        report = self.REPORT.replace("status: draft", f"status: {status}").replace(
            "| `docs/guide.md` | migrated | SPC-0001 |\n| `notes.txt` | discarded | a scratch list nobody reads |\n", rows)
        repository.write("onboarding.md", report)
        return repository

    def present(self, repository):
        return sorted(n for n in ("docs/guide.md", "notes.txt", "old.md", "source.md") if (repository.path / n).exists())

    def test_removing_placed_documents_keeps_what_is_cited(self):
        repository = self.converted()
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.present(repository), ["source.md"])
        self.assertEqual(done.stdout, "before: 4 documents\nremoved docs/guide.md (migrated)\nremoved notes.txt (discarded)\n"
                                      "removed old.md (superseded)\nafter: 1 document\n")

    def test_nothing_is_removed_before_the_report_is_approved(self):
        repository = self.converted(status="draft")
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/onboarding.md is draft, and nothing is removed before a person approves", done.stdout)
        self.assertEqual(len(self.present(repository)), 4)

    def test_nothing_is_removed_where_a_destination_does_not_exist(self):
        repository = self.converted(guide="SPC-0009")
        done = repository.run("onboarding", "remove")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("docs/guide.md is migrated to SPC-0009, which names no artifact that exists", done.stdout)
        self.assertEqual(len(self.present(repository)), 4)

    def test_onboarding_adoption_is_numbered_steps(self):
        self.found(self.onboarded("1. Declare the verbs.", "Declare the verbs.").run("check", "rules"), "rules",
                   "project/onboarding.md:31: has an Adoption section with no numbered steps, where adoption is a sequence each leaving the repository working")

    def postponing(self, fields="postpones: [REQ-0002]"):
        repository = self.repo()
        requirement = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0002-a-later-one.md", requirement.replace("REQ-0001", "REQ-0002"))
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        repository.write("adrs/ADR-0002-not-now.md", decision.replace("ADR-0001", "ADR-0002").replace("addresses: [REQ-0001]", f"addresses: []\n{fields}"))
        return repository

    def test_a_postponed_requirement_is_derived_and_counted(self):
        repository = self.postponing()
        shown = repository.run("show", "REQ-0002")
        self.assertIn("State\n  postponed by ADR-0002\n", shown.stdout)
        status = repository.run("status").stdout
        self.assertIn("ADR-0002", status)
        self.assertIn("postponing: 1 requirement, revisited at each verification", status)
        self.assertIn("2 in force: 0 verified, 0 closed and not yet verified, 1 in a task not yet done, 1 postponed, 0 checked by nothing", status)
        for check in ("rules", "coverage"):
            done = repository.run("check", check)
            self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_postponed_requirement_a_task_closes_is_no_longer_postponed(self):
        repository = self.postponing()
        repository.edit("tasks/TSK-0001-a-task.md", "    REQ-0001,", "    REQ-0001,\n    REQ-0002,")
        shown = repository.run("show", "REQ-0002").stdout
        self.assertIn("State\n  in a task not yet done\n", shown)
        self.assertNotIn("postponed by", shown)

    def test_a_decision_addressing_and_postponing_nothing_is_reported(self):
        repository = self.postponing(fields="postpones: []")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0002-not-now.md:6: addresses no requirement and postpones none, where a decision does one or both")

    def test_a_task_added_after_approval_says_why(self):
        repository = self.repo()
        self.mark(repository, "+")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 added after approval with no added: line saying why")
        repository.edit("epics/EPC-0001-a-plan.md", "closes: REQ-0001", "closes: REQ-0001\n      added: nobody foresaw the case")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_dropped_task_keeps_its_entry_and_says_why(self):
        repository = self.repo()
        self.mark(repository, "~")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:18: marks TSK-0001 dropped with no dropped: line saying why")
        repository.edit("epics/EPC-0001-a-plan.md", "closes: REQ-0001", "closes: REQ-0001\n      dropped: the decision was reversed")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_draft_task_carries_acceptance_criteria(self):
        repository = self.repo()
        self.assertEqual(repository.run("check", "shape").returncode, 0)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        self.found(repository.run("check", "shape"), "shape",
                   "project/tasks/TSK-0001-a-task.md: has no Acceptance criteria section, which a draft task carries")

    def test_a_file_of_no_known_kind_is_reported(self):
        repository = self.repo()
        repository.write("notes/stray.md", "---\nid: x\nartifact: note\nstatus: live\nrevised: 2026-01-01\n---\n")
        self.found(repository.run("check", "front-matter"), "front-matter",
                   "project/notes/stray.md: an artifact of no known kind")


class Chain(unittest.TestCase):
    """SPC-1090: the gate each step checks, the chain's state, and the template in force."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def mark(self, repository, mark):
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        f"## Tasks\n\n- [{mark}] T-001 TSK-0001 the task\n      closes: REQ-0001")

    def ready(self, repository, *args):
        return repository.run("ready", *args)

    def test_research_is_always_ready(self):
        done = self.ready(self.repo(), "research")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("research needs no approved input", done.stdout)

    def test_design_refuses_a_draft_requirement_and_names_it(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: draft")
        done = self.ready(repository, "design", "REQ-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("REQ-0001, a requirement, is draft and not approved", done.stdout)
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: draft", "status: approved")
        self.assertEqual(self.ready(repository, "design", "REQ-0001").returncode, 0)

    def test_requirements_and_spec_refuse_what_has_no_file(self):
        repository = self.repo()
        for step, missing in (("requirements", "RES-0009"), ("spec", "ADR-0009")):
            done = self.ready(repository, step, missing)
            self.assertEqual(done.returncode, 1, step)
            self.assertIn(f"{missing} has no file", done.stdout, step)
        self.assertEqual(self.ready(repository, "requirements", "RES-0002").returncode, 0)
        self.assertEqual(self.ready(repository, "spec", "ADR-0001").returncode, 0)

    def test_epic_refuses_a_decision_whose_requirement_no_spec_states(self):
        repository = self.repo()
        self.assertEqual(self.ready(repository, "epic", "ADR-0001").returncode, 0)
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        done = self.ready(repository, "epic", "ADR-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("REQ-0001, which ADR-0001 addresses, is stated by no specification", done.stdout)

    def test_cover_refuses_until_its_dependency_is_done(self):
        repository = self.repo()
        repository.write("tasks/TSK-0002-a-second-task.md", CLEAN["tasks/TSK-0001-a-task.md"]
                         .replace("TSK-0001", "TSK-0002").replace("## Depends on\n\nText.", "## Depends on\n\nTSK-0001."))
        self.mark(repository, " ")
        done = self.ready(repository, "cover", "TSK-0002")
        self.assertEqual(done.returncode, 1)
        self.assertIn("TSK-0001, which TSK-0002 depends on, isn't done", done.stdout)
        self.mark_done(repository)
        self.assertEqual(self.ready(repository, "cover", "TSK-0002").returncode, 0)

    def mark_done(self, repository):
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")

    def test_implement_refuses_a_task_whose_epic_is_a_draft(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: draft")
        done = self.ready(repository, "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("EPC-0001, the epic of TSK-0001, is draft and not approved", done.stdout)

    def test_document_and_verify_wait_for_every_task(self):
        repository = self.repo()
        self.mark(repository, " ")
        for step in ("document", "verify"):
            done = self.ready(repository, step, "EPC-0001")
            self.assertEqual(done.returncode, 1, step)
            self.assertIn("TSK-0001, a task of EPC-0001, isn't done", done.stdout, step)
        self.mark_done(repository)
        for step in ("document", "verify"):
            self.assertEqual(self.ready(repository, step, "EPC-0001").returncode, 0, step)

    def test_review_waits_for_verification(self):
        repository = self.repo()
        done = self.ready(repository, "review", "EPC-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("EPC-0001 hasn't been verified", done.stdout)
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#1"')
        self.assertEqual(self.ready(repository, "review", "EPC-0001").returncode, 0)

    def test_an_unknown_step_names_the_ten(self):
        """TSK-2530 criterion 1, REQ-3207 and REQ-3216: `ready` knows the ten steps, cover among them."""
        done = self.ready(self.repo(), "bogus", "TSK-0001")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("research, requirements, design, spec, epic, cover, implement, document, verify, review",
                      done.stderr)

    def test_status_leads_with_drafts_and_places_each_decision(self):
        """TSK-2540 criterion 1, REQ-3202: an open task with no Cover is placed at cover (REQ-0321 for the drafts)."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.mark(repository, " ")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "Waiting for approval")
        self.assertIn("RES-0002 research, draft", lines[1])
        self.assertIn("next: cover TSK-0001 (EPC-0001, 0 of 1 task done)", done.stdout)
        self.mark_done(repository)
        self.assertIn("next: document, then verify EPC-0001 (1 task done)", repository.run("status").stdout)
        # A verified epic resting on draft research has drifted (ADR-1470).
        repository.edit("research/RES-0002-a-finding.md", "status: draft", "status: approved")
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#7"')
        self.assertIn("realised: EPC-0001 verified under #7", repository.run("status").stdout)

    def test_status_places_a_decision_with_no_epic(self):
        repository = self.repo()
        (repository.root / "epics" / "EPC-0001-a-plan.md").unlink()
        self.assertIn("next: spec, then epic", repository.run("status").stdout)

    def test_status_prints_the_same_state_twice(self):
        """TSK-2540 criterion 3, REQ-3202 and REQ-0210: status prints the same text twice, uncovered or covered."""
        repository = self.repo()
        first = repository.run("status").stdout
        self.assertIn("ADR-0001", first)
        self.assertEqual(first, repository.run("status").stdout)
        self.mark(repository, " ")
        first = repository.run("status").stdout
        self.assertIn(self.NEXT.format(step="cover"), first)
        self.assertEqual(first, repository.run("status").stdout)
        self.cover(repository)
        first = repository.run("status").stdout
        self.assertIn(self.NEXT.format(step="implement"), first)
        self.assertEqual(first, repository.run("status").stdout)

    NEXT = "next: {step} TSK-0001 (EPC-0001, 0 of 1 task done)"

    def cover(self, repository):
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence",
                        "## Acceptance criteria\n\n" + CRITERIA + "\n\n## Cover\n\n" + FILLED + "\n\n## Evidence")
        for name in ("tests/test_a_task.py", "evidence/a-failing-run.txt"):
            path = repository.path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("A file.\n", encoding="utf-8")

    def test_status_names_cover_for_an_uncovered_task(self):
        """TSK-2540 criterion 1, REQ-3202: an open task with no Cover is next for cover, not implement."""
        repository = self.repo()
        self.mark(repository, " ")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn(self.NEXT.format(step="cover"), [l.strip() for l in done.stdout.splitlines()])
        self.assertNotIn(self.NEXT.format(step="implement"), done.stdout)

    def test_status_names_implement_once_covered(self):
        """TSK-2540 criterion 2, REQ-3202: the same line names implement once the task's Cover is filled."""
        repository = self.repo()
        self.mark(repository, " ")
        self.assertIn(self.NEXT.format(step="cover"), repository.run("status").stdout)
        self.cover(repository)
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn(self.NEXT.format(step="implement"), [l.strip() for l in done.stdout.splitlines()])
        self.assertNotIn(self.NEXT.format(step="cover"), done.stdout)

    def test_the_profile_template_names_no_language(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("template", "profile")
        self.assertEqual(done.returncode, 0, done.stderr)
        path = Path(done.stdout.strip())
        self.assertEqual(path.name, "profile.toml")
        text = path.read_text(encoding="utf-8")
        for section in ("[verbs]", "[commits]", "[git]", "[record]", "[prose]"):
            self.assertIn(section, text)
        for word in ("python", "rust", "cargo", "npm", "node", "make", "mise", "gradle", "maven", "go ", "java", ".py", ".rs", ".js"):
            self.assertNotIn(word, text.lower(), word)

    def test_template_prefers_the_repository_own(self):
        repository = self.repo()
        unit = UNIT / "templates" / "task.md"
        done = repository.run("template", "task")
        if unit.is_file():
            self.assertEqual(done.stdout.strip(), str(unit))
        else:
            self.assertEqual(done.returncode, 1)
        own = repository.path / ".meowpaw" / "templates" / "task.md"
        own.parent.mkdir(parents=True)
        own.write_text("# mine\n", encoding="utf-8")
        done = repository.run("template", "task")
        self.assertEqual(done.returncode, 0)
        self.assertEqual(Path(done.stdout.strip()).resolve(), own.resolve())

    def test_an_unknown_kind_names_the_kinds(self):
        done = self.repo().run("template", "memo")
        self.assertEqual(done.returncode, 2)
        self.assertIn("research, requirement, adr, spec, epic, task, bug, insight, vision, constitution", done.stderr)

    def template(self, kind):
        done = self.repo().run("template", kind)
        self.assertEqual(done.returncode, 0, done.stderr)
        return Path(done.stdout.strip()).read_text(encoding="utf-8")

    def test_the_task_template_carries_a_cover(self):
        """TSK-2550 criterion 6, REQ-3200: the task template has `## Cover`, reading `Not yet.`, naming the four lines."""
        text = self.template("task")
        self.assertIn("\n## Cover\n", text)
        headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
        self.assertEqual(headings[headings.index("Depends on") + 1], "Cover", headings)
        cover = text.split("\n## Cover\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Not yet.", cover)
        for line in ("Checks", "Failing run", "Landed in", "Judgement"):
            self.assertIn(line, cover, line)

    def test_the_bug_template_names_cover(self):
        """TSK-2550 criterion 6, REQ-3200: the bug template's `enters` comment names cover among the steps."""
        enters = [line for line in self.template("bug").splitlines() if line.startswith("enters:")]
        self.assertEqual(len(enters), 1, enters)
        self.assertRegex(enters[0].split("#", 1)[1], r"\bcover\b")


FILLED = """- Checks: tests/test_a_task.py
- Failing run: evidence/a-failing-run.txt
- Landed in: #12
- Judgement: 2: whether the page reads well rests on a reader"""

CRITERIA = """1. Given a task, then a check passes.
2. Given a page, then it reads well.
3. Given a table, then it is ordered as a reader expects."""


class TasklessEpic(unittest.TestCase):
    """BUG-1250: `ready` and `status` read an epic that lists no tasks the same way (REQ-0208)."""

    def repo(self, named):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        if named:
            repository.edit("epics/EPC-0001-a-plan.md", "## Not covered\n\nText.",
                            "## Not covered\n\n- REQ-0001 is closed by a task another record carries.")
        return repository

    def test_an_epic_naming_every_requirement_is_ready(self):
        """TSK-2560 criterion 1: no tasks, every addressed requirement named under Not covered."""
        repository = self.repo(named=True)
        for step in ("document", "verify"):
            done = repository.run("ready", step, "EPC-0001")
            self.assertEqual(done.returncode, 0, done.stdout)

    def test_status_names_document_and_ready_agrees(self):
        """TSK-2560 criterion 2: status names document, and the gate it names lets the step run."""
        repository = self.repo(named=True)
        self.assertIn("next: document, then verify EPC-0001 (0 tasks done)", repository.run("status").stdout)
        done = repository.run("ready", "document", "EPC-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_an_epic_leaving_a_requirement_unnamed_is_refused_by_both(self):
        """TSK-2560 criterion 3: ready refuses naming the requirement, and status names the same refusal."""
        repository = self.repo(named=False)
        reason = "EPC-0001 lists no tasks, and REQ-0001, which ADR-0001 addresses, isn't named under Not covered"
        done = repository.run("ready", "document", "EPC-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn(reason, done.stdout)
        status = repository.run("status").stdout
        self.assertIn(f"waiting: {reason}", status)
        self.assertNotIn("next: document, then verify EPC-0001", status)


class Cover(unittest.TestCase):
    """SPC-1090 "The gate": `ready cover` takes today's implement gate, and `ready implement` needs a filled Cover.

    REQ-3207 keeps the run in which the checks failed, and REQ-3216 names each
    criterion resting on judgement before any implementation starts. A path
    under `Checks` or `Failing run` resolves against the repository's root.
    """

    def repo(self, cover=None, criteria=None):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        sections = ""
        if criteria is None and cover is not None:
            criteria = CRITERIA
        if criteria is not None:
            sections += "## Acceptance criteria\n\n" + criteria + "\n\n"
        if cover is not None:
            sections += "## Cover\n\n" + cover + "\n\n"
        if sections:
            repository.edit("tasks/TSK-0001-a-task.md", "## Evidence", sections + "## Evidence")
        return repository

    def landed(self, repository, *names):
        for name in names:
            path = repository.path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("A file.\n", encoding="utf-8")

    def implement(self, repository, task="TSK-0001"):
        return repository.run("ready", "implement", task)

    def test_cover_is_ready_on_an_approved_task(self):
        """TSK-2530 criterion 2, REQ-3207: `ready cover` exits 0 on an approved task under an approved epic."""
        done = self.repo().run("ready", "cover", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_cover_refuses_a_draft_task(self):
        """TSK-2530 criterion 2, REQ-3207: `ready cover` exits 1 naming a draft task as not approved."""
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        done = repository.run("ready", "cover", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("TSK-0001, a task, is draft and not approved", done.stdout)

    def test_cover_refuses_until_its_dependency_is_done(self):
        """TSK-2530 criterion 2, REQ-3207: `ready cover` exits 1 naming a dependency that isn't done."""
        repository = self.repo()
        repository.write("tasks/TSK-0002-a-second-task.md", CLEAN["tasks/TSK-0001-a-task.md"]
                         .replace("TSK-0001", "TSK-0002").replace("## Depends on\n\nText.", "## Depends on\n\nTSK-0001."))
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        done = repository.run("ready", "cover", "TSK-0002")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("TSK-0001, which TSK-0002 depends on, isn't done", done.stdout)
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")
        done = repository.run("ready", "cover", "TSK-0002")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_implement_refuses_a_task_with_no_cover(self):
        """TSK-2530 criterion 3, REQ-3207: `ready implement` exits 1 naming the missing Cover."""
        done = self.implement(self.repo())
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("Cover", done.stdout)
        self.assertIn("TSK-0001", done.stdout)

    def test_implement_refuses_a_cover_left_not_yet(self):
        """TSK-2530 criterion 3, REQ-3207: a Cover reading `Not yet.` is not filled either."""
        done = self.implement(self.repo(cover="Not yet."))
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("Cover", done.stdout)

    def test_implement_names_a_missing_failing_run(self):
        """TSK-2530 criterion 4, REQ-3207: a `Failing run` naming no file is named on its own line."""
        repository = self.repo(cover=FILLED)
        self.landed(repository, "tests/test_a_task.py")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertTrue(any("evidence/a-failing-run.txt" in line for line in done.stdout.splitlines()), done.stdout)
        self.assertNotIn("tests/test_a_task.py", done.stdout)

    def test_implement_names_a_missing_check(self):
        """TSK-2530 criterion 4, REQ-3207: a path under `Checks` naming no file is named on its own line."""
        repository = self.repo(cover=FILLED)
        self.landed(repository, "evidence/a-failing-run.txt")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("tests/test_a_task.py", done.stdout)
        self.assertNotIn("evidence/a-failing-run.txt", done.stdout)

    def test_implement_names_landed_in_left_none(self):
        """TSK-2530 criterion 5, REQ-3207: checks named and landed nowhere is named by its `Landed in` line."""
        repository = self.repo(cover=FILLED.replace("- Landed in: #12", "- Landed in: none"))
        self.landed(repository, "tests/test_a_task.py", "evidence/a-failing-run.txt")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("Landed in", done.stdout)

    def test_implement_names_a_judgement_with_no_reason(self):
        """TSK-2530 criterion 6, REQ-3216: a `Judgement` number with no reason is named by its number."""
        repository = self.repo(cover=FILLED.replace(
            "- Judgement: 2: whether the page reads well rests on a reader",
            "- Judgement: 2: whether the page reads well rests on a reader; 3:"))
        self.landed(repository, "tests/test_a_task.py", "evidence/a-failing-run.txt")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        named = [line for line in done.stdout.splitlines() if re.search(r"\b3\b", line.replace("TSK-0001", ""))]
        self.assertTrue(named, done.stdout)
        self.assertFalse(any(re.search(r"\b2\b", line.replace("TSK-0001", "")) for line in named), done.stdout)

    def test_implement_is_ready_once_the_cover_is_filled(self):
        """TSK-2530 criterion 7, REQ-3207 and REQ-3216: every line filled and every path present exits 0.

        The files are landed only after the refusal, so the check fails while
        `ready implement` reads no Cover at all.
        """
        repository = self.repo(cover=FILLED)
        refused = self.implement(repository)
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        self.landed(repository, "tests/test_a_task.py", "evidence/a-failing-run.txt")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_implement_is_ready_when_every_criterion_is_judgement(self):
        """TSK-2530 criterion 7, REQ-3216: all-`none` lines pass only when `Judgement` names every criterion."""
        criteria = "1. Given a page, then it reads well.\n2. Given a table, then it is ordered as a reader expects."
        partly = ("- Checks: none\n- Failing run: none\n- Landed in: none\n"
                  "- Judgement: 1: a reader decides whether it reads well")
        repository = self.repo(cover=partly, criteria=criteria)
        refused = self.implement(repository)
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        repository.edit("tasks/TSK-0001-a-task.md", "a reader decides whether it reads well",
                        "a reader decides whether it reads well; 2: the order a reader expects is a judgement")
        done = self.implement(repository)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_a_finished_task_needs_no_cover(self):
        """TSK-2530 criterion 8, REQ-3207: `paw check` asks no Cover of a task marked `[x]`, so a task finished before
        ADR-1620 stays valid, while `ready implement` asks one of the same task while it is open."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        refused = self.implement(repository)
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        self.assertIn("Cover", refused.stdout)
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nThe fixture passed.")
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("TSK-0001", done.stdout + done.stderr)
        self.assertNotIn("Cover", done.stdout + done.stderr)


class CoverPaths(unittest.TestCase):
    """BUG-1260, REQ-3207: a path under `Checks` or `Failing run` is a regular file kept inside the repository, and
    the failing run isn't one of the checks."""

    def refused(self, line, path, outside=False):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        cover = FILLED.replace("tests/test_a_task.py" if line == "Checks" else "evidence/a-failing-run.txt", path)
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence",
                        "## Acceptance criteria\n\n" + CRITERIA + "\n\n## Cover\n\n" + cover + "\n\n## Evidence")
        for name in ("tests/test_a_task.py", "evidence/a-failing-run.txt"):
            (repository.path / name).parent.mkdir(parents=True, exist_ok=True)
            (repository.path / name).write_text("A file.\n", encoding="utf-8")
        if outside:
            (repository.path.parent / "outside.txt").write_text("A file.\n", encoding="utf-8")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertTrue(any(path in l and line in l for l in done.stdout.splitlines()), done.stdout)

    def test_a_failing_run_outside_the_repository_is_refused(self):
        """TSK-2570 criterion 1: an absolute path, and a `..` path to a file that exists, under `Failing run`."""
        self.refused("Failing run", "/etc/hosts")
        self.refused("Failing run", "../outside.txt", outside=True)

    def test_a_failing_run_that_is_a_directory_is_refused(self):
        """TSK-2570 criterion 1: a directory in the repository under `Failing run` is no run."""
        self.refused("Failing run", "tests")

    def test_a_check_outside_the_repository_or_a_directory_is_refused(self):
        """TSK-2570 criterion 2: an absolute path, a `..` escape and a directory under `Checks`."""
        self.refused("Checks", "/etc/hosts")
        self.refused("Checks", "../outside.txt", outside=True)
        self.refused("Checks", "evidence")

    def test_a_check_named_as_its_own_failing_run_is_refused(self):
        """TSK-2570 criterion 3: `Failing run` naming the file `Checks` names."""
        self.refused("Failing run", "tests/test_a_task.py")


class CoverCriteria(unittest.TestCase):
    """BUG-1261, REQ-3216: no criterion that nothing checks reads as covered, whatever the Cover's other lines say."""

    def implement(self, cover, criteria="1. Given a, then b.\n2. Given c, then d."):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        sections = "## Acceptance criteria\n\n" + criteria + "\n\n" if criteria is not None else ""
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence", sections + "## Cover\n\n" + cover + "\n\n## Evidence")
        for name in ("tests/t.py", "evidence/run.txt"):
            (repository.path / name).parent.mkdir(parents=True, exist_ok=True)
            (repository.path / name).write_text("A file.\n", encoding="utf-8")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        return done.stdout.splitlines()

    def test_no_checks_names_every_criterion_whatever_else_is_named(self):
        """TSK-2571 criterion 1: `Checks: none` with a run and a pull request named still asks for every criterion."""
        lines = self.implement("- Checks: none\n- Failing run: evidence/run.txt\n- Landed in: #1\n- Judgement: none")
        for number in ("1", "2"):
            self.assertTrue(any(f"criterion {number}" in l for l in lines), lines)

    def test_a_task_with_no_numbered_criterion_is_refused(self):
        """TSK-2571 criterion 2: bullets in place of numbered criteria, and no criteria section, are refused."""
        none = "- Checks: none\n- Failing run: none\n- Landed in: none\n- Judgement: none"
        for criteria in ("- One.\n- Two.", None):
            with self.subTest(criteria=criteria):
                lines = self.implement(none, criteria)
                self.assertTrue(any("no numbered" in l and "criterion" in l for l in lines), lines)

    def test_a_judgement_naming_no_criterion_is_refused(self):
        """TSK-2571 criterion 3: `Judgement: 7` on a task whose criteria are 1 and 2."""
        lines = self.implement("- Checks: tests/t.py\n- Failing run: evidence/run.txt\n- Landed in: #1\n"
                               "- Judgement: 7: a reason")
        self.assertTrue(any(re.search(r"\b7\b", l.replace("TSK-0001", "")) for l in lines), lines)

    def test_an_empty_judgement_is_refused(self):
        """TSK-2571 criterion 4: `Judgement:` with nothing after it is neither a reason nor `none`."""
        lines = self.implement("- Checks: tests/t.py\n- Failing run: evidence/run.txt\n- Landed in: #1\n- Judgement:")
        self.assertTrue(any("Judgement" in l for l in lines), lines)


class RunSkill(unittest.TestCase):
    """SPC-1090 "The driver": `/meow-flow:run` continues past a step with no gate and stops at one (REQ-3202)."""

    def steps(self):
        text = (UNIT / "skills" / "run" / "SKILL.md").read_text(encoding="utf-8")
        block = re.search(r'<steps name="drive the chain">(.*?)</steps>', text, re.S)
        self.assertIsNotNone(block, "the run skill has no drive-the-chain steps")
        items = re.findall(r"^(\d+)\. (.*?)(?=^\d+\. |\Z)", block.group(1), re.S | re.M)
        return {int(number): " ".join(body.split()) for number, body in items}

    def test_the_driver_continues_past_a_step_with_no_gate(self):
        """TSK-2540 criterion 4, REQ-3202: a step reruns `paw status` and continues where no approval gate ends the step."""
        steps = self.steps()
        again = [body for body in steps.values()
                 if re.search(r"\b(without|no) (an )?approval gate", body)
                 and "paw status" in body and "again" in body and "continu" in body]
        self.assertTrue(again, steps)
        self.assertRegex(steps.get(5, ""), r"(?i)\bstop\b.*approval gate")


class Show(unittest.TestCase):
    """SPC-1100: an identifier resolves to its artifact and to what cites it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_show_resolves_an_identifier_and_derives_what_cites_it(self):
        done = self.repo().run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "REQ-0001 requirement, approved: project/requirements/REQ-0001-an-obligation.md")
        self.assertIn("Names\n  elaborates: RES-0002", done.stdout)
        cited = done.stdout.split("Cited by\n", 1)[1]
        for line in ("  addresses: ADR-0001", "  closes: TSK-0001", "  states: SPC-0001", "  violates: BUG-0001",
                     "  body: project/requirements/README.md"):
            self.assertIn(line, cited)

    def test_a_withdrawn_artifact_still_resolves(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0)
        self.assertIn("REQ-0001 requirement, withdrawn:", done.stdout)

    def test_a_task_marked_parallel_is_read_with_its_mark(self):
        """BUG-1180, REQ-0584: a task marked [P] derives its requirement's state from its mark."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.",
                        "## Tasks\n\n- [x] T-001 [P] TSK-0001 the task\n      closes: REQ-0001")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("TSK-0001 done in EPC-0001", done.stdout)
        self.assertNotIn("in a task not yet done", done.stdout)

    def test_an_identifier_with_no_artifact_resolves_to_nothing(self):
        done = self.repo().run("show", "REQ-0999")
        self.assertEqual(done.returncode, 1)
        self.assertIn("REQ-0999 resolves to nothing in the record", done.stdout)

    def test_show_needs_an_identifier(self):
        done = self.repo().run("show")
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: paw show <id>", done.stderr)


class Frozen(unittest.TestCase):
    """ADR-1170: an approved record changed since a base, outside what its kind may change."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        return repository

    def frozen(self, repository):
        return repository.run("check", "frozen", "--base", "HEAD")

    def test_nothing_changed_is_clean(self):
        done = self.frozen(self.repo())
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_rewording_an_approved_requirement_invalidates_it(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\nThe system MUST do more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/requirements/REQ-0001-an-obligation.md: approved at HEAD, and changed since", done.stdout)

    def test_a_change_naming_its_authority_passes(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\n**Amended by ADR-0001.** It says more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_task_may_gain_evidence_and_an_unverified_epic_marks(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nThe fixture passed.")
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [x] T-001 TSK-0001 the task")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_task_may_gain_its_projection(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "epic: EPC-0001", "epic: EPC-0001\nprojected: 0123456789ab")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_task_rewritten_outside_its_evidence_is_reported(self):
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## What to do\n\nText.", "## What to do\n\nSomething else.")
        self.assertEqual(self.frozen(repository).returncode, 1)

    def committed(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        return repository

    def test_a_filled_cover_leaves_an_approved_task_unchanged(self):
        """TSK-2530 criterion 9, REQ-3207: `check frozen` lets `## Cover` change after approval, as `## Evidence` does,
        and still reports a change to the task's acceptance criteria."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence",
                        "## Acceptance criteria\n\n1. Given a record, then it passes.\n\n## Cover\n\nNot yet.\n\n## Evidence")
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        repository.edit("tasks/TSK-0001-a-task.md", "## Cover\n\nNot yet.",
                        "## Cover\n\n- Checks: tests/test_a_task.py\n- Failing run: evidence/a-failing-run.txt\n"
                        "- Landed in: #12\n- Judgement: none")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("frozen: 0 findings", done.stdout)
        repository.edit("tasks/TSK-0001-a-task.md", "1. Given a record, then it passes.",
                        "1. Given a record, then it passes quickly.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/tasks/TSK-0001-a-task.md: approved at HEAD, and changed since", done.stdout)

    def test_an_added_line_citing_a_hash_as_a_revision_is_reported(self):
        repository = self.committed()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nThe fixtures passed at `9f3c2e1`.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("cites the commit 9f3c2e1 as a revision; cite the pull request that carried it", done.stdout)

    def test_an_added_line_citing_a_pull_request_passes(self):
        repository = self.committed()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nThe fixtures passed at the trunk after #12, and a fee was added.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_verified_epic_is_frozen(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "checked-at: ", 'checked-at: "#9"')
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\nTidied.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/epics/EPC-0001-a-plan.md: approved at HEAD", done.stdout)

    def test_a_living_document_is_never_frozen(self):
        repository = self.repo()
        repository.edit("specs/SPC-0001-a-part.md", "## Scope\n\nText.", "## Scope\n\nRewritten.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_a_kinds_own_index_is_never_frozen(self):
        repository = self.repo()
        repository.edit("research/RES-0001-synthesis.md", "It indexes RES-0002.", "It indexes RES-0002, and more.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)

    def test_withdrawing_a_requirement_passes(self):
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("frozen: 0 findings", done.stdout)


class Waiting(unittest.TestCase):
    """ADR-1170: a session opens with what waits for approval, and says nothing otherwise."""

    def test_a_draft_decision_is_reported_at_its_gate(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        done = repository.run("status", "--waiting")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("ADR-0001 decision, at the design gate", done.stdout)

    def test_nothing_waiting_prints_nothing(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("status", "--waiting")
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertIn("ADR-0001", repository.run("status").stdout)

    def test_a_repository_with_no_record_prints_nothing(self):
        repository = Repository(profile='[record]\nroot = "nowhere"\n')
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("status", "--waiting")
        self.assertEqual((done.returncode, done.stdout), (0, ""))
        self.assertIn("nowhere", repository.run("status").stdout)


class Indexes(unittest.TestCase):
    """ADR-1180: a kind's index generated from the tree, and checked for drift."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "---\nid: index\nartifact: index\nstatus: live\nrevised: 2026-01-01\n---\n\n"
                         "# Decisions\n\nWritten by hand.\n\n<!-- meow-flow index -->\n<!-- /meow-flow index -->\n")
        return repository

    def test_index_writes_the_block_and_keeps_the_prose(self):
        repository = self.repo()
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        text = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Written by hand.", text)
        self.assertIn("| [ADR-0001](ADR-0001-a-choice.md) |", text)
        self.assertIn("1 decision in all: 1 approved.", text)
        self.assertEqual(repository.run("check", "index").returncode, 0)

    def test_an_index_left_behind_is_reported_and_rewriting_clears_it(self):
        repository = self.repo()
        repository.run("index", "adr", "--write")
        repository.write("adrs/ADR-0002-another.md", CLEAN["adrs/ADR-0001-a-choice.md"].replace("ADR-0001", "ADR-0002"))
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/adrs/README.md:12: its generated block is out of date; run paw index decision --write",
                      done.stdout)
        repository.run("index", "adr", "--write")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings", done.stdout)

    def test_padding_a_generated_table_is_not_drift(self):
        repository = self.repo()
        repository.run("index", "adr", "--write")
        path = repository.root / "adrs" / "README.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| --- |", "| ------------ |").replace("| [ADR", "|   [ADR"),
                        encoding="utf-8")
        done = repository.run("check", "index")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("index: 0 findings", done.stdout)

    def test_a_large_kind_gains_a_view_by_topic_ordered_by_identifier(self):
        repository = self.repo()
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        for n in range(2, 40):
            topic = "b" if n % 2 else "a"
            repository.write(f"requirements/REQ-{n:04d}-r.md",
                             base.replace("REQ-0001", f"REQ-{n:04d}").replace("topic: a", f"topic: {topic}"))
        done = repository.run("index", "requirement")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        rows = re.findall(r"^\| \[(REQ-\d{4})\]", done.stdout, re.M)
        self.assertEqual(rows, sorted(rows))
        self.assertEqual(len(rows), 39)
        self.assertIn("By topic:", done.stdout)
        self.assertRegex(done.stdout, r"- a: REQ-0001, REQ-0002, REQ-0004")


class Allocate(unittest.TestCase):
    """ADR-1180: the next identifier, in its topic's block, never one already taken."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0010-ten.md", base.replace("REQ-0001", "REQ-0010").replace("topic: a", "topic: t"))
        return repository

    def new(self, repository, *args):
        done = repository.run("new", *args)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return done.stdout.strip()

    def test_a_requirement_takes_the_next_number_in_its_topic(self):
        repository = self.repo()
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0012")
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0012-twelve.md", base.replace("REQ-0001", "REQ-0012").replace("topic: a", "topic: t"))
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0014")

    def test_a_withdrawn_or_cited_number_is_never_given_again(self):
        repository = self.repo()
        base = CLEAN["requirements/REQ-0001-an-obligation.md"]
        repository.write("requirements/REQ-0012-gone.md", base.replace("REQ-0001", "REQ-0012").replace("topic: a", "topic: z")
                         .replace("status: approved", "status: withdrawn"))
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nSee REQ-0014.")
        self.assertEqual(self.new(repository, "requirement", "--topic", "t"), "REQ-0016")

    def test_a_new_topic_starts_a_block_above_the_highest(self):
        self.assertEqual(self.new(self.repo(), "requirement", "--topic", "fresh"), "REQ-0100")

    def test_other_kinds_take_the_next_block_of_ten(self):
        repository = self.repo()
        self.assertEqual(self.new(repository, "adr"), "ADR-0010")
        self.assertEqual(self.new(repository, "research"), "RES-0003")

    def test_a_requirement_needs_its_topic(self):
        done = self.repo().run("new", "requirement")
        self.assertEqual(done.returncode, 2)
        self.assertIn("name it with --topic", done.stderr)


class Find(unittest.TestCase):
    """ADR-1180: identifiers and headings first, ranked by the words matched."""

    def test_find_ranks_and_prints_headings_only(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("adrs/ADR-0001-a-choice.md", "# ADR-0001", "# 0001. An approval gate for the plan")
        repository.edit("epics/EPC-0001-a-plan.md", "# EPC-0001", "# The gate")
        done = repository.run("find", "approval", "gate")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = done.stdout.strip().splitlines()
        self.assertEqual(lines[0], "ADR-0001 decision, approved: An approval gate for the plan")
        self.assertEqual(lines[1], "EPC-0001 epic, approved: The gate")
        self.assertNotIn("Text.", done.stdout)

    def test_find_with_no_match_says_so(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find", "zebra")
        self.assertEqual(done.returncode, 1)
        self.assertIn("nothing in the record carries zebra", done.stdout)

    def test_find_needs_a_word(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("find")
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage: paw find", done.stderr)


class ReadingEnvironment(unittest.TestCase):
    """ADR-1320: every read of source control has prompting, paging, advice and machine-wide configuration off."""

    def test_each_read_of_git_runs_in_the_reading_environment(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        real = shutil.which("git")
        stand_in = repository.path.parent / "bin"
        stand_in.mkdir()
        log = repository.path.parent / "git.log"
        (stand_in / "git").write_text(
            "#!/bin/sh\n"
            f"printf '%s %s %s %s %s\\n' \"$GIT_TERMINAL_PROMPT\" \"$GIT_PAGER\" \"$GIT_ADVICE\" \"$GIT_CONFIG_NOSYSTEM\" \"$1\" >> {log}\n"
            f"exec {real} \"$@\"\n", encoding="utf-8")
        (stand_in / "git").chmod(0o755)
        env = {**os.environ, "PATH": f"{stand_in}:{os.environ['PATH']}"}
        for command in (["status"], ["check", "frozen"], ["check", "coverage"]):
            subprocess.run([str(BIN), *command], cwd=repository.path, capture_output=True, text=True, env=env)
        calls = log.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(calls), 3, calls)
        for call in calls:
            self.assertEqual(call.split()[:4], ["0", "cat", "0", "1"], call)


class ReadOnly(unittest.TestCase):
    """ADR-1200: the commands that read the record write nothing, and repeat themselves."""

    COMMANDS = (["check"], ["check", "frozen"], ["status"], ["status", "--waiting"], ["ready", "design", "REQ-0001"],
                ["template", "task"], ["show", "REQ-0001"], ["index", "requirement"], ["new", "adr"],
                ["find", "task"], ["count"])

    def tree(self, root):
        out = {}
        for path in sorted(root.rglob("*")):
            if ".git" in path.parts:
                continue
            stat = path.stat()
            out[str(path)] = (hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir", stat.st_mtime_ns)
        return out

    def test_each_read_only_command_writes_nothing_and_repeats_itself(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        for command in self.COMMANDS:
            before = self.tree(repository.path)
            first = repository.run(*command)
            second = repository.run(*command)
            self.assertEqual(before, self.tree(repository.path), command)
            self.assertEqual(first.stdout, second.stdout, command)
            # Nothing waiting is the one case whose right answer is silence.
            if command != ["status", "--waiting"]:
                self.assertNotEqual(first.stdout + first.stderr, "", command)

    def test_writing_an_index_leaves_no_temporary_file(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "# Decisions\n\n<!-- meow-flow index -->\n<!-- /meow-flow index -->\n")
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(sorted(p.name for p in (repository.root / "adrs").iterdir()),
                         ["ADR-0001-a-choice.md", "README.md"])
        written = (repository.root / "adrs" / "README.md").read_text(encoding="utf-8")
        self.assertIn("| [ADR-0001](ADR-0001-a-choice.md) |", written)
        self.assertIn("<!-- /meow-flow index -->", written)

    def test_an_index_with_the_old_markers_is_no_longer_read(self):
        """REQ-3190, ADR-1390: from 0.32.0 the markers before the rename are not read, and writing names the new ones."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("adrs/README.md", "# Decisions\n\n<!-- meow-method index -->\n<!-- /meow-method index -->\n")
        done = repository.run("index", "adr", "--write")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("has no <!-- meow-flow index --> block to write into", done.stdout)


class Where(unittest.TestCase):
    def test_a_root_outside_the_repository_is_read_there(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        elsewhere = Path(outside.name) / "record"
        repository = Repository(profile=f'[record]\nroot = "{elsewhere}"\n', root=str(elsewhere))
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"{elsewhere.resolve()}/tasks/TSK-0001-a-task.md:4: status done", done.stdout)
        self.assertFalse((repository.path / "project").exists())

    def test_a_relative_root_leading_outside_is_read_there(self):
        repository = Repository(profile='[record]\nroot = "../shared/record"\n', root="../shared/record")
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("shape: 0 findings", done.stdout)

    def test_a_root_that_does_not_exist_checks_nothing(self):
        repository = Repository(profile='[record]\nroot = "nowhere"\n')
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("nowhere doesn't exist; nothing was checked", done.stdout)
        self.assertNotIn("findings", done.stdout)

    def test_an_unknown_check_names_the_six(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        done = repository.run("check", "spelling")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("front-matter, identifiers, relations, index, coverage, shape, rules", done.stderr)


class NoWrites(unittest.TestCase):
    def test_the_tree_is_identical_before_and_after_a_run(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: done")

        def tree():
            out = {}
            for path in sorted(repository.path.rglob("*")):
                if ".git" in path.parts:
                    continue
                stat = path.stat()
                digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "dir"
                out[str(path)] = (digest, stat.st_mtime_ns)
            return out

        before = tree()
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(before, tree())



class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "paw"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "paw").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "check"], cwd=tmp, capture_output=True, text=True, input="")
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("not checked", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("reinstall the unit", done.stdout)


class Named(unittest.TestCase):
    """REQ-3168, REQ-3190, ADR-1390: the unit is meow-flow, and its command is paw."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_every_usage_line_and_message_names_paw(self):
        repository = self.repo()
        done = [repository.run(*args) for args in
                [("check",), ("show",), ("ready",), ("find",), ("count", "x"), ("check", "nothing"), ("show", "REQ-0999")]]
        self.assertEqual(done[0].returncode, 0, done[0].stdout + done[0].stderr)
        said = "".join(run.stdout + run.stderr for run in done)
        self.assertIn("usage: paw show <id>", said)
        self.assertIn("paw check: no check is named nothing", said)
        self.assertIn("paw show: REQ-0999 resolves to nothing", said)
        self.assertNotIn("meow-method", said)

    def test_the_unit_is_named_meow_flow(self):
        manifest = json.loads((UNIT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "meow-flow")
        self.assertEqual(UNIT.name, "meow-flow")
        self.assertEqual(sorted(p.name for p in (UNIT / "bin").iterdir() if p.is_file()), ["paw"])

    def test_nothing_the_unit_ships_names_the_old_unit(self):
        found = [f"{path.relative_to(UNIT)}:{number}"
                 for path in sorted(UNIT.rglob("*"))
                 if path.is_file() and path.suffix in {".md", ".json", ".toml", ""} and "tests" not in path.parts
                 and path.parent.parent != UNIT / "bin"
                 for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
                 if "meow-method" in line]
        self.assertEqual(found, [])



class DefectTasks(unittest.TestCase):
    """ADR-1440: a defect authorises a task directly, with no epic."""

    def repo(self, bug_status="approved", mark="x"):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        bug = record("bug", "BUG-0002", {"status": bug_status, "violates": "REQ-0001", "severity": "minor",
                                          "found": "2026-01-01"},
                     ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"])
        bug += f"\n## Tasks\n\n- [{mark}] T-001 TSK-0002 restore the obligation\n      evidence: the reproduction passes.\n"
        repository.write("bugs/BUG-0002-a-second-defect.md", bug)
        repository.write("tasks/TSK-0002-a-fix.md", record(
            "task", "TSK-0002", {"bug": "BUG-0002", "closes": "[REQ-0001]"},
            ["What to do", "Depends on", "Evidence", "Left alone"]).replace(
            "## Depends on\n\nText.", "## Depends on\n\nNothing."))
        return repository

    def test_a_task_a_defect_marks_done_is_done(self):
        """REQ-0354: a defect carries its own task, and the task's state derives from its mark."""
        done = self.repo().run("show", "REQ-0001")
        self.assertIn("TSK-0002 done in BUG-0002", done.stdout)

    def test_a_task_under_an_approved_defect_is_ready(self):
        """REQ-0352: a defect record authorises work exactly as a decision record does."""
        done = self.repo(mark=" ").run("ready", "cover", "TSK-0002")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_task_under_a_draft_defect_is_not_ready(self):
        """REQ-0352: a draft defect authorises nothing yet."""
        done = self.repo(bug_status="draft", mark=" ").run("ready", "implement", "TSK-0002")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("BUG-0002, the defect of TSK-0002, is draft and not approved", done.stdout)

    def test_status_counts_tasks_by_their_authority(self):
        """REQ-0374: the proportion of work defects authorise is reported."""
        done = self.repo().run("status")
        self.assertIn("2 in all: 1 authorised by decisions, 1 by defects", done.stdout)

    def test_a_draft_task_naming_no_authority_is_reported(self):
        """ADR-1440: a task names exactly one epic or one defect."""
        repository = self.repo()
        repository.write("tasks/TSK-0003-a-stray.md", record(
            "task", "TSK-0003", {"status": "draft", "closes": "[REQ-0001]"},
            ["What to do", "Depends on", "Evidence", "Left alone", "Acceptance criteria"]))
        done = repository.run("check", "rules")
        self.assertIn("TSK-0003-a-stray.md", done.stdout)
        self.assertIn("names 0 authorising records", done.stdout)

    def test_a_defects_marks_change_after_approval(self):
        """ADR-1440: an approved defect's Tasks section changes as an epic's marks do."""
        repository = self.repo(mark=" ")
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)
        repository.edit("bugs/BUG-0002-a-second-defect.md", "- [ ] T-001", "- [x] T-001")
        repository.edit("bugs/BUG-0002-a-second-defect.md", "## Closed by\n\nText.", "## Closed by\n\nThe reproduction, now a check.")
        done = repository.run("check", "frozen")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("bugs/BUG-0002-a-second-defect.md", "## Triage\n\nText.", "## Triage\n\nRewritten.")
        self.assertEqual(repository.run("check", "frozen").returncode, 1)


class Triage(unittest.TestCase):
    """ADR-1440: a defect's triage, reproduction and closing, held by paw check."""

    SECTIONS = ["Reproduction", "What the system does", "What it should do, and why", "Triage", "Closed by"]

    def check(self, fields, edits=(), extra=None):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        base = {"severity": "minor", "found": "2026-01-01"}
        base.update(fields)
        repository.write("bugs/BUG-0003-a-report.md", record("bug", "BUG-0003", base, self.SECTIONS))
        for old, new in edits:
            repository.edit("bugs/BUG-0003-a-report.md", old, new)
        if extra:
            extra(repository)
        return repository.run("check", "rules").stdout

    def test_a_triaged_draft_names_where_it_enters(self):
        """REQ-0360: the triage answer decides which step the defect enters at."""
        said = self.check({"status": "draft", "violates": "REQ-0001"})
        self.assertIn("has a Triage section and no enters", said)

    def test_entering_at_implement_needs_a_violated_requirement(self):
        """REQ-0358: triage first answers whether a requirement in force covers the behaviour."""
        said = self.check({"enters": "implement"})
        self.assertIn("enters implement and names no requirement it violates", said)

    def test_a_defect_may_enter_at_cover(self):
        """TSK-2530 criterion 10, REQ-3207: `enters: cover` is a step, and naming what it violates is enough."""
        said = self.check({"enters": "cover", "violates": "REQ-0001"})
        self.assertNotIn("enters", said)
        self.assertIn("rules: 0 findings", said)

    def test_a_defect_entering_at_cover_names_what_it_violates(self):
        """TSK-2530 criterion 10, REQ-3207: a defect entering at cover names the requirement it violates."""
        said = self.check({"enters": "cover"})
        self.assertIn("enters cover and names no requirement it violates", said)
        self.assertNotIn("which is not a step", said)

    def test_a_triaged_defect_carries_a_reproduction(self):
        """REQ-0364: a defect carries a reproduction before it is triaged."""
        said = self.check({"enters": "requirements"}, [("## Reproduction\n\nText.", "## Reproduction\n")])
        self.assertIn("is triaged with an empty Reproduction", said)

    def test_a_rejected_report_records_why(self):
        """REQ-0370: a defect closed as not a defect records the reasoning."""
        said = self.check({"status": "rejected"}, [("## Triage\n\nText.", "## Triage\n")])
        self.assertIn("is rejected as no defect with an empty Triage", said)

    def test_a_closed_defect_names_its_regression_check(self):
        """REQ-0368: the check that closes a defect remains as a regression check."""
        def task(repository):
            repository.write("tasks/TSK-0004-a-fix.md", record(
                "task", "TSK-0004", {"bug": "BUG-0003", "closes": "[]"},
                ["What to do", "Depends on", "Evidence", "Left alone"]))
        said = self.check({"violates": "REQ-0001"}, [("## Closed by\n\nText.", "## Closed by\n\n## Tasks\n\n- [x] T-001 TSK-0004 fix it\n      evidence: it passes.\n")], task)
        self.assertIn("has every task done and an empty Closed by", said)

    def test_severity_is_required(self):
        """REQ-0372: severity is recorded on the defect."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.write("bugs/BUG-0003-a-report.md", record("bug", "BUG-0003", {"found": "2026-01-01"}, self.SECTIONS))
        said = repository.run("check", "front-matter").stdout
        self.assertIn("BUG-0003-a-report.md", said)
        self.assertIn("severity", said)

    def test_an_epic_for_a_one_task_defect_is_reported(self):
        """REQ-0356: an epic is created for a defect only where the fix needs several ordered tasks."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: BUG-0001")
        said = repository.run("check", "rules").stdout
        self.assertIn("realises the defect BUG-0001 with 0 tasks and no order between them", said)

    def test_prompted_by_names_a_defect(self):
        """REQ-0362: a record a defect prompted cites the defect."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("requirements/REQ-0001-an-obligation.md", "topic: a", "topic: a\nprompted-by: ADR-0001")
        said = repository.run("check", "rules").stdout
        self.assertIn("is prompted by ADR-0001, which is not a defect", said)


class Connections(unittest.TestCase):
    """ADR-1470: each chain is checked to its research, and each citation against its target's date."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_an_evaluation_case_may_name_a_record_that_does_not_exist(self):
        """ADR-1490: an evaluation case's sample record is fixture material, not a document citing the record."""
        repository = self.repo()
        case = repository.path / "plugins" / "unit" / "evals" / "a-case" / "prompt.md"
        case.parent.mkdir(parents=True)
        case.write_text("Review this record.\n\n---\nid: REQ-0999\n---\n\nREQ-0999 MUST hold.\n", encoding="utf-8")
        done = repository.run("check", "identifiers")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_an_approved_task_over_draft_research_names_the_chain(self):
        """REQ-0139: a task whose own links resolve is reported where the research under it is a draft."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/tasks/TSK-0001-a-task.md: rests on RES-0002, a draft, through "
                      "TSK-0001 -> EPC-0001 -> ADR-0001 -> REQ-0001 -> RES-0002", done.stdout)

    def test_a_draft_over_a_withdrawn_requirement_is_reported(self):
        """REQ-0139: a draft still being written can be moved off a withdrawn provider."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/adrs/ADR-0001-a-choice.md: rests on REQ-0001, which is withdrawn, through "
                      "ADR-0001 -> REQ-0001", done.stdout)

    def test_a_living_artifact_over_a_rejected_provider_is_reported(self):
        """REQ-0139: a living artifact can be moved off a rejected provider, so check reports it."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: rejected")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/specs/SPC-0001-a-part.md: rests on RES-0002, which is rejected, through "
                      "SPC-0001 -> REQ-0001 -> RES-0002", done.stdout)
        self.assertNotIn("project/adrs/ADR-0001-a-choice.md: rests on", done.stdout)

    def test_a_draft_citing_a_later_revision_is_suspect(self):
        """REQ-0141: a draft citing an artifact revised after it is reported, and so is a living one."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "status: approved", "status: draft")
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/adrs/ADR-0001-a-choice.md:6: addresses REQ-0001, revised 2026-02-01, "
                      "after this record's 2026-01-01, so the citation is suspect", done.stdout)
        self.assertIn("project/specs/SPC-0001-a-part.md:6: states REQ-0001, revised 2026-02-01", done.stdout)
        self.assertIn("relations: 2 findings", done.stdout)

    def test_an_approved_record_citing_a_later_revision_is_marked_by_show(self):
        """REQ-0141: a frozen record can't be revised, so show marks its suspect citation and check passes."""
        repository = self.repo()
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        repository.edit("specs/SPC-0001-a-part.md", "revised: 2026-01-01", "revised: 2026-03-01")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        shown = repository.run("show", "ADR-0001").stdout
        self.assertIn("  addresses: REQ-0001 (suspect: revised 2026-02-01, after this record)", shown)

    def test_an_epic_is_suspect_by_its_status_and_not_its_date(self):
        """REQ-0141: an epic changes as its tasks close, so only its withdrawal makes a citation suspect."""
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        repository.edit("epics/EPC-0001-a-plan.md", "revised: 2026-01-01", "revised: 2026-02-01")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: withdrawn")
        done = repository.run("check", "relations")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("project/tasks/TSK-0001-a-task.md:6: epic EPC-0001 is withdrawn, so the citation is suspect",
                      done.stdout)


class Reported(unittest.TestCase):
    """ADR-1470: status reports what only a new record can fix, and fails on none of it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_an_approved_unconnected_artifact_is_listed_and_a_draft_is_not(self):
        """REQ-0143: an artifact nothing cites and that cites nothing is reported, once it is approved."""
        repository = self.repo()
        sections = ["Summary", "Method", "Conclusions", "Sources"]
        repository.write("research/RES-0003-alone.md", record("research", "RES-0003", {}, sections))
        repository.write("research/RES-0004-being-written.md", record("research", "RES-0004", {"status": "draft"}, sections))
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("  unconnected, citing nothing and cited by nothing: RES-0003\n", done.stdout)

    def test_a_rejected_provider_and_a_frozen_suspect_citation_are_reported(self):
        """REQ-0143: what only a new record can fix is reported by status and fails nothing."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: rejected")
        repository.edit("requirements/REQ-0001-an-obligation.md", "revised: 2026-01-01", "revised: 2026-02-01")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("  RES-0002, rejected, under 5 approved artifacts: ADR-0001, BUG-0001, EPC-0001, REQ-0001, "
                      "TSK-0001\n", done.stdout)
        self.assertIn("  3 suspect citations in approved artifacts: ADR-0001 addresses REQ-0001, BUG-0001 violates "
                      "REQ-0001, TSK-0001 closes REQ-0001\n", done.stdout)

    def test_the_share_resting_on_judgement_is_stated(self):
        """REQ-0161: the requirements in force are counted by how they are verified."""
        repository = self.repo()
        for number, verification in ((2, "behavioural"), (3, "evaluation"), (4, "judgement\nverifier: agent"),
                                     (5, "judgement\nverifier: person")):
            repository.write(f"requirements/REQ-000{number}-more.md", record(
                "requirement", f"REQ-000{number}",
                {"topic": "a", "class": "functional", "verification": verification, "elaborates": "RES-0002"}, []))
        said = repository.run("status").stdout
        self.assertIn("  by verification: 1 static, 1 behavioural, 1 evaluation, 2 judgement "
                      "(1 by an agent, 1 by a person)\n", said)
        self.assertIn("  3 of 5 rest on evaluation or judgement, not on a mechanical check\n", said)


class VerificationKind(unittest.TestCase):
    """ADR-1510: every requirement declares one of the four kinds of check."""

    def test_a_kind_outside_the_four_is_reported_on_drafts_and_approved_records(self):
        """REQ-1664: a requirement's kind of check is one the harness knows."""
        for status in ("draft", "approved"):
            repository = Repository()
            self.addCleanup(repository.tmp.cleanup)
            repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", f"status: {status}")
            repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: statc")
            done = repository.run("check", "rules")
            self.assertEqual(done.returncode, 1, status + done.stdout + done.stderr)
            self.assertIn("verification statc is not one of static, behavioural, evaluation and judgement", done.stdout)

    def test_each_of_the_four_passes(self):
        """REQ-1664: the four kinds are the whole vocabulary."""
        for kind in ("static", "behavioural", "evaluation"):
            repository = Repository()
            self.addCleanup(repository.tmp.cleanup)
            repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", f"verification: {kind}")
            done = repository.run("check", "rules")
            self.assertEqual(done.returncode, 0, kind + done.stdout + done.stderr)
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("requirements/REQ-0001-an-obligation.md", "verification: static", "verification: judgement\nverifier: agent")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 0, "judgement" + done.stdout + done.stderr)


STEPS = ("research", "requirements", "design", "spec", "epic", "cover", "implement", "document", "verify", "review")
METHOD = UNIT / "skills" / "method"
REPOSITORY = UNIT.parent.parent

# ADR-1620's table: where each step's artifact lands, as its role names it (REQ-3203).
LANDS = {
    "research": "a research record's file",
    "requirements": "one requirement record's file for each obligation",
    "design": "a decision record's file",
    "spec": "the specification's file",
    "epic": "the epic's file and each task's file",
    "cover": "the check files, the kept failing run, and the task file's cover",
    "implement": "the changed files, the kept runs, and the task file's evidence",
    "document": "each user-facing page it changed",
    "verify": "the epic's file, its verification and the evidence it cites",
    "review": "writes nothing into the repository",
}


def flat(text):
    """Lower case, no backticks or heading marks, and every run of white space one space, so a wrapped line
    reads as one and a section named as `## Cover` reads as its name."""
    return re.sub(r"\s+", " ", re.sub(r"#+\s*", "", text.replace("`", ""))).lower().strip()


def tagged(text, tag):
    found = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.DOTALL)
    return found.group(1) if found else ""


class MethodSkill(unittest.TestCase):
    """ADR-1620: the method's prompts name ten steps (REQ-3200) and where each step's artifact lands (REQ-3203)."""

    def step(self, name):
        path = METHOD / "steps" / f"{name}.md"
        self.assertTrue(path.is_file(), f"{path} doesn't exist")
        return path.read_text(encoding="utf-8")

    def assertInOrder(self, text, where):
        """The ten names appear as one list in order: `a, b, ... and z`, the last comma optional."""
        pattern = r",\s+".join(STEPS[:-1]) + r",?\s+and\s+" + STEPS[-1]
        self.assertRegex(re.sub(r"\s+", " ", text), pattern, where)

    def test_the_skill_names_ten_steps_in_order(self):
        """TSK-2550 criterion 1, REQ-3200: SKILL.md's body and description name the ten steps in order."""
        text = (METHOD / "SKILL.md").read_text(encoding="utf-8")
        front, body = text.split("\n---\n", 1)
        description = next(line for line in front.splitlines() if line.startswith("description:"))
        self.assertInOrder(description, "description")
        self.assertInOrder(body, "body")

    def test_each_step_has_one_file(self):
        """TSK-2550 criterion 1, REQ-3200: `steps/` holds one file for each of the ten steps and no other."""
        self.assertEqual(sorted(p.stem for p in (METHOD / "steps").glob("*.md")), sorted(STEPS))

    def test_each_role_names_where_its_artifact_lands(self):
        """TSK-2550 criterion 3, REQ-3203: each role names ADR-1620's committed file; review's writes nothing."""
        for name, lands in LANDS.items():
            with self.subTest(step=name):
                self.assertIn(lands, flat(tagged(self.step(name), "role")))

    def test_cover_writes_checks_only(self):
        """TSK-2550 criterion 4, REQ-3200: cover writes checks and no implementation code, sees them fail, keeps
        the run, lands the checks, fills the four lines of `## Cover`, and hands over to implement."""
        text = self.step("cover")
        whole = flat(text)
        self.assertRegex(flat(tagged(text, "role")), r"the step that picks it up is implement\b")
        self.assertIn("paw ready cover", whole)
        self.assertRegex(whole, r"\b(no|never|not)\b[^.]*\bimplementation code\b")
        self.assertRegex(whole, r"\brun\b[^.]*\bfail")
        self.assertIn("meow-verbs evidence --keep", whole)
        self.assertRegex(whole, r"\bland\b[^.]*\bchecks\b|\bchecks\b[^.]*\blanded?\b")
        self.assertIn("## Cover", text)
        for line in ("checks:", "failing run:", "landed in:", "judgement:"):
            self.assertIn(line, whole, line)

    def test_epic_hands_over_to_cover(self):
        """TSK-2550 criterion 5, REQ-3200: the epic step's role names cover as the step that picks it up."""
        self.assertRegex(flat(tagged(self.step("epic"), "role")), r"the step that picks it up is cover\b")

    def test_implement_runs_the_cover_checks(self):
        """TSK-2550 criterion 5, REQ-3200: implement's step 3 runs the cover step's checks and sees them pass,
        and no longer writes the task's checks."""
        steps = tagged(self.step("implement"), "steps")
        third = re.search(r"^3\.(.*?)(?=^\d+\.|\Z)", steps, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(third, steps)
        third = flat(third.group(1))
        self.assertIn("cover", third)
        self.assertRegex(third, r"\brun")
        self.assertRegex(third, r"\bpass")
        self.assertNotRegex(third, r"\bwrite a check\b")

    def chain(self, text):
        block = next(b for b in re.findall(r"```text\n(.*?)```", text, re.DOTALL) if "research ->" in b)
        return tuple(name.strip() for name in block.split("->")), text.split(block, 1)[0]

    def test_the_living_documents_name_ten_steps(self):
        """TSK-2550 criterion 7, REQ-3200: the chain in CLAUDE.md's own_method_first and in the vision is ten
        steps with cover between epic and implement, and the vision's sentence before it no longer says nine."""
        constitution = (REPOSITORY / "CLAUDE.md").read_text(encoding="utf-8")
        principle = tagged(constitution, "principle")
        self.assertIn("own_method_first", constitution.split(principle, 1)[0][-80:])
        self.assertEqual(self.chain(principle)[0], STEPS)
        steps, before = self.chain((REPOSITORY / "project" / "vision.md").read_text(encoding="utf-8"))
        self.assertEqual(steps, STEPS)
        introduction = before.rstrip().removesuffix("```text").rstrip().rsplit("\n\n", 1)[-1].lower()
        self.assertNotRegex(introduction, r"\bnine\b")
        self.assertRegex(introduction, r"\bten\b")


if __name__ == "__main__":
    unittest.main()
