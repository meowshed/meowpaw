# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1195 states `meow-markdown` detects, lists and binds.

Each fixture is a scratch git repository with its home isolated. The program
runs git alone and writes nothing, so a fixture needs no Markdown tool
installed. `MEOW_MARKDOWN_BIN` names the launcher to test. Where no launcher
exists yet, a run reports exit 127 and prints nothing, so every check fails on
what the program should have printed, and not on a missing file (RES-0075).
"""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
ROOT = UNIT.parent.parent
BIN = Path(os.environ.get("MEOW_MARKDOWN_BIN", UNIT / "bin" / "meow-markdown"))

PROFILE = '[markdown]\ntarget = "github"\n'
DOC = "# A document\n\nSome text.\n"
TWO = {".meowpaw/profile.toml": PROFILE, "README.md": DOC, "docs/guide.md": DOC}
NOT_MARKDOWN = "unresolved: not a Markdown repository"
FRONT_END_CLI = re.compile(r"markdownlint-cli(?!2)")
# SPC-1195 doesn't say whether the `# check: unresolved` line makes `bind` exit
# 3 under SPC-1190's table, so a detected repository may take either.
BIND_EXITS = (0, 3)


class Repository:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.root = base / "repo"
        self.home = base / "home"
        for directory in (self.root, self.home):
            directory.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("MISE_", "__MISE_"))}
        self.env.update(HOME=str(self.home), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        for name, text in files.items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=self.env)

    def run(self, *args):
        if not BIN.exists():
            return subprocess.CompletedProcess([str(BIN), *args], 127, "", f"no launcher at {BIN}\n")
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True, text=True, env=self.env,
                              stdin=subprocess.DEVNULL)

    def tree(self):
        return subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"], cwd=self.root,
                              capture_output=True, text=True, env=self.env).stdout


class Fixture(unittest.TestCase):
    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def bind(self, files):
        done = self.repo(files).run("bind")
        self.assertIn(done.returncode, BIND_EXITS, done.stdout + done.stderr)
        self.assertIn("[verbs]", done.stdout, done.stderr)
        return done.stdout.splitlines()

    @staticmethod
    def following(lines, line):
        at = lines.index(line)
        return lines[at + 1] if at + 1 < len(lines) else ""


class Detection(Fixture):
    """TSK-3100 criterion 1, REQ-2352: two tracked `*.md` or a markdownlint file make a Markdown corpus."""

    def test_criterion_1_two_tracked_markdown_files_are_detected(self):
        """TSK-3100 criterion 1, REQ-2352: two tracked `*.md` files are a Markdown repository."""
        done = self.repo(TWO).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn(NOT_MARKDOWN, done.stdout + done.stderr)

    def test_criterion_1_a_lone_readme_is_not_detected(self):
        """TSK-3100 criterion 1, REQ-2352: one tracked README is not a Markdown repository."""
        done = self.repo({".meowpaw/profile.toml": PROFILE, "README.md": DOC}).run("status")
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn(NOT_MARKDOWN, done.stdout + done.stderr)

    def test_criterion_1_a_lone_readme_beside_a_markdownlint_file_is_detected(self):
        """TSK-3100 criterion 1, REQ-2352: any tracked `.markdownlint*` file makes a Markdown repository."""
        done = self.repo({".meowpaw/profile.toml": PROFILE, "README.md": DOC,
                          ".markdownlint.yaml": "default: true\n"}).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn(NOT_MARKDOWN, done.stdout + done.stderr)


class Bind(Fixture):
    """TSK-3100 criterion 2, REQ-2352: `bind` prints each verb from the configuration committed."""

    def test_criterion_2_a_markdownlint_cli2_file_binds_lint_and_names_check(self):
        """TSK-3100 criterion 2, REQ-2352: lint runs markdownlint-cli2, with `meow-markdown check` in a comment."""
        lines = self.bind({**TWO, ".markdownlint-cli2.yaml": "config:\n  MD013: false\n"})
        line = "lint = \"markdownlint-cli2 '**/*.md'\""
        self.assertIn(line, lines)
        comment = self.following(lines, line)
        self.assertTrue(comment.startswith("#"), lines)
        self.assertIn("meow-markdown check", comment)

    def test_criterion_2_no_linter_configuration_binds_lint_to_check(self):
        """TSK-3100 criterion 2, REQ-2352: with no linter configured, lint is `meow-markdown check`."""
        self.assertIn('lint = "meow-markdown check"', self.bind(TWO))

    def test_criterion_2_a_prettierrc_binds_format(self):
        """TSK-3100 criterion 2, REQ-2352: a `.prettierrc` binds format to prettier."""
        self.assertIn("format = \"prettier --check '**/*.md'\"", self.bind({**TWO, ".prettierrc": "{}\n"}))

    def test_criterion_2_check_is_unresolved_with_its_reason(self):
        """TSK-3100 criterion 2, REQ-2352: Markdown has no types, so check is unresolved."""
        self.assertIn("# check: unresolved, Markdown has no types", self.bind(TWO))

    def test_criterion_2_a_lychee_toml_binds_test_to_links(self):
        """TSK-3100 criterion 2, REQ-2352: a `lychee.toml` binds test to `meow-markdown links`."""
        self.assertIn('test = "meow-markdown links"', self.bind({**TWO, "lychee.toml": "offline = true\n"}))

    def test_criterion_2_a_mkdocs_yml_leaves_build_unbound_naming_it(self):
        """TSK-3100 criterion 2, REQ-2352: a site build is named and left unbound."""
        self.assertIn("# build: unbound, mkdocs.yml configures a site build",
                      self.bind({**TWO, "mkdocs.yml": "site_name: Fixture\n"}))

    def test_criterion_2_a_declared_verb_is_left_out(self):
        """TSK-3100 criterion 2, REQ-2352: a verb the profile declares gets no line at all."""
        profile = PROFILE + '\n[verbs]\ntest = "make test"\n'
        lines = self.bind({**TWO, ".meowpaw/profile.toml": profile, "lychee.toml": "offline = true\n"})
        self.assertIn("# check: unresolved, Markdown has no types", lines)
        self.assertEqual([line for line in lines if re.match(r"#?\s*test\b", line)], [], lines)


class Runner(Fixture):
    def test_criterion_3_a_mise_toml_is_named_with_the_mise_pack(self):
        """TSK-3100 criterion 3, REQ-2352: a runner's configuration points at that runner's pack."""
        lines = self.bind({**TWO, "mise.toml": "[tasks.docs]\nrun = \"true\"\n"})
        named = [line for line in lines if "mise.toml" in line]
        self.assertTrue(named, lines)
        self.assertIn("meow-mise", "\n".join(lines))


class Status(Fixture):
    def test_criterion_4_a_markdownlint_cli2_file_is_read_by_cli2_alone(self):
        """TSK-3100 criterion 4, REQ-2352: this repository's `.markdownlint-cli2.yaml` is read by markdownlint-cli2 alone."""
        copy = (ROOT / ".markdownlint-cli2.yaml").read_text(encoding="utf-8")
        done = self.repo({**TWO, ".markdownlint-cli2.yaml": copy}).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        lines = [line for line in done.stdout.splitlines() if ".markdownlint-cli2.yaml" in line]
        self.assertEqual(len(lines), 1, done.stdout)
        said = lines[0].replace(".markdownlint-cli2.yaml", "")
        self.assertIn("markdownlint-cli2", said)
        self.assertIsNone(FRONT_END_CLI.search(said), lines[0])


class Tree(Fixture):
    """TSK-3100 criterion 5, REQ-2352: `status` and `bind` write nothing, tracked or ignored."""

    FIXTURES = {
        "two": (TWO, 0),
        "lone readme": ({".meowpaw/profile.toml": PROFILE, "README.md": DOC}, 3),
        "markdownlint": ({**TWO, ".markdownlint-cli2.yaml": "config: {}\n", ".markdownlint.yaml": "default: true\n"}, 0),
        "prettier": ({**TWO, ".prettierrc": "{}\n"}, 0),
        "lychee": ({**TWO, "lychee.toml": "cache = true\n", ".gitignore": ".lycheecache\n"}, 0),
        "mkdocs": ({**TWO, "mkdocs.yml": "site_name: Fixture\n"}, 0),
        "mise": ({**TWO, "mise.toml": "[tasks.docs]\nrun = \"true\"\n"}, 0),
    }

    def test_criterion_5_status_and_bind_leave_the_tree_as_it_was(self):
        """TSK-3100 criterion 5, REQ-2352: `git status --porcelain --ignored` reads the same before and after."""
        for name, (files, status) in self.FIXTURES.items():
            with self.subTest(fixture=name):
                repository = self.repo(files)
                before = repository.tree()
                binds = (status,) if status == 3 else BIND_EXITS
                for command, expected in (("status", (status,)), ("bind", binds)):
                    done = repository.run(command)
                    self.assertIn(done.returncode, expected, f"{command}: {done.stdout}{done.stderr}")
                    self.assertTrue((done.stdout + done.stderr).strip(), command)
                self.assertEqual(repository.tree(), before)


if __name__ == "__main__":
    unittest.main()
