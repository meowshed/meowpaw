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
        "spec", "SPC-0001", {"status": "live", "states": "[REQ-0001]"},
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
        "epic", "EPC-0001", {"realises": "ADR-0001"},
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
                   'project/epics/EPC-0001-a-plan.md:17: marks TSK-0001 done, and its Evidence section holds nothing past "Not yet."')

    def test_a_task_marked_done_carries_evidence(self):
        repository = self.repo()
        self.mark(repository, "x")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.found(repository.run("check", "rules"), "rules",
                   'project/epics/EPC-0001-a-plan.md:17: marks TSK-0001 done, and its Evidence section holds nothing past "Not yet."')
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nNot yet.", "## Evidence\n\nNot yet.\n\nThe fixture passed.")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_task_with_evidence_left_unmarked_is_reported(self):
        repository = self.repo()
        self.mark(repository, " ")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/epics/EPC-0001-a-plan.md:17: leaves TSK-0001 unmarked, and its Evidence section is written")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\nNot yet. Postponed by the owner.")
        self.assertEqual(repository.run("check", "coverage").returncode, 0)

    def test_a_task_closing_a_withdrawn_requirement_in_an_open_epic_is_reported(self):
        repository = self.repo()
        self.mark(repository, ">")
        repository.edit("requirements/REQ-0001-an-obligation.md", "status: approved", "status: withdrawn")
        # A living specification stating a withdrawn requirement is a finding of its own (ADR-1470).
        repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: []")
        self.found(repository.run("check", "coverage"), "coverage",
                   "project/tasks/TSK-0001-a-task.md:7: closes REQ-0001, which is withdrawn, while the task is open in EPC-0001")
        repository.edit("epics/EPC-0001-a-plan.md", "- [>] T-001", "- [x] T-001")
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

    def test_show_derives_a_requirements_state(self):
        repository = self.repo()
        self.verified(repository)
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("State\n  closed\n  TSK-0001 done in EPC-0001\n", done.stdout)
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("State\n  open, named by no task\n\n", repository.run("show", "REQ-0002").stdout)

    def test_status_counts_requirements_by_derived_state(self):
        repository = self.repo()
        self.verified(repository)
        repository.write("requirements/REQ-0002-another.md",
                         (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8").replace("REQ-0001", "REQ-0002"))
        self.assertIn("Requirements\n  2 in force: 1 closed, 0 in a task not yet done, 0 reopened by a defect, 0 postponed, 1 named by no task\n",
                      repository.run("status").stdout)

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
                   "project/specs/SPC-0001-a-part.md:21: cites REQ-0001, which is withdrawn, outside a Withdrawn section")
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
        self.assertIn("postponing: 1 requirement, listed under Postponed", status)
        self.assertIn("2 in force: 0 closed, 1 in a task not yet done, 0 reopened by a defect, 1 postponed, 0 named by no task", status)
        for check in ("rules", "coverage"):
            done = repository.run("check", check)
            self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_postponed_requirement_a_task_closes_is_no_longer_postponed(self):
        repository = self.postponing()
        repository.edit("tasks/TSK-0001-a-task.md", "    REQ-0001,", "    REQ-0001,\n    REQ-0002,")
        shown = repository.run("show", "REQ-0002").stdout
        self.assertIn("State\n  open, in a task not yet done\n", shown)
        self.assertNotIn("postponed by", shown)

    def test_a_decision_addressing_and_postponing_nothing_is_reported(self):
        repository = self.postponing(fields="postpones: []")
        self.found(repository.run("check", "rules"), "rules",
                   "project/adrs/ADR-0002-not-now.md:6: addresses no requirement and postpones none, where a decision does one or both")

    def test_a_task_added_after_approval_says_why(self):
        repository = self.repo()
        self.mark(repository, "+")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:17: marks TSK-0001 added after approval with no added: line saying why")
        repository.edit("epics/EPC-0001-a-plan.md", "closes: REQ-0001", "closes: REQ-0001\n      added: nobody foresaw the case")
        self.assertEqual(repository.run("check", "rules").returncode, 0)

    def test_a_dropped_task_keeps_its_entry_and_says_why(self):
        repository = self.repo()
        self.mark(repository, "~")
        self.found(repository.run("check", "rules"), "rules",
                   "project/epics/EPC-0001-a-plan.md:17: marks TSK-0001 dropped with no dropped: line saying why")
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

    def test_implement_refuses_until_its_dependency_is_done(self):
        repository = self.repo()
        repository.write("tasks/TSK-0002-a-second-task.md", CLEAN["tasks/TSK-0001-a-task.md"]
                         .replace("TSK-0001", "TSK-0002").replace("## Depends on\n\nText.", "## Depends on\n\nTSK-0001."))
        self.mark(repository, " ")
        done = self.ready(repository, "implement", "TSK-0002")
        self.assertEqual(done.returncode, 1)
        self.assertIn("TSK-0001, which TSK-0002 depends on, isn't done", done.stdout)
        self.mark_done(repository)
        self.assertEqual(self.ready(repository, "implement", "TSK-0002").returncode, 0)

    def mark_done(self, repository):
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")

    def test_implement_refuses_a_task_whose_epic_is_a_draft(self):
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "status: approved", "status: draft")
        done = self.ready(repository, "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1)
        self.assertIn("EPC-0001, the epic of TSK-0001, is draft and not approved", done.stdout)

    def test_review_needs_no_verification(self):
        """ADR-2300: nothing writes checked-at, so review doesn't wait on it."""
        done = self.ready(self.repo(), "review", "EPC-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_status_leads_with_drafts_and_places_each_decision(self):
        """REQ-3202, REQ-3638: an open task is placed at implement (REQ-0321 for the drafts)."""
        repository = self.repo()
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        self.mark(repository, " ")
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout)
        lines = done.stdout.splitlines()
        self.assertEqual(lines[0], "Waiting for approval")
        self.assertIn("RES-0002 research, draft", lines[1])
        self.assertIn("next: implement TSK-0001 (EPC-0001, 0 of 1 task done)", done.stdout)
        self.mark_done(repository)
        self.assertIn("closed: EPC-0001 (1 task done)", repository.run("status").stdout)

    def test_status_places_a_decision_with_no_epic(self):
        repository = self.repo()
        (repository.root / "epics" / "EPC-0001-a-plan.md").unlink()
        self.assertIn("next: spec, then epic", repository.run("status").stdout)

    def test_status_prints_the_same_state_twice(self):
        """REQ-0210: status prints the same text twice, with an open task or with none."""
        repository = self.repo()
        first = repository.run("status").stdout
        self.assertIn("ADR-0001", first)
        self.assertEqual(first, repository.run("status").stdout)
        self.mark(repository, " ")
        first = repository.run("status").stdout
        self.assertIn("next: implement TSK-0001 (EPC-0001, 0 of 1 task done)", first)
        self.assertEqual(first, repository.run("status").stdout)

    def cover(self, repository):
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence",
                        "## Acceptance criteria\n\n" + CRITERIA + "\n\n## Cover\n\n" + FILLED + "\n\n## Evidence")
        for name in ("tests/test_a_task.py", "project/evidence/a-failing-run.txt"):
            path = repository.path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("A file.\n", encoding="utf-8")

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

    def test_the_bug_template_names_no_retired_step(self):
        """REQ-3638: the bug template's `enters` comment names no step a draft is refused for."""
        enters = [line for line in self.template("bug").splitlines() if line.startswith("enters:")]
        self.assertEqual(len(enters), 1, enters)
        self.assertNotRegex(enters[0].split("#", 1)[1], r"\b(cover|document|verify)\b")


FILLED = """- Checks: tests/test_a_task.py
- Failing run: project/evidence/a-failing-run.txt
- Landed in: #12
- Judgement: 2: whether the page reads well rests on a reader"""

CRITERIA = """1. Given a task, then a check passes.
   Closed by: tests/test_a_task.py.
2. Given a page, then it reads well.
3. Given a table, then it is ordered as a reader expects.
   Closed by: tests/test_a_task.py."""


class TasklessEpic(unittest.TestCase):
    """BUG-1250: `ready` and `status` read an epic that lists no tasks the same way (REQ-0208)."""

    def repo(self, named):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        if named:
            repository.edit("epics/EPC-0001-a-plan.md", "## Not covered\n\nText.",
                            "## Not covered\n\n- REQ-0001 is closed by a task another record carries.")
        return repository

    def test_status_names_document_and_ready_agrees(self):
        """TSK-2560 criterion 2, REQ-3620: a taskless epic naming everything is closed."""
        repository = self.repo(named=True)
        self.assertIn("closed: EPC-0001 (0 tasks done)", repository.run("status").stdout)

    def test_an_epic_leaving_a_requirement_unnamed_is_refused_by_both(self):
        """TSK-2560 criterion 3: status waits on a taskless epic that leaves a requirement unnamed."""
        repository = self.repo(named=False)
        reason = "EPC-0001 lists no tasks, and REQ-0001, which ADR-0001 addresses, isn't named under Not covered"
        status = repository.run("status").stdout
        self.assertIn(f"waiting: {reason}", status)
        self.assertNotIn("closed: EPC-0001", status)


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

    def test_a_task_may_say_what_it_left_alone(self):
        """The implementer fills `## Left alone` after approval, as the template asks, so it is free like Evidence."""
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Left alone\n\nText.", "## Left alone\n\nThe index, because nothing moved.")
        done = self.frozen(repository)
        self.assertEqual(done.returncode, 0, done.stdout)

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
        done = self.repo(mark=" ").run("ready", "implement", "TSK-0002")
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


class Dependencies(unittest.TestCase):
    """ADR-1800 and SPC-1090 "The gate": each dependency line says whether it blocks, and `paw` waits only on
    the blocking ones (REQ-1358). A bare line on an approved task keeps blocking, and a draft is asked to mark it.
    """

    TASK = "tasks/TSK-0002-a-second-task.md"

    def repo(self, lines, status="approved", first=False):
        """TSK-0002 depends on TSK-0001 through `lines`; both are open under EPC-0001. With `first`, the epic
        lists TSK-0002 ahead of TSK-0001, so `status` reaches it first."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        task = CLEAN["tasks/TSK-0001-a-task.md"].replace("TSK-0001", "TSK-0002").replace(
            "## Depends on\n\nText.", "## Depends on\n\n" + "\n".join(lines)).replace(
            "status: approved", f"status: {status}").replace(
            "## Evidence", "## Acceptance criteria\n\n" + CRITERIA + "\n\n## Cover\n\n" + FILLED + "\n\n## Evidence")
        repository.write(self.TASK, task)
        entries = ["- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001",
                   "- [ ] T-002 TSK-0002 the second task\n      closes: REQ-0001"]
        if first:
            entries = ["- [ ] T-001 TSK-0002 the second task\n      closes: REQ-0001",
                       "- [ ] T-002 TSK-0001 the task\n      closes: REQ-0001"]
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n" + "\n\n".join(entries))
        for name in ("tests/test_a_task.py", "project/evidence/a-failing-run.txt"):
            path = repository.path / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("A file.\n", encoding="utf-8")
        return repository

    # `dependency-declared`'s messages, so each test shows the line reported by that rule and by no other (BUG-1300).
    UNMARKED = "names a dependency without (blocking) or (not blocking), where each line says whether it blocks"
    TWO = "names 2 tasks on one dependency line, where each line names one task and says whether it blocks"

    def line_of(self, repository, text):
        lines = (repository.root / self.TASK).read_text(encoding="utf-8").splitlines()
        return f"{self.TASK.split('/')[1]}:{lines.index(text) + 1}:"

    def test_a_declared_dependency_passes(self):
        """TSK-2900 criterion 1, REQ-1358: a draft's `(blocking)` and `(not blocking)` lines are reported by no
        rule, while a variant such as `(non-blocking)` is reported by line under `dependency-declared`."""
        declared = ["- TSK-0001 (not blocking): shares a helper", "- TSK-0003 (blocking): the parser lands there"]
        variant = "- TSK-0004 (non-blocking): shares a fixture"
        repository = self.repo(declared + [variant], status="draft")
        done = repository.run("check", "rules")
        for line in declared:
            self.assertNotIn(self.line_of(repository, line), done.stdout, line)
        self.assertIn(self.line_of(repository, variant) + " " + self.UNMARKED, done.stdout, done.stdout + done.stderr)

    def test_a_bare_dependency_in_a_draft_is_reported(self):
        """TSK-2900 criterion 1, REQ-1358: a draft's bare `- TSK-NNNN` line is reported by its line number
        under `dependency-declared`."""
        bare = "- TSK-0001"
        repository = self.repo(["- TSK-0003 (not blocking): shares a helper", bare], status="draft")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(self.line_of(repository, bare) + " " + self.UNMARKED, done.stdout)

    def test_a_line_naming_two_tasks_is_reported(self):
        """TSK-2900 criterion 1, REQ-1358: a draft's line naming two identifiers is reported by its line number,
        even when it carries a marker."""
        two = "- TSK-0001 and TSK-0003 (blocking): both land the parser"
        repository = self.repo([two], status="draft")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(self.line_of(repository, two) + " " + self.TWO, done.stdout)

    def test_an_approved_bare_dependency_still_blocks(self):
        """TSK-2900 criterion 2, REQ-1358: an approved task's bare line is not reported and `ready implement`
        still waits on it, while the same line in a draft is reported, because `dependency-declared` is a draft
        rule (ADR-1140)."""
        bare = "- TSK-0001"
        repository = self.repo([bare])
        checked = repository.run("check", "rules")
        self.assertNotIn(self.line_of(repository, bare), checked.stdout)
        done = repository.run("ready", "implement", "TSK-0002")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("TSK-0001, which TSK-0002 depends on, isn't done", done.stdout)
        draft = self.repo([bare], status="draft")
        self.assertIn(self.line_of(draft, bare), draft.run("check", "rules").stdout)

    def test_a_not_blocking_dependency_leaves_the_task_ready(self):
        """TSK-2900 criterion 3, REQ-1358: a task whose only open dependency is `(not blocking)` is ready to
        cover and to implement."""
        repository = self.repo(["- TSK-0001 (not blocking): shares a helper"])
        for step in ("implement",):
            done = repository.run("ready", step, "TSK-0002")
            self.assertEqual(done.returncode, 0, step + done.stdout + done.stderr)
            self.assertNotIn("TSK-0001, which TSK-0002 depends on", done.stdout, step)

    def test_a_blocking_dependency_makes_the_task_wait(self):
        """TSK-2900 criterion 3, REQ-1358: the same dependency marked `(blocking)` keeps `ready cover` and
        `ready implement` waiting on it, and only the marker separates the two outcomes."""
        for marker, code in (("blocking", 1), ("not blocking", 0)):
            repository = self.repo([f"- TSK-0001 ({marker}): the parser lands there"])
            for step in ("implement",):
                done = repository.run("ready", step, "TSK-0002")
                self.assertEqual(done.returncode, code, marker + " " + step + done.stdout + done.stderr)
                named = "TSK-0001, which TSK-0002 depends on, isn't done"
                (self.assertIn if code else self.assertNotIn)(named, done.stdout, marker + " " + step)

    def test_status_names_a_task_whose_only_dependency_does_not_block(self):
        """TSK-2900 criterion 3, REQ-1358: `paw status` names as next the first task whose only open
        dependency is `(not blocking)`."""
        repository = self.repo(["- TSK-0001 (not blocking): shares a helper"], first=True)
        done = repository.run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertRegex(done.stdout, r"next: \w+ TSK-0002 \(EPC-0001, 0 of 2 tasks done\)")

    def test_status_waits_on_a_blocking_dependency(self):
        """TSK-2920 criterion 1, BUG-1300, REQ-1358: with the epic listing TSK-0002 first, a `(blocking)` line
        and an approved task's bare line each make `paw status` pass over TSK-0002 and name TSK-0001, so only the
        marker separates this outcome from the `(not blocking)` one above."""
        for lines in (["- TSK-0001 (blocking): the parser lands there"], ["- TSK-0001"]):
            with self.subTest(lines=lines):
                done = self.repo(lines, first=True).run("status")
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                self.assertRegex(done.stdout, r"next: \w+ TSK-0001 \(EPC-0001, 0 of 2 tasks done\)")
                self.assertNotRegex(done.stdout, r"next: \w+ TSK-0002")

    def defect_epic(self, task_lines, depends=None):
        """An epic realising BUG-0001 with two tasks, ordered only by `task_lines` or by an entry's `depends:`."""
        repository = self.repo(task_lines)
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: BUG-0001")
        if depends is not None:
            repository.edit("epics/EPC-0001-a-plan.md", "the second task\n      closes: REQ-0001",
                            f"the second task\n      closes: REQ-0001\n      depends: {depends}")
        return repository.run("check", "rules").stdout

    UNORDERED = "realises the defect BUG-0001 with 2 tasks and no order between them"

    def test_a_not_blocking_order_does_not_order_a_defects_epic(self):
        """TSK-2900 criterion 4, REQ-1358: a task's line and an epic entry's `depends:` marked `(not blocking)`
        are no order, so `defect-epic-ordered` reports each epic."""
        said = self.defect_epic(["- TSK-0001 (not blocking): shares a helper"])
        self.assertIn(self.UNORDERED, said)
        said = self.defect_epic(["Nothing."], depends="TSK-0001 (not blocking) - shares a helper")
        self.assertIn(self.UNORDERED, said)

    def test_a_blocking_order_orders_a_defects_epic(self):
        """TSK-2900 criterion 4, REQ-1358: `(blocking)` on the task's line or the entry's `depends:`, or an
        unmarked `depends:`, orders the epic, and only the marker separates it from the reported one."""
        for lines, depends in ((["- TSK-0001 (blocking): the parser lands there"], None),
                               (["Nothing."], "TSK-0001 (blocking) - the parser lands there"),
                               (["Nothing."], "TSK-0001 - the parser lands there")):
            self.assertNotIn(self.UNORDERED, self.defect_epic(lines, depends), (lines, depends))
        self.assertIn(self.UNORDERED, self.defect_epic(["- TSK-0001 (not blocking): shares a helper"]))

    def test_the_templates_and_the_epic_step_show_both_markers(self):
        """TSK-2900 criterion 5, REQ-1358: the task and epic templates show both markers and no longer say a
        convenience isn't a dependency, and the epic step holds a rule beside E6 to declare one as not blocking."""
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        texts = {}
        for kind in ("task", "epic"):
            done = repository.run("template", kind)
            self.assertEqual(done.returncode, 0, done.stderr)
            texts[kind] = Path(done.stdout.strip()).read_text(encoding="utf-8")
        depends_on = texts["task"].split("## Depends on", 1)[1].split("\n## ", 1)[0]
        self.assertIn("(blocking)", depends_on)
        self.assertIn("(not blocking)", depends_on)
        self.assertRegex(texts["epic"], r"depends: TSK-NNNN \(not blocking\) - why")
        for kind, text in texts.items():
            self.assertNotRegex(flat(text).lower(), r"convenience isn.t a dependency", kind)
        rules = tagged((METHOD / "steps" / "epic.md").read_text(encoding="utf-8"), "rules")
        items = re.findall(r"^- (E\d+)\.(.*?)(?=^- E\d+\.|\Z)", rules, re.MULTILINE | re.DOTALL)
        names = [name for name, _ in items]
        self.assertIn("E6", names)
        at = names.index("E6")
        beside = [flat(body) for _, body in items[max(at - 1, 0):at + 2]]
        self.assertTrue(any("convenience" in body and "not blocking" in body and re.search(r"\breason|\bwhy\b", body)
                            for body in beside), beside)


STEPS = ("research", "requirements", "design", "spec", "epic", "implement", "review")
METHOD = UNIT / "skills" / "method"
REPOSITORY = UNIT.parent.parent

# Where each step's artifact lands, as a path pattern under the record root the profile resolves (REQ-3203,
# BUG-1264). Document and review are read apart: a page isn't under the record root, and review writes nothing.
LANDS = {
    "research": ["research/res-nnnn-<topic>.md"],
    "requirements": ["requirements/req-nnnn-<slug>.md"],
    "design": ["adrs/adr-nnnn-<slug>.md"],
    "spec": ["specs/spc-nnnn-<topic>.md"],
    "epic": ["epics/epc-nnnn-<slug>.md", "tasks/tsk-nnnn-<slug>.md"],
    "implement": ["tasks/tsk-nnnn-<slug>.md", "evidence", "test files", "user-facing page"],
}
RECORD_ROOT = ("[record] root", ".meowpaw/profile.toml", "project/")


def flat(text):
    """Lower case, no backticks or heading marks, and every run of white space one space, so a wrapped line
    reads as one and a section named as `## Cover` reads as its name."""
    return re.sub(r"\s+", " ", re.sub(r"#+\s*", "", text.replace("`", ""))).lower().strip()


OUTCOMES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED")


def word_in(word, text):
    """Whether `text` names the outcome `word` as a whole word, so DONE_WITH_CONCERNS doesn't name DONE."""
    return re.search(rf"(?<![A-Za-z_]){word}(?![A-Za-z_])", text) is not None


def outcomes_named(text):
    return {w for w in OUTCOMES if word_in(w, text)}


def sentences(text):
    """Each sentence of a prompt, with a list item and a table row each ending one, white space made single and
    backticks dropped, so a rule is read clause by clause whether it is prose, a list or a table."""
    out = []
    for part in re.split(r"\n(?=\s*(?:[-|*]|\d+\.)\s)|\n\s*\n", text):
        part = re.sub(r"\s+", " ", part.replace("`", "")).strip()
        out.extend(s for s in re.split(r"(?<=[.;])\s+", part) if s)
    return out


def together(text, word, pattern):
    """Whether one sentence of `text` names the outcome `word` and matches `pattern`, ignoring case."""
    return any(word_in(word, s) and re.search(pattern, s, re.IGNORECASE) for s in sentences(text))


def tagged(text, tag):
    found = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, re.DOTALL)
    return found.group(1) if found else ""


class Grouping(unittest.TestCase):
    """ADR-1800 and SPC-1070 "The layout": the task, epic and defect kinds forbid every grouping field, and the
    epic kind forbids `epic`, so a task sits under its epic or its defect and nothing else (REQ-3320)."""

    TASK = "tasks/TSK-0001-a-task.md"
    EPIC = "epics/EPC-0001-a-plan.md"
    BUG = "bugs/BUG-0001-a-defect.md"

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def reported(self, repository, name, field):
        """`paw check` exits 1 and names the file, the field's line and the field. Line 7 is the first line after
        the fixture's own fields, where each test writes the grouping field."""
        done = repository.run("check")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(f"project/{name}:7: carries {field},", done.stdout)
        return done

    def test_a_task_with_a_milestone_is_reported(self):
        """TSK-2910 criterion 1, REQ-3320: a task carrying `milestone:` is reported by file and field, whatever
        its status, so the draft is reported as the approved one is."""
        repository = self.repo()
        repository.edit(self.TASK, "status: approved\nrevised: 2026-01-01\nepic: EPC-0001",
                        "status: draft\nrevised: 2026-01-01\nepic: EPC-0001\nmilestone: v1")
        self.reported(repository, self.TASK, "milestone")

    def test_an_epic_with_a_parent_is_reported(self):
        """TSK-2910 criterion 1, REQ-3320: an epic carrying `parent:` is reported by file and field."""
        repository = self.repo()
        repository.edit(self.EPIC, "realises: ADR-0001", "realises: ADR-0001\nparent: EPC-0002")
        self.reported(repository, self.EPIC, "parent")

    def test_a_task_under_its_epic_or_defect_passes(self):
        """TSK-2910 criterion 1, REQ-3320: a task naming `epic:`, or `bug:` in its place, and no grouping field
        is not reported, so the forbidden list doesn't reach the fields that place a task. The epic carries
        `parent:` in the same run, so the check is shown reporting a grouping field and passing the task, and a
        run that reports no grouping field anywhere doesn't pass."""
        for field in ("epic: EPC-0001", "bug: BUG-0001"):
            with self.subTest(field=field):
                repository = self.repo()
                repository.edit(self.TASK, "epic: EPC-0001", field)
                repository.edit(self.EPIC, "realises: ADR-0001", "realises: ADR-0001\nparent: EPC-0002")
                done = self.reported(repository, self.EPIC, "parent")
                self.assertNotIn("TSK-0001", done.stdout, done.stdout)
                self.assertEqual(done.stdout.count("carries"), 1, done.stdout)

    def test_an_approved_task_with_a_label_is_reported(self):
        """TSK-2910 criterion 2, REQ-3320: an approved task carrying `label:` is reported, because a forbidden
        field reaches every record and not only a draft."""
        repository = self.repo()
        repository.edit(self.TASK, "epic: EPC-0001", "epic: EPC-0001\nlabel: urgent")
        self.assertIn("status: approved", (repository.root / self.TASK).read_text(encoding="utf-8"))
        self.reported(repository, self.TASK, "label")

    def test_a_defect_with_a_milestone_is_reported(self):
        """TSK-2910 criterion 3, REQ-3320: a defect carrying `milestone:` is reported by file and field."""
        repository = self.repo()
        repository.edit(self.BUG, "violates: REQ-0001", "violates: REQ-0001\nmilestone: v1")
        self.reported(repository, self.BUG, "milestone")

    # ADR-1800's forbidden groupings, and the fixture's last field on each kind, after which a test writes one.
    GROUPINGS = ("milestone", "parent", "project", "sprint", "iteration", "label", "labels")
    PLACES = {TASK: ("epic: EPC-0001", GROUPINGS), EPIC: ("realises: ADR-0001", ("epic",) + GROUPINGS),
              BUG: ("violates: REQ-0001", GROUPINGS)}

    def test_every_grouping_field_is_reported_on_every_kind(self):
        """TSK-2930 criterion 1, BUG-1301, REQ-3320: each field ADR-1800 forbids, on each kind it forbids it on, is
        reported by file, line and field, so a layout that drops one field from one kind fails here."""
        for name, (last, fields) in self.PLACES.items():
            for field in fields:
                with self.subTest(kind=name, field=field):
                    repository = self.repo()
                    repository.edit(name, last, f"{last}\n{field}: x")
                    self.reported(repository, name, field)

    def test_an_epic_under_an_epic_is_reported(self):
        """TSK-2910 criterion 3, REQ-3320: an epic carrying `epic:` is reported, because only an epic would place
        one epic under another."""
        repository = self.repo()
        repository.edit(self.EPIC, "realises: ADR-0001", "realises: ADR-0001\nepic: EPC-0002")
        self.reported(repository, self.EPIC, "epic")


class MethodSkill(unittest.TestCase):
    """ADR-2300: the method's prompts name seven steps (REQ-3638) and where each step's artifact lands (REQ-3203)."""

    def step(self, name):
        path = METHOD / "steps" / f"{name}.md"
        self.assertTrue(path.is_file(), f"{path} doesn't exist")
        return path.read_text(encoding="utf-8")

    def assertInOrder(self, text, where):
        """The ten names appear as one list in order: `a, b, ... and z`, the last comma optional."""
        pattern = r",\s+".join(STEPS[:-1]) + r",?\s+and\s+" + STEPS[-1]
        self.assertRegex(re.sub(r"\s+", " ", text), pattern, where)

    def test_each_role_names_where_its_artifact_lands(self):
        """REQ-3203: each role names its path pattern under the record root, implement its tests, pages and
        Evidence, and review nothing."""
        for name, patterns in LANDS.items():
            role = flat(tagged(self.step(name), "role"))
            for phrase in RECORD_ROOT + tuple(patterns):
                with self.subTest(step=name, phrase=phrase):
                    self.assertIn(phrase, role)
        self.assertIn("writes no finding into the record", flat(tagged(self.step("review"), "role")))

    def chain(self, text):
        block = next(b for b in re.findall(r"```text\n(.*?)```", text, re.DOTALL) if "research ->" in b)
        return tuple(name.strip() for name in block.split("->")), text.split(block, 1)[0]

    def test_the_living_documents_name_the_chain(self):
        """REQ-3638: the chain in CLAUDE.md's own_method_first and in the vision is the seven steps, and the
        vision's sentence before it says seven."""
        constitution = (REPOSITORY / "CLAUDE.md").read_text(encoding="utf-8")
        principle = tagged(constitution, "principle")
        self.assertIn("own_method_first", constitution.split(principle, 1)[0][-80:])
        self.assertEqual(self.chain(principle)[0], STEPS)
        steps, before = self.chain((REPOSITORY / "project" / "vision.md").read_text(encoding="utf-8"))
        self.assertEqual(steps, STEPS)
        introduction = before.rstrip().removesuffix("```text").rstrip().rsplit("\n\n", 1)[-1].lower()
        self.assertNotRegex(introduction, r"\b(nine|ten)\b")
        self.assertRegex(introduction, r"\bseven\b")


AGENTS = UNIT / "agents"


class AgentReports(unittest.TestCase):
    """TSK-2702 criterion 3, REQ-0816, SPC-1030 "What an agent reports" and SPC-1090's rows for each agent:
    `record-reviewer` and `router` state when they report each outcome and where the outcome and cause go, and
    `record-reviewer` quotes no more than the span a finding names, 25 words at most."""

    def agent(self, name):
        return (AGENTS / f"{name}.md").read_text(encoding="utf-8").split("---\n", 2)[2]

    def when(self, text, rows):
        for word, pattern in rows:
            with self.subTest(outcome=word):
                self.assertTrue(together(text, word, pattern), f"no sentence says when {word} is reported ({pattern})")

    def test_the_router_names_the_four_outcomes(self):
        """TSK-2702 criterion 3, REQ-0816: router names DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT and BLOCKED."""
        self.assertEqual(outcomes_named(self.agent("router")), set(OUTCOMES))

    def test_the_router_says_when_it_reports_each_outcome(self):
        """TSK-2702 criterion 3, REQ-0816, SPC-1090 "The route": DONE where every change has a size and a shape;
        DONE_WITH_CONCERNS where a file or index its steps name couldn't be found; NEEDS_CONTEXT where the request
        names no change it can route; BLOCKED where a tool call was denied."""
        self.when(self.agent("router"), (
            ("DONE", r"size and (a )?shape|every change"),
            ("DONE_WITH_CONCERNS", r"could ?n.t (be )?f(ou)?nd|not found|missing"),
            ("NEEDS_CONTEXT", r"no change|names nothing|nothing (it|you) can route"),
            ("BLOCKED", r"denied"),
        ))

    def test_the_routers_first_field_is_outcome_and_cause_follows_it(self):
        """TSK-2702 criterion 3, REQ-0816, SPC-1030 "What an agent reports": the router's first field is outcome:,
        before size:, and a cause: field follows it."""
        fields = re.findall(r"^\s*- `([a-z ]+):`", tagged(self.agent("router"), "rules"), re.MULTILINE)
        self.assertTrue(fields, "the router's rules list no fields")
        self.assertEqual(fields[0], "outcome", fields)
        self.assertIn("cause", fields)
        self.assertLess(fields.index("outcome"), fields.index("cause"))
        self.assertLess(fields.index("outcome"), fields.index("size"))


class RequirementState(unittest.TestCase):
    """TSK-3800, ADR-2300: a requirement's state comes from the tasks, epics and defects that name it."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def tasks(self, repository, *entries):
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n" + "\n\n".join(entries))

    def second_requirement(self, repository, addressed=True):
        text = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0002-another.md", text.replace("REQ-0001", "REQ-0002"))
        if addressed:
            repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", "addresses: [REQ-0001, REQ-0002]")
            repository.edit("specs/SPC-0001-a-part.md", "states: [REQ-0001]", "states: [REQ-0001, REQ-0002]")

    def second_task(self, repository, closes):
        text = (repository.root / "tasks/TSK-0001-a-task.md").read_text(encoding="utf-8")
        text = text.replace("TSK-0001", "TSK-0002").replace("\n  [\n    REQ-0001,\n  ]", f" [{closes}]")
        repository.write("tasks/TSK-0002-another.md", text)

    def test_a_requirement_whose_only_task_is_done_is_closed(self):
        """REQ-3600, REQ-3602: done with no checked-at is closed, and nothing says verified."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        done = repository.run("show", "REQ-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("State\n  closed\n  TSK-0001 done in EPC-0001\n", done.stdout)
        self.assertNotIn("verified", done.stdout)

    def test_a_requirement_with_one_open_task_of_two_is_open(self):
        """REQ-3600, REQ-3648: a second task naming the requirement keeps it open until it is done."""
        repository = self.repo()
        self.second_task(repository, "REQ-0001")
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001",
                   "- [ ] T-002 TSK-0002 another\n      closes: REQ-0001")
        self.assertIn("State\n  open, in a task not yet done\n", repository.run("show", "REQ-0001").stdout)

    def test_a_requirement_no_task_names_is_open(self):
        """REQ-3608: nothing naming it leaves it open, never closed."""
        repository = self.repo()
        self.second_requirement(repository, addressed=False)
        self.assertIn("State\n  open, named by no task\n", repository.run("show", "REQ-0002").stdout)

    def test_an_open_defect_reopens_a_closed_requirement(self):
        """REQ-3610: an open defect naming the requirement in violates reopens it."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit("bugs/BUG-0001-a-defect.md", "## Closed by\n\nText.", "## Closed by\n\nNot closed.")
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)

    def defect_tasks(self, repository, *marks):
        entries = "\n".join(f"- [{m}] T-00{i} TSK-000{i + 5} a fix" for i, m in enumerate(marks, 1))
        repository.edit("bugs/BUG-0001-a-defect.md", "## Closed by\n\nText.",
                        f"## Closed by\n\nNot closed.\n\n## Tasks\n\n{entries}")

    def test_a_defect_whose_tasks_are_done_is_closed(self):
        """REQ-3610: a defect closes with its tasks, whatever its Closed by says, and the requirement closes again."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        self.defect_tasks(repository, "x")
        self.assertIn("State\n  closed\n", repository.run("show", "REQ-0001").stdout)

    def test_a_defect_with_an_open_task_is_open(self):
        """REQ-3610: one open fix task keeps the defect open, and its requirement with it."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        self.defect_tasks(repository, "x", " ")
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)

    def test_a_defect_whose_fixes_were_all_dropped_is_open(self):
        """REQ-3610: dropping every fix closes nothing, as it closes no requirement."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        self.defect_tasks(repository, "~")
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)

    def test_a_draft_defect_with_no_task_is_open(self):
        """REQ-3610: a defect still being written is open, whatever its Closed by says."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit("bugs/BUG-0001-a-defect.md", "status: approved", "status: draft")
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)

    def test_a_defect_an_epic_realises_closes_with_the_epics_tasks(self):
        """REQ-3610: a defect realised by an epic is open while the epic's tasks are, and closed once one is done."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit("bugs/BUG-0001-a-defect.md", "## Closed by\n\nText.", "## Closed by\n\nNot closed.")
        epic = (repository.root / "epics/EPC-0001-a-plan.md").read_text(encoding="utf-8")
        epic = epic.replace("EPC-0001", "EPC-0002").replace("realises: ADR-0001", "realises: BUG-0001")
        repository.write("epics/EPC-0002-the-fix.md", epic.replace("- [x] T-001 TSK-0001", "- [ ] T-001 TSK-0007"))
        self.assertIn("State\n  open, violated by BUG-0001\n", repository.run("show", "REQ-0001").stdout)
        repository.edit("epics/EPC-0002-the-fix.md", "- [ ] T-001 TSK-0007", "- [x] T-001 TSK-0007")
        self.assertIn("State\n  closed\n", repository.run("show", "REQ-0001").stdout)

    def test_tasks_and_requirements_relate_many_to_many(self):
        """REQ-3646, REQ-3648: two tasks naming one requirement, and one naming three, is no coverage finding."""
        repository = self.repo()
        self.second_requirement(repository)
        text = (repository.root / "requirements/REQ-0001-an-obligation.md").read_text(encoding="utf-8")
        repository.write("requirements/REQ-0003-a-third.md", text.replace("REQ-0001", "REQ-0003"))
        repository.edit("adrs/ADR-0001-a-choice.md", "REQ-0001, REQ-0002]", "REQ-0001, REQ-0002, REQ-0003]")
        repository.edit("specs/SPC-0001-a-part.md", "REQ-0001, REQ-0002]", "REQ-0001, REQ-0002, REQ-0003]")
        self.second_task(repository, "REQ-0001, REQ-0002, REQ-0003")
        for task in ("tasks/TSK-0001-a-task.md", "tasks/TSK-0002-another.md"):
            repository.edit(task, "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.tasks(repository, "- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001",
                   "- [ ] T-002 TSK-0002 another\n      closes: REQ-0001, REQ-0002, REQ-0003")
        done = repository.run("check", "coverage")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_status_counts_requirements_by_their_state(self):
        """REQ-3600, REQ-3602, REQ-3608: the counts name closed and open, and no verified state."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        self.second_requirement(repository, addressed=False)
        self.assertIn("Requirements\n  2 in force: 1 closed, 0 in a task not yet done, 0 reopened by a defect, "
                      "0 postponed, 1 named by no task\n", repository.run("status").stdout)

    def test_status_closes_an_epic_whose_tasks_are_done(self):
        """REQ-3604, REQ-3620: every task done closes the epic, and no document or verify step is named."""
        repository = self.repo()
        self.tasks(repository, "- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        status = repository.run("status").stdout
        self.assertIn("closed: EPC-0001 (1 task done)", status)
        self.assertNotIn("verify", status)
        self.assertNotIn("document", status)

    def postpone(self, repository, reverse):
        self.second_requirement(repository, addressed=False)
        decision = (repository.root / "adrs/ADR-0001-a-choice.md").read_text(encoding="utf-8")
        decision = decision.replace("ADR-0001", "ADR-0002").replace("addresses: [REQ-0001]", "addresses: []\npostpones: [REQ-0002]")
        repository.write("adrs/ADR-0002-not-now.md", decision.replace("## What would reverse it\n\nText.", f"## What would reverse it\n\n{reverse}"))

    def test_status_lists_each_postponement_with_its_condition(self):
        """REQ-3622: status lists each postponed requirement with the first entry of the decision's What would reverse it."""
        repository = self.repo()
        self.postpone(repository, "- A second repository\n  asks for it.\n- The owner asks.")
        self.assertIn("Postponed\n  REQ-0002 by ADR-0002, until: A second repository asks for it.\n\n",
                      repository.run("status").stdout)

    def test_a_numbered_condition_is_read_to_its_first_item(self):
        """REQ-3622: a numbered list with no blank lines is read to its first item."""
        repository = self.repo()
        self.postpone(repository, "1. A second repository asks.\n2. The owner asks.")
        self.assertIn("  REQ-0002 by ADR-0002, until: A second repository asks.\n\n", repository.run("status").stdout)

    def test_a_postponement_whose_task_was_dropped_is_listed_and_counted_alike(self):
        """REQ-3622: a requirement whose only task is dropped is postponed in the count and in the list."""
        repository = self.repo()
        self.postpone(repository, "- The owner asks.")
        repository.edit("tasks/TSK-0001-a-task.md", "    REQ-0001,", "    REQ-0001,\n    REQ-0002,")
        self.tasks(repository, "- [~] T-001 TSK-0001 the task\n      closes: REQ-0001, REQ-0002\n      dropped: not now")
        status = repository.run("status").stdout
        self.assertIn("1 postponed", status)
        self.assertIn("  REQ-0002 by ADR-0002, until: The owner asks.\n", status)


class SevenSteps(unittest.TestCase):
    """TSK-3810, ADR-2300: `paw` knows seven steps, reads no Cover, and lets a task realise a decision."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_an_unknown_step_names_the_seven(self):
        """REQ-3638: the steps are research, requirements, design, spec, epic, implement and review."""
        done = self.repo().run("ready", "bogus", "TSK-0001")
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("the steps are research, requirements, design, spec, epic, implement, review\n", done.stderr)

    def test_a_retired_step_is_an_unknown_step(self):
        """TSK-4060 criterion 1, REQ-3004, ADR-2350: cover, document and verify are refused as any step `paw ready`
        doesn't know, with exit 2 and the seven steps in order and nothing else, so `bogus` gets the same line with
        its own name and no pointer follows any of them."""
        repository = self.repo()
        for step in ("cover", "document", "verify", "bogus"):
            with self.subTest(step=step):
                done = repository.run("ready", step, "TSK-0001")
                self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
                self.assertEqual(done.stdout, "")
                self.assertEqual(done.stderr, f"paw ready: no step is named {step}; the steps are research, "
                                              "requirements, design, spec, epic, implement, review\n")

    def test_implement_reads_no_cover(self):
        """REQ-3616: an approved task with no Cover section is ready to implement."""
        repository = self.repo()
        text = (repository.root / "tasks/TSK-0001-a-task.md").read_text(encoding="utf-8")
        self.assertNotIn("## Cover", text)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def direct(self, repository, evidence="Not yet."):
        (repository.root / "epics/EPC-0001-a-plan.md").unlink()
        repository.edit("README.md", "- EPC-0001\n", "")
        repository.edit("tasks/TSK-0001-a-task.md", "epic: EPC-0001", "realises: ADR-0001")
        repository.edit("tasks/TSK-0001-a-task.md", "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n", "\n")
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", f"## Evidence\n\n{evidence}")

    def test_a_task_realises_a_decision_with_no_epic(self):
        """REQ-3630: a task naming `realises: ADR-NNNN` and no epic passes every check and is next to implement."""
        repository = self.repo()
        self.direct(repository)
        done = repository.run("check")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("next: implement TSK-0001 (ADR-0001, 0 of 1 task done)", repository.run("status").stdout)
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)

    def test_a_draft_task_may_realise_a_decision(self):
        """REQ-3630: `realises` counts as the one authority a draft names."""
        repository = self.repo()
        self.direct(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        done = repository.run("check", "rules")
        self.assertEqual(done.returncode, 0, done.stdout)

    def second_direct(self, repository, status="approved", evidence="Not yet.", extra=""):
        text = (repository.root / "tasks/TSK-0001-a-task.md").read_text(encoding="utf-8")
        text = text.replace("TSK-0001", "TSK-0002").replace("epic: EPC-0001", f"realises: ADR-0001{extra}")
        text = text.replace("status: approved", f"status: {status}").replace("## Evidence\n\nText.", f"## Evidence\n\n{evidence}")
        repository.write("tasks/TSK-0002-direct.md", text.replace("\nSee [the plan](../epics/EPC-0001-a-plan.md).\n", "\n"))

    def test_a_decision_with_an_epic_and_an_open_direct_task_is_not_closed(self):
        """REQ-3604, REQ-3630: a direct task open beside a finished epic keeps the decision open in status."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [x] T-001 TSK-0001 the task\n      closes: REQ-0001")
        self.second_direct(repository)
        status = repository.run("status").stdout
        self.assertIn("next: implement TSK-0002 (EPC-0001, 1 of 2 tasks done)", status)
        self.assertNotIn("closed: EPC-0001", status)

    def test_a_withdrawn_direct_task_is_dropped(self):
        """REQ-3630: a direct task withdrawn has nothing to mark it, so its status drops it."""
        repository = self.repo()
        self.direct(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: withdrawn")
        self.assertIn("closed: ADR-0001 (1 task done)", repository.run("status").stdout)
        self.assertIn("TSK-0001 dropped in ADR-0001", repository.run("show", "REQ-0001").stdout)

    def test_status_waits_on_a_draft_direct_task_as_ready_does(self):
        """REQ-3630: status and `ready implement` agree that a draft direct task waits for approval."""
        repository = self.repo()
        self.direct(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        self.assertIn("waiting: TSK-0001 is draft and not approved", repository.run("status").stdout)
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 1)

    def test_a_task_realises_only_a_decision(self):
        """REQ-3630: `realises` naming a defect is refused by the draft rule and by `ready`."""
        repository = self.repo()
        self.direct(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "realises: ADR-0001", "realises: BUG-0001")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001 realises BUG-0001, which is not a decision", done.stdout)
        repository.edit("tasks/TSK-0001-a-task.md", "status: approved", "status: draft")
        self.assertIn("realises BUG-0001, where a task realises only a decision", repository.run("check", "rules").stdout)

    def test_a_task_naming_no_authority_closes_nothing_from_its_evidence(self):
        """REQ-3630: only a task naming `realises` is done by its Evidence; one naming nothing stays open."""
        repository = self.repo()
        self.second_direct(repository, evidence="In #1.")
        repository.edit("tasks/TSK-0002-direct.md", "realises: ADR-0001\n", "")
        self.assertIn("TSK-0002 open in \n", repository.run("show", "REQ-0001").stdout)

    def test_a_direct_task_waits_on_its_dependency(self):
        """REQ-1358, REQ-3630: a direct task's blocking dependency is done once that task's Evidence is written."""
        repository = self.repo()
        self.direct(repository)
        self.second_direct(repository, extra="")
        repository.edit("tasks/TSK-0002-direct.md", "## Depends on\n\nText.", "## Depends on\n\n- TSK-0001 (blocking): it lands first")
        self.assertEqual(repository.run("ready", "implement", "TSK-0002").returncode, 1)
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nNot yet.", "## Evidence\n\nIn #1.")
        self.assertEqual(repository.run("ready", "implement", "TSK-0002").returncode, 0)

    def test_a_retired_step_is_refused_in_a_draft_defect_only(self):
        """REQ-3638: a draft defect may not enter at a retired step; one approved, superseded or withdrawn keeps it."""
        repository = self.repo()
        for step in ("cover", "document", "verify"):
            repository.edit("bugs/BUG-0001-a-defect.md", "found:", f"enters: {step}\nfound:")
            for status, code in (("approved", 0), ("superseded", 0), ("withdrawn", 0), ("draft", 1)):
                text = (repository.root / "bugs/BUG-0001-a-defect.md").read_text(encoding="utf-8")
                text = re.sub(r"\nstatus: \w+", f"\nstatus: {status}", text, count=1)
                repository.write("bugs/BUG-0001-a-defect.md", text)
                done = repository.run("check", "rules")
                self.assertEqual(done.returncode, code, f"{step} {status}: {done.stdout}")
                if code:
                    self.assertIn(f"enters {step}, which is not a step", done.stdout)
            repository.edit("bugs/BUG-0001-a-defect.md", f"enters: {step}\n", "")

    def test_a_direct_task_closes_with_its_evidence(self):
        """REQ-3630, REQ-3604: with no epic to mark it, a task is done once its Evidence is written."""
        repository = self.repo()
        self.direct(repository, evidence="In #1: the checks pass.")
        self.assertIn("closed: ADR-0001 (1 task done)", repository.run("status").stdout)
        self.assertIn("State\n  closed\n  TSK-0001 done in ADR-0001\n", repository.run("show", "REQ-0001").stdout)


class ShortChainPrompts(unittest.TestCase):
    """TSK-3820, ADR-2300: the prompts and templates ask for the seven-step chain."""

    SEVEN = ["research", "requirements", "design", "spec", "epic", "implement", "review"]

    def flat(self, path):
        return re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))

    def test_the_skill_names_seven_steps_in_order(self):
        """Criterion 1, REQ-3638: SKILL.md's description and body name the seven steps in order."""
        text = (METHOD / "SKILL.md").read_text(encoding="utf-8")
        front, body = text.split("\n---\n", 1)
        pattern = r",\s+".join(self.SEVEN[:-1]) + r",?\s+and\s+" + self.SEVEN[-1]
        description = next(line for line in front.splitlines() if line.startswith("description:"))
        self.assertRegex(description, pattern)
        self.assertRegex(re.sub(r"\s+", " ", body), pattern)

    def test_each_of_the_seven_steps_has_one_file(self):
        """Criterion 1, REQ-3638: `steps/` holds one file for each of the seven steps and no other."""
        self.assertEqual(sorted(p.stem for p in (METHOD / "steps").glob("*.md")), sorted(self.SEVEN))

    def test_nothing_the_unit_ships_dispatches_a_record_reviewer_or_a_skeptic(self):
        """Criterion 2, REQ-3624: no shipped file names the record reviewer or the skeptic, and the agent is gone."""
        self.assertFalse((UNIT / "agents" / "record-reviewer.md").exists())
        found = [str(path.relative_to(UNIT)) for path in sorted(UNIT.rglob("*"))
                 if path.is_file() and "tests" not in path.parts and "bin" not in path.parts
                 and re.search(r"record-reviewer|skeptic", path.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(found, [])

    def test_implement_writes_the_tests_first(self):
        """Criterion 3, REQ-3616, REQ-3640, REQ-3642, REQ-3644, REQ-3618: tests in a first commit that fails, not
        weakened outside a commit saying why, and the documentation and the record marks in the same pull request."""
        text = self.flat(METHOD / "steps" / "implement.md")
        self.assertRegex(text, r"test for each acceptance criterion a program can check")
        self.assertRegex(text, r"commit of their own.{0,80}before any (commit|code) that implements")
        self.assertRegex(text, r"see each (one|test) fail")
        self.assertRegex(text, r"(modify|weaken).{0,120}commit of its own.{0,60}why")
        self.assertRegex(text, r"documentation.{0,120}same pull request|same pull request.{0,120}documentation")
        self.assertRegex(text, r"mark the task.{0,80}same pull request")
        self.assertRegex(text, r"Where every verb passed,.{0,260}mark the task")
        self.assertRegex(text, r"Mark the task done only in a change whose verbs all passed, because")
        self.assertNotRegex(text, r"its output")
        self.assertRegex(text, r"Keep `Not yet\.` as the first line of the task's Evidence until every verb has passed, because")
        self.assertRegex(text, r"Where a verb didn't pass, leave `Not yet\.` as the first line")

    def test_review_is_a_code_review_in_the_pull_request(self):
        """Criterion 4, REQ-3626, REQ-3612: a review of the change in its pull request, fixed there, written into no
        record, reporting a test that would pass against a wrong implementation."""
        text = self.flat(METHOD / "steps" / "review.md")
        self.assertRegex(text, r"task's pull request")
        self.assertRegex(text, r"fix.{0,80}in (that|the same) pull request")
        self.assertRegex(text, r"Write no finding into the record")
        self.assertRegex(text, r"writes no finding into the record")
        self.assertRegex(text, r"agent with read-only tools")
        self.assertRegex(text, r"fresh agent review the fixes, for at most two rounds")
        self.assertRegex(text, r"End in one verdict")
        self.assertRegex(text, r"would (still )?pass against a wrong implementation")

    def test_the_templates_carry_no_cover_and_no_checked_at(self):
        """Criterion 5, REQ-3616, REQ-3602: the task template has no Cover section and the epic no checked-at."""
        templates = UNIT / "templates"
        self.assertNotIn("## Cover", (templates / "task.md").read_text(encoding="utf-8"))
        self.assertNotIn("checked-at", (templates / "epic.md").read_text(encoding="utf-8"))
        self.assertIn("realises:", (templates / "task.md").read_text(encoding="utf-8"))

    def test_the_living_documents_name_seven_steps(self):
        """Criterion 6, REQ-3638: the constitution and the root README give the chain with seven steps."""
        root = UNIT.parent.parent
        chain = r"research -> requirements -> design -> spec -> epic\s+-> implement -> review"
        for name in ("CLAUDE.md", "README.md", "project/vision.md"):
            text = (root / name).read_text(encoding="utf-8")
            self.assertRegex(text, chain, name)
        for name in ("CLAUDE.md", "README.md", "project/vision.md", "llms.txt", "plugins/meow-flow/README.md"):
            text = re.sub(r"\s+", " ", (root / name).read_text(encoding="utf-8"))
            self.assertNotRegex(text, r"(?i)\b(nine|ten) steps\b", name)
            self.assertRegex(text, r"(?i)\bseven steps\b", name)

    def test_a_criterion_is_decidable_from_its_own_work(self):
        """REQ-3628: the task and epic templates and the epic step ask for a criterion its own work decides."""
        templates = UNIT / "templates"
        self.assertIn("decidable from this task's own work", self.flat(templates / "task.md"))
        self.assertIn("decidable from this epic's own work", self.flat(templates / "epic.md"))
        self.assertRegex(self.flat(METHOD / "steps" / "epic.md"), r"own work decides, never a later epic's")

    def test_the_epic_step_writes_a_lone_task_with_no_epic(self):
        """REQ-3630: the epic step writes one task naming `realises:` where one task realises the decision."""
        text = self.flat(METHOD / "steps" / "epic.md")
        self.assertRegex(text, r"Where one task realises the decision, write that task alone, naming `realises: ADR-NNNN`")
        self.assertRegex(text, r"Write no epic for a decision one task realises, because")


class MigratedShape(unittest.TestCase):
    """TSK-3860, ADR-2300, REQ-3652: no record carries the old chain's sections or `checked-at`."""

    def repo(self):
        repository = Repository()
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def commit(self, repository):
        for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                                     "commit", "-q", "-m", "base"]):
            subprocess.run(["git", *args], cwd=repository.path, check=True, capture_output=True)

    def test_the_clean_record_carries_no_checked_at(self):
        """A specification and an epic need no `checked-at` to pass every check."""
        repository = self.repo()
        for name in ("specs/SPC-0001-a-part.md", "epics/EPC-0001-a-plan.md"):
            self.assertNotIn("checked-at", (repository.root / name).read_text(encoding="utf-8"), name)
        self.assertEqual(repository.run("check").returncode, 0)

    def test_checked_at_is_a_retired_field(self):
        """A record still carrying `checked-at` is reported, by file and line."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", 'realises: ADR-0001\nchecked-at: "#1"')
        done = repository.run("check", "front-matter")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/epics/EPC-0001-a-plan.md:7: carries checked-at, a retired field", done.stdout)

    def test_a_retired_section_is_reported(self):
        """A record still carrying `## Cover`, `## Verified` or `## Open review findings` is reported by `shape`."""
        for name, section in (("tasks/TSK-0001-a-task.md", "Cover"), ("epics/EPC-0001-a-plan.md", "Verified"),
                              ("adrs/ADR-0001-a-choice.md", "Open review findings")):
            with self.subTest(section=section):
                repository = self.repo()
                path = repository.root / name
                path.write_text(path.read_text(encoding="utf-8") + f"\n## {section}\n\nText.\n", encoding="utf-8")
                done = repository.run("check", "shape")
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertRegex(done.stdout, rf"project/{re.escape(name)}:\d+: carries the section {section}, which is retired")

    def test_a_retired_heading_inside_fenced_code_is_an_example(self):
        """A fenced example showing an old section is text, not a section, whichever fence holds it."""
        repository = self.repo()
        path = repository.root / "adrs/ADR-0001-a-choice.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n```text\n## Cover\n~~~\n## Verified\n```\n\n~~~\n## Cover\n~~~\n",
                        encoding="utf-8")
        self.assertEqual(repository.run("check", "shape").returncode, 0)

    def test_removing_a_retired_section_or_field_leaves_an_approved_record_frozen_and_clean(self):
        """The migration's own edits aren't a change: an approved record loses `## Cover`, `## Open review findings`
        or `checked-at` with no finding, and still can't change anything else."""
        repository = self.repo()
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence", "## Cover\n\n- Checks: none\n\n## Evidence")
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001\n", "# REQ-0001\n\n## Open review findings\n\nOne.\n")
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at: "#1"')
        self.commit(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "## Cover\n\n- Checks: none\n\n## Evidence", "## Evidence")
        repository.edit("requirements/REQ-0001-an-obligation.md", "\n## Open review findings\n\nOne.\n", "")
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at: "#1"', "")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("requirements/REQ-0001-an-obligation.md", "# REQ-0001", "# REQ-0001\n\nIt MUST do more.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_text_under_a_retired_heading_is_still_a_change(self):
        """A record gaining a retired section, or changing the text of one it carries, is a change like any other."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "## Cover\n\nOld.\n\n## Consequences")
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nOld.", "## Cover\n\nA new obligation.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nA new obligation.", "## Cover\n\nOld.")
        path = repository.root / "requirements/REQ-0001-an-obligation.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n## Verified\n\nIt MUST now do more.\n", encoding="utf-8")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/requirements/REQ-0001-an-obligation.md: approved at HEAD", done.stdout)

    def test_a_retired_heading_with_more_words_is_the_same_section(self):
        """`## Verified, and closed with a criterion unmet` is the Verified section; `## Covered` is not Cover."""
        repository = self.repo()
        path = repository.root / "epics/EPC-0001-a-plan.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n## Verified, and closed with a criterion unmet\n\nText.\n", encoding="utf-8")
        self.assertIn("carries the section Verified, which is retired", repository.run("check", "shape").stdout)
        path.write_text(text + "\n## Covered\n\nText.\n", encoding="utf-8")
        self.assertNotIn("which is retired", repository.run("check", "shape").stdout)

    def test_a_wrapped_retired_field_and_a_line_opening_with_a_span_are_read(self):
        """A retired field written over several lines is removed whole, and a prose line opening with an inline
        span of backticks isn't a fence, so the section after it is still a section."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at:\n  [\n    "#1",\n  ]')
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence", "```paw check``` prints nothing.\n\n## Cover\n\nNot yet.\n\n## Evidence")
        self.assertIn("carries the section Cover", repository.run("check", "shape").stdout)
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at:\n  [\n    "#1",\n  ]', "")
        repository.edit("tasks/TSK-0001-a-task.md", "## Cover\n\nNot yet.\n\n## Evidence", "## Evidence")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_blank_line_changed_elsewhere_is_a_change(self):
        """Only the blank lines round a removed section move: one removed inside fenced code is a change."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "```text\na\n\n\n\nb\n```\n\n## Consequences")
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "a\n\n\n\nb", "a\n\nb")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_a_record_that_never_carried_one_is_compared_as_it_is(self):
        """The allowances belong to a removal: with nothing retired removed, a changed `revised` or an added blank
        line in an approved record is a change."""
        repository = self.repo()
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "revised: 2026-01-01", "revised: 2026-02-02")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_one_retired_section_removed_while_another_stays(self):
        """A migration in two steps passes: removing `## Cover` while `## Verified` stays as it was, and removing a
        `checked-at` written as a block list."""
        repository = self.repo()
        repository.edit("adrs/ADR-0001-a-choice.md", "## Consequences", "## Cover\n\nOld.\n\n## Verified\n\nKept.\n\n## Consequences")
        repository.edit("adrs/ADR-0001-a-choice.md", "addresses: [REQ-0001]", 'addresses: [REQ-0001]\nchecked-at:\n- "#1"\n- "#2"')
        self.commit(repository)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Cover\n\nOld.\n\n", "")
        repository.edit("adrs/ADR-0001-a-choice.md", '\nchecked-at:\n- "#1"\n- "#2"', "")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 0, done.stdout)
        repository.edit("adrs/ADR-0001-a-choice.md", "## Verified\n\nKept.", "## Verified\n\nChanged.")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_a_first_level_heading_in_evidence_ends_nothing(self):
        """Only a `## ` heading bounds a section, so a `# ` line in a task's Evidence is part of it."""
        repository = self.repo()
        self.commit(repository)
        repository.edit("tasks/TSK-0001-a-task.md", "## Evidence\n\nText.", "## Evidence\n\n# ran\n\noutput")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 0)

    def test_a_fence_closes_on_its_own_mark_at_its_own_length(self):
        """A four-mark fence holds a three-mark one, a line with an info string closes nothing, a tilde fence takes
        any info string, and a fence indented four spaces is code, not a fence."""
        for body, reported in (("````markdown\n```text\n## Cover\n```\n## Verified\n````", False),
                               ("```text\n```rust\n## Cover\n```", False),
                               ("~~~ a~b\n## Cover\n~~~", False),
                               ("    ```\n\n## Cover\n\nText.", True)):
            with self.subTest(body=body):
                repository = self.repo()
                path = repository.root / "adrs/ADR-0001-a-choice.md"
                path.write_text(path.read_text(encoding="utf-8") + f"\n{body}\n", encoding="utf-8")
                self.assertEqual("which is retired" in repository.run("check", "shape").stdout, reported)

    def test_a_second_tasks_section_or_a_changed_relation_freezes_an_epic(self):
        """An epic's free text is its first Tasks section: a second one added to hold new text, and a changed
        `realises`, are reported, and a fenced heading inside Tasks doesn't end it."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n```text\n## Example\n```\n\n- [ ] T-001 TSK-0001 the task")
        self.commit(repository)
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 0)
        repository.edit("epics/EPC-0001-a-plan.md", "## Coverage", "## Tasks\n\nNew criterion: easier.\n\n## Coverage")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nNew criterion: easier.\n\n## Coverage", "## Coverage")
        repository.edit("epics/EPC-0001-a-plan.md", "realises: ADR-0001", "realises: BUG-0001")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 1)

    def test_an_approved_epic_may_change_its_tasks_and_nothing_else(self):
        """With no `checked-at` to freeze it, an approved epic changes only under `## Tasks`."""
        repository = self.repo()
        self.commit(repository)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [x] T-001 TSK-0001 the task")
        self.assertEqual(repository.run("check", "frozen", "--base", "HEAD").returncode, 0)
        repository.edit("epics/EPC-0001-a-plan.md", "## Acceptance criteria\n\nText.", "## Acceptance criteria\n\nEasier.")
        done = repository.run("check", "frozen", "--base", "HEAD")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("project/epics/EPC-0001-a-plan.md: approved at HEAD", done.stdout)


class OffTheTrunk(unittest.TestCase):
    """TSK-3880, ADR-2310: a task whose record isn't on the declared trunk waits on its merge."""

    TASK = "tasks/TSK-0001-a-task.md"

    def git(self, repository, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", *args],
                              cwd=repository.path, check=True, capture_output=True, text=True,
                              env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})

    def repo(self, profile='[git]\ntrunk = "main"\n', on_trunk=False):
        """A record whose one open task is committed on `work`, and on `main` too where `on_trunk`."""
        repository = Repository(profile=profile)
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit(self.TASK, "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.git(repository, "checkout", "-q", "-b", "main")
        task = (repository.root / self.TASK).read_text(encoding="utf-8")
        if not on_trunk:
            (repository.root / self.TASK).unlink()
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "base")
        self.git(repository, "checkout", "-q", "-b", "work")
        (repository.root / self.TASK).write_text(task, encoding="utf-8")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "--allow-empty", "-m", "the task")
        return repository

    def test_a_task_off_the_trunk_is_not_ready(self):
        """Criterion 1, REQ-3660: `ready implement` exits 1 naming the task and the trunk, and 0 once it is there."""
        done = self.repo().run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("TSK-0001 is not approved on main yet", done.stdout)
        done = self.repo(on_trunk=True).run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

    def test_status_names_the_task_as_waiting_on_its_merge(self):
        """Criterion 2, REQ-3662: `status` prints waiting and no next for a task off the trunk."""
        status = self.repo().run("status").stdout
        self.assertIn("waiting: TSK-0001 is not approved on main yet", status)
        self.assertNotIn("next: implement TSK-0001", status)
        status = self.repo(on_trunk=True).run("status").stdout
        self.assertIn("next: implement TSK-0001 (EPC-0001, 0 of 1 task done)", status)
        self.assertNotIn("waiting: TSK-0001", status)
        self.assertNotIn("can't be told", status)

    def test_no_declared_trunk_is_said_and_refuses_nothing(self):
        """Criterion 3, REQ-3664: with no `[git] trunk`, ready passes and status says the guard is absent, once."""
        repository = self.repo(profile='[record]\nroot = "project"\n')
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        status = repository.run("status").stdout
        self.assertEqual(status.count("can't be told from one waiting on a merge"), 1, status)
        self.assertIn("declares no trunk", status)
        self.assertIn("next: implement TSK-0001", status)

    def test_outside_git_is_said_and_refuses_nothing(self):
        """Criterion 3, REQ-3664: where the directory is no git work tree, the same holds, naming that cause."""
        repository = self.repo()
        shutil.rmtree(repository.path / ".git")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        status = repository.run("status").stdout
        self.assertEqual(status.count("can't be told from one waiting on a merge"), 1, status)
        self.assertIn("isn't a git work tree", status)

    def test_a_trunk_naming_no_branch_is_said(self):
        """Criterion 3, REQ-3664: a declared trunk that names no branch refuses nothing and says so."""
        repository = self.repo(profile='[git]\ntrunk = "trunk"\n')
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        status = repository.run("status").stdout
        self.assertIn("trunk names no branch", status)
        self.assertEqual(status.count("can't be told from one waiting on a merge"), 1, status)

    def test_the_remote_tracking_trunk_is_read(self):
        """Criterion 4, REQ-3660: where the trunk exists only as a remote-tracking branch, that branch is read, and
        a task approved on it is on the trunk whatever the local branch holds."""
        repository = self.repo()
        sha = self.git(repository, "rev-parse", "main").stdout.strip()
        self.git(repository, "update-ref", "refs/remotes/origin/main", sha)
        self.git(repository, "branch", "-q", "-D", "main")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001 is not approved on main yet", done.stdout)
        self.git(repository, "update-ref", "refs/remotes/origin/main", self.git(repository, "rev-parse", "work").stdout.strip())
        self.git(repository, "branch", "-q", "main", sha)
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)

    def test_a_finished_task_is_never_held(self):
        """REQ-3660: only an open task is asked about, so a done one off the trunk changes nothing in status."""
        repository = self.repo()
        repository.edit("epics/EPC-0001-a-plan.md", "- [ ] T-001", "- [x] T-001")
        repository.edit(self.TASK, "## Evidence\n\nNot yet.", "## Evidence\n\nIn #1.")
        self.assertIn("closed: EPC-0001", repository.run("status").stdout)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_task_approved_only_on_the_branch_waits(self):
        """REQ-3660: a task that is a draft on the trunk and approved on the branch still waits on its merge."""
        repository = self.repo(on_trunk=True)
        self.git(repository, "checkout", "-q", "main")
        repository.edit(self.TASK, "status: approved", "status: draft")
        self.git(repository, "commit", "-q", "-am", "draft on the trunk")
        self.git(repository, "checkout", "-q", "work")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001 is not approved on main yet", done.stdout)

    def test_a_task_renamed_on_the_branch_is_the_same_task(self):
        """REQ-3660: the task is found on the trunk by its identifier, so a renamed file is still approved there."""
        repository = self.repo(on_trunk=True)
        self.git(repository, "mv", f"project/{self.TASK}", "project/tasks/TSK-0001-renamed.md")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_task_committed_to_the_local_trunk_is_on_it(self):
        """ADR-2310: a repository that commits straight to its trunk gets no guard, even where the remote-tracking
        branch is behind."""
        repository = self.repo()
        base = self.git(repository, "rev-parse", "main").stdout.strip()
        self.git(repository, "update-ref", "refs/remotes/origin/main", base)
        self.git(repository, "checkout", "-q", "main")
        self.git(repository, "merge", "-q", "--ff-only", "work")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def second_task(self, repository):
        text = (repository.root / self.TASK).read_text(encoding="utf-8").replace("TSK-0001", "TSK-0002")
        repository.write("tasks/TSK-0002-another.md", text)
        repository.edit("epics/EPC-0001-a-plan.md", "      closes: REQ-0001", "      closes: REQ-0001\n\n- [ ] T-002 TSK-0002 another\n      closes: REQ-0001")

    def test_a_task_on_the_trunk_is_next_past_one_that_waits(self):
        """REQ-3662: one task waiting on its merge doesn't hold a later one that is approved on the trunk, and the
        decision waits only when every task it could start does."""
        repository = Repository(profile='[git]\ntrunk = "main"\n')
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit(self.TASK, "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.second_task(repository)
        first = (repository.root / self.TASK).read_text(encoding="utf-8")
        (repository.root / self.TASK).unlink()
        self.git(repository, "checkout", "-q", "-b", "main")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "base")
        self.git(repository, "checkout", "-q", "-b", "work")
        (repository.root / self.TASK).write_text(first, encoding="utf-8")
        status = repository.run("status").stdout
        self.assertIn("next: implement TSK-0002 (EPC-0001, 0 of 2 tasks done)", status)
        self.assertNotIn("waiting:", status)
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 1)
        self.assertEqual(repository.run("ready", "implement", "TSK-0002").returncode, 0)
        (repository.root / "tasks/TSK-0002-another.md").write_text(
            first.replace("TSK-0001", "TSK-0002").replace("status: approved", "status: draft"), encoding="utf-8")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "second is a draft here")
        self.git(repository, "checkout", "-q", "main")
        self.git(repository, "merge", "-q", "--ff-only", "work")
        self.git(repository, "checkout", "-q", "work")
        repository.edit("tasks/TSK-0002-another.md", "status: draft", "status: approved")
        status = repository.run("status").stdout
        self.assertIn("next: implement TSK-0001 (EPC-0001, 0 of 2 tasks done)", status)

    def test_a_decision_waits_only_when_every_startable_task_does(self):
        """REQ-3662: with both tasks off the trunk the decision waits, naming the first."""
        repository = self.repo()
        self.second_task(repository)
        status = repository.run("status").stdout
        self.assertIn("waiting: TSK-0001 is not approved on main yet", status)
        self.assertNotIn("next: implement", status)

    def test_a_longer_identifier_and_a_stray_copy_are_told_apart(self):
        """REQ-3660: `TSK-00010` on the trunk isn't `TSK-0001`, and a stray file of the identifier beside the
        approved record doesn't hide it."""
        repository = self.repo()
        self.git(repository, "checkout", "-q", "main")
        task = (repository.root / self.TASK)
        repository.write("tasks/TSK-00010-other.md", "---\nid: TSK-00010\nstatus: approved\n---\n")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "a longer identifier")
        self.git(repository, "checkout", "-q", "work")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 1)
        self.git(repository, "checkout", "-q", "main")
        self.git(repository, "merge", "-q", "work")
        repository.write("tasks/TSK-0001-a-old.md.orig", "junk\n")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "a stray copy")
        self.assertTrue(task.is_file())
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)

    def test_a_record_root_of_another_name_is_guarded(self):
        """REQ-3660: the guard follows `[record] root`, and reads a status written with quotes or a comment."""
        repository = Repository(profile='[git]\ntrunk = "main"\n[record]\nroot = "rec/ord"\n', root="rec/ord")
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit(self.TASK, "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        task = (repository.root / self.TASK).read_text(encoding="utf-8")
        (repository.root / self.TASK).unlink()
        self.git(repository, "checkout", "-q", "-b", "main")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "base")
        (repository.root / self.TASK).write_text(task, encoding="utf-8")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 1)
        (repository.root / self.TASK).write_text(task.replace("status: approved", 'status: "approved" # agreed'), encoding="utf-8")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "the task")
        (repository.root / self.TASK).write_text(task, encoding="utf-8")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)

    def test_a_record_outside_the_repository_is_said(self):
        """REQ-3664: a record root outside the repository is on no branch of it, so nothing is refused and status says so."""
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        root = Path(outside.name).resolve() / "record"
        repository = Repository(profile=f'[git]\ntrunk = "main"\n[record]\nroot = "{root}"\n', root=str(root))
        self.addCleanup(repository.tmp.cleanup)
        repository.edit("epics/EPC-0001-a-plan.md", "## Tasks\n\nText.", "## Tasks\n\n- [ ] T-001 TSK-0001 the task\n      closes: REQ-0001")
        repository.edit(self.TASK, "## Evidence\n\nText.", "## Evidence\n\nNot yet.")
        self.git(repository, "checkout", "-q", "-b", "main")
        self.git(repository, "add", "-A")
        self.git(repository, "commit", "-q", "-m", "base")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        status = repository.run("status").stdout
        self.assertIn("the record sits outside the repository", status)
        self.assertEqual(status.count("can't be told from one waiting on a merge"), 1, status)

    def test_the_line_comes_after_the_drafts(self):
        """REQ-0321, REQ-3664: status still leads with what waits for approval."""
        repository = self.repo(profile='[record]\nroot = "project"\n')
        repository.edit("research/RES-0002-a-finding.md", "status: approved", "status: draft")
        lines = repository.run("status").stdout.splitlines()
        self.assertEqual(lines[0], "Waiting for approval")
        self.assertIn("RES-0002 research, draft", lines[1])
        self.assertIn("can't be told from one waiting on a merge", lines[2])

    def test_a_task_a_defect_carries_and_one_realising_a_decision_wait_too(self):
        """REQ-3660: the guard asks about the task, whatever authorises it."""
        for field in ("bug: BUG-0001", "realises: ADR-0001"):
            with self.subTest(field=field):
                repository = self.repo()
                repository.edit(self.TASK, "epic: EPC-0001", field)
                repository.edit(self.TASK, "\nSee [the plan](../epics/EPC-0001-a-plan.md).\n", "\n")
                done = repository.run("ready", "implement", "TSK-0001")
                self.assertEqual(done.returncode, 1, done.stdout)
                self.assertIn("TSK-0001 is not approved on main yet", done.stdout)

    def test_a_trunk_record_with_crlf_endings_is_read(self):
        """TSK-4000 criterion 1, BUG-1370: a task approved on the trunk in a file with CRLF endings is on the trunk."""
        repository = self.repo(on_trunk=True)
        self.git(repository, "checkout", "-q", "main")
        path = repository.root / self.TASK
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.git(repository, "commit", "-q", "-am", "crlf endings")
        self.assertIn(b"status: approved\r\n", path.read_bytes())
        self.git(repository, "checkout", "-q", "work")
        self.assertNotIn(b"\r\n", path.read_bytes())
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_trunk_on_a_remote_of_another_name_is_read(self):
        """TSK-4000 criterion 2, BUG-1370: the only remote holds the trunk whatever its name, and a second branch
        of it whose name ends in the trunk's changes nothing."""
        repository = self.repo()
        base = self.git(repository, "rev-parse", "main").stdout.strip()
        work = self.git(repository, "rev-parse", "work").stdout.strip()
        self.git(repository, "remote", "add", "upstream", "https://example.invalid/upstream.git")
        self.git(repository, "update-ref", "refs/remotes/upstream/main", base)
        self.git(repository, "branch", "-q", "-D", "main")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("TSK-0001 is not approved on main yet", done.stdout)
        self.assertNotIn("names no branch", repository.run("status").stdout)
        self.git(repository, "update-ref", "refs/remotes/upstream/release/main", work)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, "a branch whose name ends in the trunk's was read\n" + done.stdout)
        self.assertIn("TSK-0001 is not approved on main yet", done.stdout)
        self.assertNotIn("names no branch", repository.run("status").stdout)
        self.git(repository, "update-ref", "refs/remotes/upstream/main", work)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_only_the_tracked_remote_origin_and_a_sole_remote_are_read(self):
        """TSK-4000 criterion 2, BUG-1370: a remote that is neither tracked, `origin` nor alone may be a fork, so
        it isn't read, a kept ref under no remote isn't either, and on the tracked remote only the branch of the
        trunk's name is the trunk."""
        repository = self.repo()
        base = self.git(repository, "rev-parse", "main").stdout.strip()
        work = self.git(repository, "rev-parse", "work").stdout.strip()
        self.git(repository, "update-ref", "refs/remotes/fork/main", work)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, "a kept ref under no remote was read\n" + done.stdout)
        self.git(repository, "config", "branch.main.remote", "fork")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, "a tracked remote the repository doesn't configure was read\n" + done.stdout)
        self.git(repository, "config", "--unset", "branch.main.remote")
        self.git(repository, "remote", "add", "origin", "https://example.invalid/origin.git")
        self.git(repository, "remote", "add", "fork", "https://example.invalid/fork.git")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, "a remote that is neither tracked, origin nor alone was read\n" + done.stdout)
        self.git(repository, "update-ref", "refs/remotes/fork/main", base)
        self.git(repository, "update-ref", "refs/remotes/fork/feature", work)
        self.git(repository, "config", "branch.main.remote", "fork")
        self.git(repository, "config", "branch.main.merge", "refs/heads/feature")
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 1, "the tracked remote's branch of another name was read\n" + done.stdout)
        self.git(repository, "update-ref", "refs/remotes/fork/main", work)
        done = repository.run("ready", "implement", "TSK-0001")
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_a_task_behind_a_link_leaving_the_repository_is_said(self):
        """TSK-4000 criterion 3, BUG-1370, REQ-3664: the trunk says nothing about a task reached through a link that
        leaves the repository, so nothing is refused and status names the task, once."""
        repository = self.repo(on_trunk=True)
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        moved = Path(outside.name).resolve() / "tasks"
        shutil.move(repository.root / "tasks", moved)
        os.symlink(moved, repository.root / "tasks")
        self.assertEqual(repository.run("ready", "implement", "TSK-0001").returncode, 0)
        status = repository.run("status").stdout
        self.assertEqual(status.count("can't be told from one waiting on a merge"), 1, status)
        line = next(line for line in status.splitlines() if "can't be told" in line)
        self.assertIn("TSK-0001", line)
        self.assertIn("a link that leaves the repository", line)
        self.assertIn("next: implement TSK-0001", status)

    def test_status_lists_each_trunk_ref_once(self):
        """TSK-4000 criterion 4, BUG-1370: with two open tasks and a trunk held by one commit, status starts
        `git ls-tree` once, whether one ref holds that commit or two."""
        repository = self.repo()
        self.second_task(repository)
        shim = tempfile.TemporaryDirectory()
        self.addCleanup(shim.cleanup)
        log = Path(shim.name) / "calls"
        git = Path(shim.name) / "git"
        git.write_text(f'#!/bin/sh\necho "$1" >> "{log}"\nexec "{shutil.which("git")}" "$@"\n', encoding="utf-8")
        git.chmod(0o755)
        env = {**os.environ, "PATH": f"{shim.name}{os.pathsep}{os.environ['PATH']}"}
        for refs in ("one ref", "two refs at one commit"):
            with self.subTest(refs=refs):
                if refs != "one ref":
                    self.git(repository, "update-ref", "refs/remotes/origin/main", self.git(repository, "rev-parse", "main").stdout.strip())
                log.write_text("", encoding="utf-8")
                status = subprocess.run([str(BIN), "status"], cwd=repository.path, capture_output=True, text=True, env=env)
                self.assertIn("waiting: TSK-0001 is not approved on main yet", status.stdout)
                calls = log.read_text(encoding="utf-8").split()
                self.assertEqual(calls.count("ls-tree"), 1, calls)

    def rules(self):
        text = (METHOD / "SKILL.md").read_text(encoding="utf-8")
        found = re.findall(r"^- (M\d+)\.\s(.*?)(?=^- M\d+\.\s|^</rules>)", text, re.MULTILINE | re.DOTALL)
        return [(name, re.sub(r"\s+", " ", body).strip()) for name, body in found]

    def test_the_skill_says_where_each_path_stops(self):
        """Criterion 5, REQ-3656, REQ-3658: M5 and M20 name each other, a rule under M20 holds the draft, check,
        approve order and the stop at the epic step, and the identifiers run in order with none repeated."""
        rules = self.rules()
        self.assertEqual([name for name, _ in rules], [f"M{n}" for n in range(1, len(rules) + 1)])
        by = dict(rules)
        self.assertRegex(by["M5"], r"^Unless M20 applies, stop after writing an artifact that needs approval")
        self.assertRegex(by["M20"], r"^Where a person asks for a decision to land in one pull request")
        self.assertRegex(by["M20"], r"stop once, at that pull request")
        self.assertRegex(by["M20"], r"Without that request, \bM5\b holds")
        under = [body for _, body in rules if body.startswith("Under M20")]
        self.assertEqual(len(under), 1, under)
        self.assertRegex(under[0], r"write each record as a draft, run `paw check`, and set it to `approved` only where the check reports nothing")
        self.assertRegex(under[0], r"go no further than the epic step")
        self.assertNotRegex(" ".join(body for _, body in rules), r"request (itself )?approves")
        self.assertRegex(by["M1"], r"^Unless M20 applies, do this step's work and no later step's")
        self.assertRegex(by["M6"], r"waits on a merge, and the person's merge is what approves it")
        text = (METHOD / "SKILL.md").read_text(encoding="utf-8")
        steps = re.sub(r"\s+", " ", tagged(text, "steps"))
        self.assertRegex(steps, r"7\. Where M20 applies and the check reported nothing, set each artifact the step wrote to `approved`")
        self.assertRegex(steps, r"where a step up to epic remains, go to step 1 for it")
        self.assertRegex(steps, r"8\. End by naming")
        self.assertRegex(steps, r"Where M20 applies and the check still reports a finding, name the draft and the finding")

    def test_the_skill_says_who_opens_the_pull_request(self):
        """TSK-4010 criterion 1, BUG-1380, REQ-3656: M20 has the session open the pull request and name it in its
        report, and name the branch where the repository declares no code host."""
        rule = dict(self.rules())["M20"]
        self.assertRegex(rule, r"stop once, at that pull request, which you open and name in your report")
        self.assertRegex(rule, r"Where the repository declares no code host, name the branch in its place")


class DeniedDispatch(unittest.TestCase):
    """TSK-2703 criteria 1 and 3, REQ-2978, SPC-1030 "What an agent reports" and SPC-1090 "The review": every
    shipped agent carries the denial rule in the same words, and the review step ends a `BLOCKED` dispatch there."""

    AGENT_FILES = {
        "router": AGENTS / "router.md",
        "prose": REPOSITORY / "plugins" / "meow-prose" / "agents" / "prose.md",
    }

    def denial_rule(self, name):
        text = self.AGENT_FILES[name].read_text(encoding="utf-8").split("---\n", 2)[2]
        found = [s for s in sentences(text) if re.search(r"\bcall is denied\b", s) and re.search(r"use no other tool to reach the same result", s)]
        self.assertEqual(len(found), 1, f"{name} has {len(found)} sentences stating the denial rule, not one")
        return found[0]

    def test_no_shipped_agent_is_left_out(self):
        """TSK-2703 criterion 1: the agents read here are every agent a unit ships, so a new one is held too."""
        shipped = sorted(str(path.relative_to(REPOSITORY)) for path in (REPOSITORY / "plugins").glob("*/agents/*.md"))
        self.assertEqual(shipped, sorted(str(path.relative_to(REPOSITORY)) for path in self.AGENT_FILES.values()))

    def test_each_agent_carries_the_denial_rule(self):
        """TSK-2703 criterion 1, REQ-2978: where a call is denied, the agent issues no second call in another
        form, reaches the result with no other tool, asks nobody for the permission, ends with BLOCKED naming the
        tool and what it was called on, and the rule states its reason."""
        for name in self.AGENT_FILES:
            with self.subTest(agent=name):
                rule = self.denial_rule(name)
                for pattern, what in (
                    (r"no second call in another form", "no second call in another form"),
                    (r"ask nobody for the permission", "asks nobody"),
                    (r"outcome: BLOCKED", "ends as BLOCKED"),
                    (r"naming the tool and what it was called on", "names the tool and what it was called on"),
                    (r"\bbecause\b", "states its reason"),
                ):
                    self.assertRegex(rule, pattern, what)

    def test_the_agents_carry_one_sentence(self):
        """TSK-2703 criterion 1, REQ-2978, SPC-1030: the denial rule is in the same words in every agent."""
        rules = {name: self.denial_rule(name) for name in self.AGENT_FILES}
        self.assertEqual(len(set(rules.values())), 1, rules)

    def test_the_review_step_ends_a_blocked_dispatch(self):
        """TSK-2703 criterion 3, REQ-2978, SPC-1090 "The review": W13 ends a BLOCKED review with no SendMessage to
        resume it, no second dispatch under the same permissions and no review by the session itself, and reports
        it as not run, never as self-assessed or passed."""
        text = (METHOD / "steps" / "review.md").read_text(encoding="utf-8")
        found = re.search(r"^- W13\.\s(.*?)(?=^- W\d+\.\s|^</rules>|\Z)", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(found, "the review step has no W13")
        blocked = flat("\n".join(s for s in sentences(found.group(1)) if word_in("BLOCKED", s)))
        for pattern, what in (
            (r"\bno sendmessage to resume\b", "names SendMessage as the resume it refuses"),
            (r"\bno second agent under the same permissions\b", "refuses a second dispatch under the same permissions"),
            (r"\bnever review the change yourself\b", "refuses a review by the session itself"),
            (r"\bnot run\b[^.;]*\bnever as self-assessed or passed\b", "reports it as not run"),
        ):
            with self.subTest(what=what):
                self.assertRegex(blocked, pattern)

    def test_the_steps_brief_the_agent_and_end_a_review_that_did_not_run(self):
        """TSK-2703 criterion 3, REQ-2978: step 2 tells the agent to end a denied call as BLOCKED, since nothing
        else gives it the rule, and step 8 and W8 have an ending for a review that didn't run."""
        text = (METHOD / "steps" / "review.md").read_text(encoding="utf-8")
        steps = flat(tagged(text, "steps"))
        self.assertRegex(steps, r"2\. .*where a tool call is denied it makes no other call for it, asks nobody, and ends with outcome: blocked")
        self.assertRegex(steps, r"8\. .*not run where the first agent reported blocked, the fixes unreviewed where the agent reviewing a round of them did")
        self.assertRegex(flat(text), r"w8\. end in one verdict: finished, not run, or the findings still open")


if __name__ == "__main__":
    unittest.main()
