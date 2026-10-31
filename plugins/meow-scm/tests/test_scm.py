# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for every check and failure path SPC-1050 states, and ADR-1080's checks.

Each fixture builds a repository in a temporary directory and runs the launcher
there. `MEOW_SCM_BIN` names the launcher to test, so the same fixtures can
first run against a program that returns nothing and be seen failing
(REQ-2072).
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_SCM_BIN", UNIT / "bin" / "meow-scm"))

CONVENTION = """[commits]
subject_limit = 72
trailers = ["Signed-off-by"]

[commits.types]
feat = "minor"
fix = "patch"
spec = "none"
"""
SIGNED = "Signed-off-by: A Person <a@example.org>"
AUTHOR = {**os.environ, "GIT_AUTHOR_NAME": "A Person", "GIT_AUTHOR_EMAIL": "a@example.org"}
GOOD = f"fix: read a link whose target sits in angle brackets\n\nThe check cut a target at its first parenthesis.\n\n{SIGNED}\n"
# Built from parts, so this file itself carries no attribution a search would find.
CO_AUTHOR = "Co-Authored-" + "By: Claude <noreply@" + "anthropic.com>"
FOOTER = "Generated " + "with [Claude Code](https://claude.com)"


class Repository:
    def __init__(self, profile=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        if profile is not None:
            (self.root / ".meowpaw").mkdir()
            (self.root / ".meowpaw" / "profile.toml").write_text(profile, encoding="utf-8")

    def check(self, message, env=None):
        env = {**AUTHOR, **(env or {})}
        return subprocess.run([str(BIN), "check-message"], cwd=self.root, input=message,
                              capture_output=True, text=True, env=env)

    def run(self, *args, env=None):
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True,
                              text=True, env=env)


class Convention(unittest.TestCase):
    def repo(self, profile=CONVENTION):
        repository = Repository(profile)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def test_a_sign_off_naming_someone_else_is_refused(self):
        done = self.repo().check(GOOD.replace("A Person <a@example.org>", "Another Person <b@example.org>"))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("sign-off route: the first sign-off names Another Person <b@example.org>, and the commit's author is A Person <a@example.org>", done.stdout)

    def test_a_message_in_the_convention_passes(self):
        done = self.repo().check(GOOD)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_each_break_is_named(self):
        message = ("chore: " + "x" * 70 + ".\nno blank line here\n")
        done = self.repo().check(message)
        self.assertEqual(done.returncode, 1)
        for rule in ("declared type", "subject length", "subject ending", "blank line", "trailer"):
            self.assertIn(rule, done.stdout)

    def test_a_subject_not_in_the_form_is_named(self):
        done = self.repo().check(f"Fixed the thing\n\n{SIGNED}\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("line 1: subject form", done.stdout)

    def test_a_scope_and_a_breaking_marker_are_accepted(self):
        done = self.repo().check(f"feat(verbs)!: drop the old table\n\nBREAKING CHANGE: the old table is gone.\n{SIGNED}\n")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_attribution_fails_with_a_convention(self):
        for line in (CO_AUTHOR, FOOTER):
            done = self.repo().check(f"fix: a change\n\n{SIGNED}\n{line}\n")
            self.assertEqual(done.returncode, 1)
            self.assertIn("attribution", done.stdout)

    def test_attribution_fails_without_a_convention(self):
        done = self.repo(profile=None).check(f"anything at all\n\n{CO_AUTHOR}\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("attribution", done.stdout)

    def test_a_path_or_a_product_name_is_not_attribution(self):
        message = f"fix: route the reply shape in plugins/meow-core/ for Claude Code\n\n{SIGNED}\n"
        done = self.repo().check(message)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_a_copyright_line_is_not_attribution(self):
        """REQ-3070: a copyright line, even one naming a vendor, credits no tool with the work."""
        message = ("fix: vendor the upstream example file\n\nIt keeps its header, SPDX-FileCopyrightText: 2026 "
                   f"Anthropic, PBC, from its source.\n\n{SIGNED}\n")
        done = self.repo().check(message)
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("meets the declared convention", done.stdout)

    def test_no_commits_table_leaves_the_convention_undeclared(self):
        done = self.repo(profile='[verbs]\ntest = "true"\n').check("Whatever I like\n")
        self.assertEqual(done.returncode, 3)
        self.assertIn("convention undeclared", done.stdout)
        self.assertNotIn("meets the declared convention", done.stdout)

    def test_no_profile_leaves_the_convention_undeclared(self):
        done = self.repo(profile=None).check(GOOD)
        self.assertEqual(done.returncode, 3)
        self.assertIn("undeclared", done.stdout)

    def test_an_unparseable_profile_checks_no_convention(self):
        done = self.repo(profile="[commits\n").check(GOOD)
        self.assertEqual(done.returncode, 3)
        self.assertIn("convention unparseable", done.stdout)

    def test_a_malformed_types_table_is_reported(self):
        profile = '[commits]\ntrailers = []\n[commits.types]\nfeat = "big"\n'
        done = self.repo(profile=profile).run("convention")
        self.assertIn("malformed", done.stdout)
        self.assertIn("feat", done.stdout)

    def test_an_empty_message_fails(self):
        done = self.repo().check("\n# a comment only\n")
        self.assertEqual(done.returncode, 1)
        self.assertIn("empty message", done.stdout)

    def test_convention_lists_who_may_be_named(self):
        """REQ-2208: `convention` prints the people `may_name` lists."""
        profile = CONVENTION.replace("[commits.types]", 'may_name = ["Ada Lovelace <ada@example.org>"]\n\n[commits.types]')
        done = self.repo(profile=profile).run("convention")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("Ada Lovelace <ada@example.org>", done.stdout)
        self.assertNotIn("Not read by meow-scm", done.stdout)

    def test_a_co_author_nobody_listed_is_refused(self):
        """REQ-2208: the check fails a trailer naming a person the profile doesn't list."""
        done = self.repo().check(GOOD.replace(SIGNED, f"Co-authored-by: Ada Lovelace <ada@example.org>\n{SIGNED}"))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn("line 5: named person:", done.stdout)

    def test_convention_reports_what_is_declared(self):
        done = self.repo().run("convention")
        self.assertEqual(done.returncode, 0)
        self.assertIn("release: minor", done.stdout)
        self.assertIn("72 characters", done.stdout)
        self.assertIn("Signed-off-by", done.stdout)

    def test_no_interpreter_leaves_the_message_unchecked(self):
        repo = self.repo()
        fake = repo.root / "bin"
        fake.mkdir()
        old = fake / "python3"
        old.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        old.chmod(0o755)
        done = repo.check(GOOD, env={"PATH": str(fake), "HOME": str(repo.root)})
        self.assertEqual(done.returncode, 3)
        self.assertIn("unchecked", done.stdout)
        self.assertNotIn("meets", done.stdout)



class CommitSkill(unittest.TestCase):
    """ADR-3090: the commit skill names the decision or the defect as the unit of a pull request."""

    TEXT = (UNIT / "skills/commit/SKILL.md").read_text(encoding="utf-8")

    def test_b1_names_the_decision_or_the_defect_as_the_unit(self):
        """REQ-3668: B1 gives one decision or defect one branch, one pull request and one review."""
        self.assertRegex(self.TEXT, r"B1\. Give one decision or defect one branch, one pull request and one review")
        self.assertNotRegex(self.TEXT, r"Give one task one branch")

    def test_b6_splits_the_record_before_the_work_starts(self):
        """REQ-3670: B6 asks for the record to be split and the pull request to stay one change."""
        self.assertRegex(self.TEXT, r"B6\. Split a decision or defect[^.]{0,200}before its work starts")


class ToolOperations(unittest.TestCase):
    """TSK-4370, ADR-2420: the commit skill bounds a tool that runs source control operations."""

    TEXT = " ".join((UNIT / "skills/commit/SKILL.md").read_text(encoding="utf-8").split())
    README = " ".join((UNIT / "README.md").read_text(encoding="utf-8").split())

    def test_it_lists_the_composite_commands_it_never_runs_with_a_reason(self):
        """Criterion 1, REQ-2610: a command that bundles decisions the method reserves is never called."""
        self.assertRegex(self.TEXT, r"T\d+\. Never run a command that bundles[^.]{0,200}`wt merge`")
        self.assertRegex(self.TEXT, r"`wt merge`[^.]{0,260}because")

    def test_a_message_a_tool_generated_is_never_used(self):
        """Criterion 2, REQ-2612: a generated message is never used, and the reason is given."""
        self.assertRegex(self.TEXT, r"T\d+\. Never use a message a tool generated[^.]{0,200}because")
        self.assertNotRegex(self.TEXT, r"a message here states why")

    def test_a_tool_with_no_machine_readable_output_runs_operations_only(self):
        """Criterion 3, REQ-2608: state is read from the documented output of the tool that owns it."""
        self.assertRegex(
            self.TEXT,
            r"documents no machine-readable output, use it to run operations only[^.]{0,120}"
            r"documented output of the tool that owns it",
        )

    def test_a_rebase_after_signing_is_signed_again_and_never_automatic(self):
        """Criterion 3, REQ-2614."""
        self.assertRegex(self.TEXT, r"Treat a rebase after signing as a change to what was signed[^.]{0,120}signed again")
        self.assertRegex(self.TEXT, r"never use a workflow that rebases[^.]{0,80}signatures are required")

    def test_a_model_written_summary_is_never_evidence_and_may_be_shown_in_a_list(self):
        """Criterion 3, REQ-2616: the ban and the one allowance."""
        self.assertRegex(self.TEXT, r"Never cite a model-written summary as evidence")
        self.assertRegex(self.TEXT, r"Show one only where a person is reading a list")

    def test_a_working_tree_is_removed_only_in_the_foreground(self):
        """Criterion 4, REQ-2618: no background removal, and the foreground one only when asked."""
        self.assertRegex(self.TEXT, r"Never remove a working tree in the background")
        self.assertRegex(self.TEXT, r"only in the foreground, when the person or the step that made it asks[^.]{0,80}because")

    def test_working_trees_share_only_ignored_build_output(self):
        """Criterion 4, REQ-2620: never source, and the unsupported filesystem is reported."""
        self.assertRegex(self.TEXT, r"Never let working trees share tracked source")
        self.assertRegex(self.TEXT, r"share only ignored build output")
        self.assertRegex(self.TEXT, r"report where the filesystem can't support the sharing")

    def test_the_readme_names_the_bounds(self):
        """TSK-4370 'What to do': the README says where it summarises the skill."""
        self.assertRegex(self.README, r"`wt merge`")
        self.assertRegex(self.README, r"only in the foreground")
        self.assertRegex(self.README, r"no message a tool generated|never uses a message a tool generated")

    def test_tsk_5070_worktrunk_runs_only_operations_whose_result_git_reports(self):
        """TSK-5070 criterion 3, REQ-2364: the skill and its page say worktrunk runs only operations whose result is read from git."""
        for name, text in (("SKILL.md", self.TEXT), ("README.md", self.README)):
            with self.subTest(file=name):
                self.assertRegex(text, r"worktrunk[^.]{0,200}only[^.]{0,120}result[^.]{0,80}from git")


class SparseTrees(unittest.TestCase):
    """TSK-5065, ADR-2650: the commit skill carries the rules for parallel agents in working trees, in both copies."""

    TEXTS = {where: " ".join((UNIT.parent.parent / where / "meow-scm/skills/commit/SKILL.md")
                             .read_text(encoding="utf-8").split())
             for where in ("plugins", "packages")}

    def test_sparse_paths_list_every_directory_any_agent_reads(self):
        """Criterion 1, REQ-3052: the sparse paths list every directory, `.meowpaw/` and `.claude/` included."""
        for where, text in self.TEXTS.items():
            with self.subTest(copy=where):
                self.assertRegex(text, r"T\d+\. [^.]{0,80}sparse[^.]{0,120}every directory any (agent|of them) reads")
                self.assertRegex(text, r"sparse[^.]{0,200}`\.meowpaw/` and `\.claude/`[^.]{0,200}because")

    def test_settings_that_must_apply_live_in_the_roots_settings_file(self):
        """Criterion 2, REQ-3054: settings that must apply in a working tree live in the root's settings file."""
        for where, text in self.TEXTS.items():
            with self.subTest(copy=where):
                self.assertRegex(text, r"T\d+\. [^.]{0,200}settings[^.]{0,120}root's `\.claude/settings\.json`[^.]{0,200}because")


class SkillLoading(unittest.TestCase):
    """TSK-5370, BUG-1550: the description routes the skill on every operation its rules bound."""

    RAW = (UNIT / "skills/commit/SKILL.md").read_text(encoding="utf-8")
    DESCRIPTION = " ".join(RAW.split("---")[1].split()).removeprefix("name: commit description: ")
    OBLIGATION = DESCRIPTION[DESCRIPTION.index("It MUST be loaded before") : DESCRIPTION.index("It MUST NOT be skipped")]

    def test_the_obligation_names_each_operation_the_rules_bound(self):
        """Criterion 1, REQ-1146: each verb a request uses sits in the sentence that says it MUST be loaded."""
        for words in (
            r"commit message, squash message or pull request title is written",
            r"`wt merge` is run",
            r"merged",
            r"rebased",
            r"worktree",
            r"working tree",
            r"created",
            r"removed",
            r"deleted",
        ):
            self.assertRegex(self.OBLIGATION, words)

    def test_the_description_closes_with_the_skip_sentence(self):
        """Criterion 1, REQ-1148: the closing sentence stays last."""
        self.assertRegex(self.DESCRIPTION, r"It MUST NOT be skipped, however[^.]*\.$")
        self.assertEqual(self.DESCRIPTION.count("It MUST be loaded before"), 1)

    def test_it_is_in_the_third_person_and_names_no_work_the_skill_does_not_govern(self):
        """Criterion 1, REQ-1144: no first or second person, and no tag, release or publish."""
        self.assertNotRegex(self.DESCRIPTION, r"\b(you|your|I|we)\b")
        self.assertNotRegex(self.OBLIGATION, r"\b(tag|release|publish)")


class Launcher(unittest.TestCase):
    """ADR-1270: a launcher with no binary for the machine names the machine and the fix."""

    def test_a_missing_binary_names_the_machine_and_the_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            launcher = Path(tmp) / "bin" / "meow-scm"
            launcher.parent.mkdir()
            launcher.write_text((UNIT / "bin" / "meow-scm").read_text(encoding="utf-8"), encoding="utf-8")
            launcher.chmod(0o755)
            done = subprocess.run(["sh", str(launcher), "check-message"], cwd=tmp, env={"PATH": os.environ["PATH"], "HOME": tmp, "CLAUDE_PLUGIN_DATA": f"{tmp}/data/unit"}, capture_output=True, text=True, input="")
            machine = subprocess.run(["uname", "-s"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
            self.assertIn("unchecked", done.stdout)
            self.assertIn(machine, done.stdout)
            self.assertIn("install meow-core", done.stdout)


if __name__ == "__main__":
    unittest.main()
