# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1195 states `meow-markdown` detects, lists and binds.

Each fixture is a scratch git repository with its home isolated. The program
runs git alone and writes nothing, so a fixture needs no Markdown tool
installed. `MEOW_MARKDOWN_BIN` names the launcher to test. Where no launcher
exists yet, a run reports exit 127 and prints nothing, so every check fails on
what the program should have printed, and not on a missing file (RES-0075).
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
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


class Markdownlintrc(Fixture):
    """TSK-3140, BUG-1320, REQ-2352: a root `.markdownlintrc` configures markdownlint-cli (RES-0295)."""

    FILES = {**TWO, ".markdownlintrc": '{ "MD013": false }\n'}

    def test_criterion_1_a_markdownlintrc_binds_markdownlint_cli(self):
        """TSK-3140 criterion 1, REQ-2352: lint runs markdownlint-cli, with `meow-markdown check` in a comment."""
        lines = self.bind(self.FILES)
        line = "lint = \"markdownlint '**/*.md'\""
        self.assertIn(line, lines)
        self.assertNotIn('lint = "meow-markdown check"', lines)
        comment = self.following(lines, line)
        self.assertTrue(comment.startswith("#"), lines)
        self.assertIn("meow-markdown check", comment)

    def test_criterion_2_status_lists_a_markdownlintrc(self):
        """TSK-3140 criterion 2, REQ-2352: `status` lists the file as read by markdownlint-cli alone."""
        done = self.repo(self.FILES).run("status")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("markdownlint configuration: none tracked", done.stdout)
        lines = [text for text in done.stdout.splitlines() if ".markdownlintrc" in text]
        self.assertEqual(len(lines), 1, done.stdout)
        self.assertIn("read by markdownlint-cli alone", lines[0])


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



NO_TARGET = "no render target: declare [markdown] target"
DEFAULTS = "markdownlint-cli2 runs its defaults: no configuration file"
CLI2 = "lint = \"markdownlint-cli2 '**/*.md'\"\n"
CLI = "lint = \"markdownlint '**/*.md'\"\n"
RULE = "config:\n  MD013: false\n"
JSONC = '{ "MD013": false }\n'


def verbs(lint, target='"github"'):
    """A profile declaring a render target, and a `lint` verb where `lint` is given."""
    text = "" if target is None else f"[markdown]\ntarget = {target}\n"
    return text + ("" if lint is None else f"\n[verbs]\n{lint}")


class Check(Fixture):
    def check(self, files):
        return self.repo(files).run("check")


class RenderTarget(Check):
    """TSK-3110 criterion 1, REQ-2452: `check` reports a missing render target, and takes any declared one."""

    def test_criterion_1_a_missing_target_is_a_finding(self):
        """TSK-3110 criterion 1, REQ-2452: no `[markdown] target` exits 1 naming the missing target."""
        done = self.check({**TWO, ".meowpaw/profile.toml": '[docs]\nstyle = "meow-prose"\n'})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(NO_TARGET, done.stdout)

    def test_criterion_1_an_empty_target_is_a_finding(self):
        """TSK-3110 criterion 1, REQ-2452: an empty `[markdown] target` counts as missing."""
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(None, '""')})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(NO_TARGET, done.stdout)

    def test_criterion_1_a_declared_target_passes(self):
        """TSK-3110 criterion 1, REQ-2452: `github`, and `forgejo` the skill doesn't know, both exit 0."""
        for target in ("github", "forgejo"):
            with self.subTest(target=target):
                done = self.check({**TWO, ".meowpaw/profile.toml": verbs(None, f'"{target}"')})
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                self.assertNotIn(NO_TARGET, done.stdout + done.stderr)


class MarkdownlintSettings(Check):
    """TSK-3110 criteria 2 to 4, REQ-2434: markdownlint settings the `lint` verb ignores, lacks or overrides."""

    def test_criterion_2_markdownlint_cli2_with_no_configuration_runs_its_defaults(self):
        """TSK-3110 criterion 2, REQ-2434: a `lint` verb running markdownlint-cli2 with no configuration file."""
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(CLI2)})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(DEFAULTS, done.stdout)

    def test_criterion_2_markdownlint_cli2_with_a_configuration_passes(self):
        """TSK-3110 criterion 2, REQ-2434: a tracked `.markdownlint-cli2.yaml` settles the defaults finding."""
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(CLI2), ".markdownlint-cli2.yaml": RULE})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn(DEFAULTS, done.stdout)

    def test_criterion_3_markdownlint_ignores_a_cli2_file(self):
        """TSK-3110 criterion 3, REQ-2434: markdownlint beside a tracked `.markdownlint-cli2.jsonc` exits 1 naming it."""
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(CLI), ".markdownlint-cli2.jsonc": '{ "config": {} }\n'})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("markdownlint ignores .markdownlint-cli2.jsonc", done.stdout)

    def test_criterion_3_markdownlint_cli2_reads_its_own_file(self):
        """TSK-3110 criterion 3, REQ-2434: markdownlint-cli2 beside the same file draws no finding."""
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(CLI2), ".markdownlint-cli2.jsonc": '{ "config": {} }\n'})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("ignores", done.stdout)

    def test_criterion_4_two_configurations_in_one_directory(self):
        """TSK-3110 criterion 4, REQ-2434: both files named, and markdownlint-cli2 applies the `.markdownlint.jsonc`."""
        applies = re.compile(r"markdownlint-cli2 applies \S*\.markdownlint\.jsonc\b")
        for lint in (None, CLI2, CLI, 'lint = "true"\n'):
            for directory in ("", "docs/"):
                with self.subTest(lint=lint, directory=directory or "."):
                    done = self.check({**TWO, ".meowpaw/profile.toml": verbs(lint),
                                       f"{directory}.markdownlint.jsonc": JSONC,
                                       f"{directory}.markdownlint-cli2.yaml": RULE})
                    self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                    lines = [line for line in done.stdout.splitlines() if "both configure rules" in line]
                    self.assertEqual(len(lines), 1, done.stdout)
                    self.assertIn(".markdownlint.jsonc", lines[0])
                    self.assertIn(".markdownlint-cli2.yaml", lines[0])
                    self.assertRegex(lines[0], applies)
                    if directory:
                        self.assertTrue(lines[0].startswith("docs"), lines[0])

    def test_criterion_4_a_cli2_file_setting_no_rule_is_no_finding(self):
        """TSK-3110 criterion 4, REQ-2434: a `.markdownlint-cli2.yaml` with no `config` overrides nothing."""
        done = self.check({**TWO, ".markdownlint.jsonc": JSONC, ".markdownlint-cli2.yaml": "ignores:\n  - vendor\n"})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("both configure rules", done.stdout)


class LintCommand(Check):
    """TSK-3150, BUG-1321, REQ-2434: `check` reads the lint command's program and `--config` as the tools do (RES-0295)."""

    def test_criterion_1_a_config_flag_names_the_configuration(self):
        """TSK-3150 criterion 1, REQ-2434: `--config <path>` is a configuration, and `--config=<path>` is a glob to cli2."""
        for name, flag, status in (("separate word", "--config .config/mdl.jsonc", 0),
                                   ("joined by =", "--config=.config/mdl.jsonc", 1)):
            with self.subTest(case=name):
                lint = f"lint = \"markdownlint-cli2 {flag} '**/*.md'\"\n"
                done = self.check({**TWO, ".meowpaw/profile.toml": verbs(lint), ".config/mdl.jsonc": JSONC})
                self.assertEqual(done.returncode, status, done.stdout + done.stderr)
                self.assertEqual(DEFAULTS in done.stdout.splitlines(), bool(status), done.stdout)

    def test_criterion_2_a_versioned_cli2_is_read(self):
        """TSK-3150 criterion 2, REQ-2434: `npx markdownlint-cli2@0.23.2` with no configuration runs its defaults."""
        lint = "lint = \"npx --yes markdownlint-cli2@0.23.2 '**/*.md'\"\n"
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(lint)})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn(DEFAULTS, done.stdout.splitlines())

    def test_criterion_3_a_versioned_markdownlint_cli_is_read(self):
        """TSK-3150 criterion 3, REQ-2434: `npx markdownlint-cli@0.49.1` ignores a tracked `.markdownlint-cli2.jsonc`."""
        lint = "lint = \"npx markdownlint-cli@0.49.1 '**/*.md'\"\n"
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(lint), ".markdownlint-cli2.jsonc": '{ "config": {} }\n'})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("markdownlint ignores .markdownlint-cli2.jsonc", done.stdout.splitlines())


CLI_DEFAULTS = "markdownlint runs its defaults: no configuration file"


class MarkdownlintCliDefaults(Check):
    """TSK-3160, BUG-1322, REQ-2434: markdownlint-cli with nothing configuring it runs its defaults (RES-0295, RES-0296)."""

    def cli_defaults(self, flags, extra):
        lint = f"lint = \"markdownlint {flags}'**/*.md'\"\n"
        done = self.check({**TWO, ".meowpaw/profile.toml": verbs(lint), **extra})
        return done, CLI_DEFAULTS in done.stdout.splitlines()

    def test_criterion_1_markdownlint_cli_with_no_configuration_runs_its_defaults(self):
        """TSK-3160 criterion 1, REQ-2434: no configuration exits 1 with the finding; each place cli reads settles it."""
        mdl = {".config/mdl.json": JSONC}
        for name, flags, extra, status in (
                ("none", "", {}, 1),
                (".markdownlintrc", "", {".markdownlintrc": JSONC}, 0),
                (".markdownlint.jsonc", "", {".markdownlint.jsonc": JSONC}, 0),
                ("-c", "-c .config/mdl.json ", mdl, 0),
                ("--config", "--config .config/mdl.json ", mdl, 0),
                ("--config=", "--config=.config/mdl.json ", mdl, 0)):
            with self.subTest(case=name):
                done, said = self.cli_defaults(flags, extra)
                self.assertEqual(done.returncode, status, done.stdout + done.stderr)
                self.assertEqual(said, bool(status), done.stdout)

    def test_criterion_2_what_markdownlint_cli_does_not_read_is_no_configuration(self):
        """TSK-3160 criterion 2, REQ-2434: a nested `.markdownlint.json` and `-c=<path>` leave the defaults running."""
        mdl = {".config/mdl.json": JSONC}
        for name, flags, extra in (("nested", "", {"docs/.markdownlint.json": JSONC}),
                                   ("-c=", "-c=.config/mdl.json ", mdl)):
            with self.subTest(case=name):
                done, said = self.cli_defaults(flags, extra)
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertTrue(said, done.stdout)


class CheckUnresolved(Check):
    """TSK-3110 criterion 5, REQ-2434 and REQ-2452: no profile, or one that doesn't parse, is unresolved."""

    def test_criterion_5_a_missing_profile_is_unresolved(self):
        """TSK-3110 criterion 5: a missing profile prints unresolved and exits 3."""
        done = self.check({"README.md": DOC, "docs/guide.md": DOC})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: ", done.stdout + done.stderr)

    def test_criterion_5_a_profile_that_does_not_parse_is_unresolved(self):
        """TSK-3110 criterion 5: a profile that doesn't parse prints unresolved and exits 3."""
        done = self.check({**TWO, ".meowpaw/profile.toml": "[markdown\ntarget = \n"})
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("unresolved: ", done.stdout + done.stderr)


class CheckTree(Fixture):
    """TSK-3110 criterion 6, REQ-2434 and REQ-2452: `check` writes nothing, tracked or ignored."""

    FIXTURES = {
        "no target": ({**TWO, ".meowpaw/profile.toml": '[docs]\nstyle = "meow-prose"\n'}, 1),
        "github": (TWO, 0),
        "forgejo": ({**TWO, ".meowpaw/profile.toml": verbs(None, '"forgejo"')}, 0),
        "defaults": ({**TWO, ".meowpaw/profile.toml": verbs(CLI2)}, 1),
        "ignored": ({**TWO, ".meowpaw/profile.toml": verbs(CLI), ".markdownlint-cli2.jsonc": "{}\n"}, 1),
        "overridden": ({**TWO, ".markdownlint.jsonc": JSONC, ".markdownlint-cli2.yaml": RULE}, 1),
        "no profile": ({"README.md": DOC, "docs/guide.md": DOC}, 3),
        "unparseable": ({**TWO, ".meowpaw/profile.toml": "[markdown\n"}, 3),
    }

    def test_criterion_6_check_leaves_the_tree_as_it_was(self):
        """TSK-3110 criterion 6: `git status --porcelain --ignored` reads the same before and after `check`."""
        for name, (files, status) in self.FIXTURES.items():
            with self.subTest(fixture=name):
                repository = self.repo(files)
                before = repository.tree()
                done = repository.run("check")
                self.assertEqual(done.returncode, status, done.stdout + done.stderr)
                self.assertEqual(repository.tree(), before)


class Adopted(unittest.TestCase):
    """TSK-3110 criterion 7, REQ-2434 and REQ-2452: this repository declares its target and lints with `check`."""

    def test_criterion_7_the_profile_declares_github_and_lint_runs_check(self):
        """TSK-3110 criterion 7, REQ-2452 and REQ-2434: `[markdown] target` and the `lint` verb, by the program's path."""
        profile = tomllib.loads((ROOT / ".meowpaw" / "profile.toml").read_text(encoding="utf-8"))
        self.assertEqual(profile.get("markdown", {}).get("target"), "github")
        self.assertIn("plugins/meow-markdown/bin/meow-markdown check", profile["verbs"]["lint"])

    def test_criterion_7_check_passes_on_this_repository(self):
        """TSK-3110 criterion 7, REQ-2434 and REQ-2452: `check` finds nothing in this repository."""
        env = {k: v for k, v in os.environ.items() if not k.startswith(("MISE_", "__MISE_"))}
        done = subprocess.run([str(BIN), "check"], cwd=ROOT, capture_output=True, text=True, env=env,
                              stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)



# The shape lychee 0.24.2 prints under `--format json`, as RES-0294 records it:
# counts, then one map per outcome keyed by the input file, each entry holding
# `url`, `status`, `span` and `duration`. The texts are RES-0294's.
MAPS = ("success_map", "error_map", "timeout_map", "suggestion_map", "redirect_map", "excluded_map")
TIMEOUT = ("http://10.255.255.1/", {"text": "Timeout", "details": "Request timed out"})
FAILED = ("https://unregistered.meowpaw-fixture.example.net/", {
    "text": "Network error: Connection failed. Check network connectivity and firewall settings",
    "details": "Connection failed. Check network connectivity and firewall settings"})
FORBIDDEN = ("https://httpbin.org/status/403", {"text": "Rejected status code: 403 Forbidden", "code": 403})
UNAVAILABLE = ("https://httpbin.org/status/503", {"text": "Rejected status code: 503 Service Unavailable", "code": 503})
GONE = ("https://httpbin.org/status/404", {"text": "Rejected status code: 404 Not Found", "code": 404})
MOVED = ("https://httpbin.org/status/301", {"text": "Rejected status code: 301 Moved Permanently", "code": 301})
EXCLUDED = {"text": "Excluded", "details": "This is due to your 'exclude' values"}
NOT_FOUND = {"text": "File not found. Check if file exists and path is correct",
             "details": "File not found. Check if file exists and path is correct"}
LINKS_PROFILE = PROFILE + '\n[verbs]\ntest = "meow-markdown links"\n'


def entry(url, status, line):
    return {"url": url, "status": status, "span": {"line": line, "column": 1},
            "duration": {"secs": 0, "nanos": 208417}}


def report(errors=(), timeouts=(), excluded=(), source="README.md"):
    """lychee's JSON for one input file: each argument a list of (url, status, line)."""
    maps = {name: {} for name in MAPS}
    for name, entries in (("error_map", errors), ("timeout_map", timeouts), ("excluded_map", excluded)):
        if entries:
            maps[name] = {source: [entry(*item) for item in entries]}
    total = len(errors) + len(timeouts) + len(excluded)
    counts = {"total": total, "unique": total, "successful": 0, "unknown": 0, "unsupported": 0,
              "timeouts": len(timeouts), "redirects": 0, "remaps": 0, "excludes": len(excluded),
              "errors": len(errors), "cached": 0}
    return {**counts, **maps, "duration": {"secs": 0, "nanos": 1}, "detailed_stats": False}


def without_lychee(path):
    """`PATH` with every directory holding a `lychee` left out, so only a stand-in answers."""
    return os.pathsep.join(d for d in path.split(os.pathsep) if d and not (Path(d) / "lychee").exists())


class Links(Fixture):
    """`links` runs a stand-in lychee printing RES-0294's JSON, and classifies each result from it."""

    def links(self, output, status, stderr="", files=None):
        """Run `links` with a stand-in lychee that prints `output` and exits `status`; None puts no lychee on PATH.

        `output` may be a function of the fixture's root, for an address inside it."""
        repository = self.repo({**TWO, ".meowpaw/profile.toml": LINKS_PROFILE} if files is None else files)
        path = without_lychee(repository.env.get("PATH", ""))
        if callable(output):
            output = output(repository.root)
        if output is not None:
            stand_in = repository.root.parent / "bin"
            stand_in.mkdir()
            text = stand_in / "lychee.out"
            text.write_text(output if isinstance(output, str) else json.dumps(output, indent=2), encoding="utf-8")
            script = stand_in / "lychee"
            script.write_text(f"#!/bin/sh\ncat '{text}'\nprintf '%s' '{stderr}' >&2\nexit {status}\n",
                              encoding="utf-8")
            script.chmod(0o755)
            path = f"{stand_in}{os.pathsep}{path}"
        repository.env["PATH"] = path
        return repository, repository.run("links")

    def said(self, done, url, label, line=None):
        """The one line naming `url`, which carries `label`, the file and its line."""
        lines = [text for text in done.stdout.splitlines() if url in text]
        self.assertEqual(len(lines), 1, done.stdout + done.stderr)
        self.assertIn(label, lines[0])
        self.assertIn("README.md", lines[0])
        if line is not None:
            self.assertRegex(lines[0], rf"\b{line}\b")
        return lines[0]

    def test_criterion_1_a_timeout_and_a_failed_connection_are_unreachable(self):
        """TSK-3120 criterion 1, REQ-2438: a timeout and a failed connection print as `unreachable`, exiting 3."""
        _, done = self.links(report(errors=[(*FAILED, 5)], timeouts=[(*TIMEOUT, 3)]), 2)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        for url, line in ((TIMEOUT[0], 3), (FAILED[0], 5)):
            self.assertNotIn("finding", self.said(done, url, "unreachable", line))

    def test_criterion_1_a_403_and_a_503_are_unreachable(self):
        """TSK-3120 criterion 1, REQ-2438: a 403 and a 503 response print as `unreachable`, exiting 3."""
        _, done = self.links(report(errors=[(*FORBIDDEN, 3), (*UNAVAILABLE, 4)]), 2)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        for url, line in ((FORBIDDEN[0], 3), (UNAVAILABLE[0], 4)):
            self.assertNotIn("finding", self.said(done, url, "unreachable", line))

    def test_criterion_2_a_404_and_a_missing_file_are_findings(self):
        """TSK-3120 criterion 2, REQ-2438: a 404 and a missing relative file print as `finding`, exiting 1."""
        for name, make in (("404", lambda root: (*GONE, 3)),
                           ("missing file", lambda root: ((root / "missing.md").as_uri(), NOT_FOUND, 3))):
            with self.subTest(case=name):
                items = []
                repository, done = self.links(lambda root: report(errors=[items.append(make(root)) or items[0]]), 2)
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertNotIn("unreachable", self.said(done, items[0][0], "finding", 3))

    def test_criterion_2_a_mix_exits_1_with_the_unreachable_listed_apart(self):
        """TSK-3120 criterion 2, REQ-2438: a 404 beside a timeout exits 1, the timeout under its own heading."""
        _, done = self.links(report(errors=[(*GONE, 3)], timeouts=[(*TIMEOUT, 4)]), 2)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.said(done, GONE[0], "finding", 3)
        self.said(done, TIMEOUT[0], "unreachable", 4)
        lines = done.stdout.splitlines()
        at = {url: next(i for i, text in enumerate(lines) if url in text) for url in (GONE[0], TIMEOUT[0])}
        headings = [i for i, text in enumerate(lines)
                    if "unreachable" in text.lower() and "://" not in text and i < at[TIMEOUT[0]]]
        self.assertTrue(headings, done.stdout)
        self.assertFalse(headings[-1] < at[GONE[0]] < at[TIMEOUT[0]], done.stdout)

    def test_criterion_3_only_excluded_addresses_are_skipped(self):
        """TSK-3120 criterion 3, REQ-2438: excluded addresses print as `skipped` with their count, exiting 0."""
        excluded = [("https://example.com/", EXCLUDED, 3), ("https://example.invalid/", EXCLUDED, 4)]
        _, done = self.links(report(excluded=excluded), 0)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        for url, _, line in excluded:
            self.said(done, url, "skipped", line)
        count = [text for text in done.stdout.splitlines() if "skipped" in text and "://" not in text]
        self.assertTrue(any(re.search(r"\b2\b", text) for text in count), done.stdout)

    def test_criterion_4_no_lychee_on_path_is_tool_absent(self):
        """TSK-3120 criterion 4, REQ-2438: no lychee on `PATH` prints `tool absent`, exiting 3."""
        _, done = self.links(None, 0)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("tool absent: lychee", done.stdout + done.stderr)

    def test_criterion_4_a_lychee_that_fails_or_prints_no_json_is_tool_broken(self):
        """TSK-3120 criterion 4, REQ-2438: exit 3, text that isn't JSON and a renamed `timeout_map` are `tool broken`."""
        renamed = json.dumps(report(timeouts=[(*TIMEOUT, 3)])).replace('"timeout_map"', '"timeouts_map"')
        for name, output, status, stderr in (
                ("exit 3", "", 3, "Error while loading config"),
                ("not JSON", "Issues found in 1 input. Find details below.\n", 0, ""),
                ("renamed map", renamed, 2, "")):
            with self.subTest(case=name):
                _, done = self.links(output, status, stderr)
                self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
                self.assertIn("tool broken", done.stdout + done.stderr)
                self.assertNotIn("unreachable", done.stdout)
                self.assertNotIn("finding", done.stdout)

    def test_criterion_4_a_rejected_3xx_is_unresolved(self):
        """TSK-3120 criterion 4, REQ-2438: a rejected 301 falls in no class, so it prints `unresolved`, exiting 3."""
        _, done = self.links(report(errors=[(*MOVED, 3)]), 2)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        line = self.said(done, MOVED[0], "unresolved", 3)
        self.assertNotIn("finding", line)

    def test_criterion_5_the_real_lychee_reports_a_missing_file(self):
        """TSK-3120 criterion 5, REQ-2438: lychee itself, on a missing relative file, makes `links` exit 1."""
        found = shutil.which("lychee")
        runs = found and subprocess.run([found, "--version"], capture_output=True, text=True).returncode == 0
        if not runs:
            self.skipTest("lychee isn't installed, so the real run can't be made here")
        files = {**TWO, ".meowpaw/profile.toml": LINKS_PROFILE, "README.md": "# A\n\nSee [gone](missing.md).\n"}
        repository = self.repo(files)
        done = repository.run("links")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        lines = [text for text in done.stdout.splitlines() if "missing.md" in text]
        self.assertEqual(len(lines), 1, done.stdout)
        self.assertIn("finding", lines[0])


class LinkSettings(Check):
    """TSK-3120 criteria 6 and 7, REQ-2454: a link check declares its offline behaviour, retries and cache."""

    def test_criterion_6_a_link_check_declares_offline_retries_and_cache(self):
        """TSK-3120 criterion 6, REQ-2454: no `max_retries` exits 1 naming it; all three, in the file or the flags, exit 0."""
        cases = (
            ("no max_retries", LINKS_PROFILE, {"lychee.toml": "offline = true\ncache = false\n"}, 1),
            ("all three", LINKS_PROFILE, {"lychee.toml": "offline = true\nmax_retries = 0\ncache = false\n"}, 0),
            ("flags", PROFILE + '\n[verbs]\ntest = "lychee --offline --max-retries 0 --cache=false \'**/*.md\'"\n',
             {}, 0),
        )
        for name, profile, extra, status in cases:
            with self.subTest(case=name):
                done = self.check({**TWO, ".meowpaw/profile.toml": profile, **extra})
                self.assertEqual(done.returncode, status, done.stdout + done.stderr)
                said = [text for text in done.stdout.splitlines() if "link check declares no" in text]
                if status:
                    self.assertEqual(said, ["link check declares no max_retries"], done.stdout)
                else:
                    self.assertEqual(said, [], done.stdout)
                    self.assertIn("no findings", done.stdout)

    def test_criterion_6_an_undeclared_link_check_names_each_setting(self):
        """TSK-3120 criterion 6, REQ-2454: a verb running `lychee` with no file and no flags names all three."""
        profile = PROFILE + '\n[verbs]\ntest = "npx lychee \'**/*.md\'"\n'
        done = self.check({**TWO, ".meowpaw/profile.toml": profile})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        for setting in ("offline", "max_retries", "cache"):
            self.assertIn(f"link check declares no {setting}", done.stdout.splitlines())

    def test_criterion_7_a_settings_file_that_does_not_parse_is_named(self):
        """TSK-3120 criterion 7, REQ-2454: a `lychee.toml` that isn't TOML exits 1 naming the file."""
        done = self.check({**TWO, ".meowpaw/profile.toml": LINKS_PROFILE, "lychee.toml": "offline = \n[cache\n"})
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertTrue(any(text.startswith("lychee.toml doesn't parse as TOML")
                            for text in done.stdout.splitlines()), done.stdout)

    def test_criterion_7_a_cache_left_unignored_is_a_finding(self):
        """TSK-3120 criterion 7, REQ-2454: `cache = true` with `.lycheecache` unignored exits 1, and 0 once ignored."""
        settings = {".meowpaw/profile.toml": LINKS_PROFILE, "lychee.toml": "offline = true\nmax_retries = 0\ncache = true\n"}
        for name, ignore, status in (("unignored", {}, 1), ("ignored", {".gitignore": ".lycheecache\n"}, 0)):
            with self.subTest(case=name):
                done = self.check({**TWO, **settings, **ignore})
                self.assertEqual(done.returncode, status, done.stdout + done.stderr)
                said = ".lycheecache isn't ignored" in done.stdout.splitlines()
                self.assertEqual(said, bool(status), done.stdout)


SKILL_DIR = UNIT / "skills" / "markdown"
FORBIDS = re.compile(r"\b(never|must not|don't|do not)\b", re.IGNORECASE)


def blocks(name):
    """The file's paragraphs and list items, each one block; a file not written yet has none (RES-0075)."""
    path = SKILL_DIR / name
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return [block for block in re.split(r"\n\s*\n|\n(?=\s*(?:[-*]|\d+\.)\s)", text) if block.strip()]


class Prompt(unittest.TestCase):
    def assertSaid(self, name, *patterns):
        """Some one block of `name` matches every pattern, so the terms are said together and not scattered."""
        found = [b for b in blocks(name) if all(re.search(p, b, re.IGNORECASE) for p in patterns)]
        self.assertTrue(found, f"no block of {name} matches all of {patterns}")


class Reviewing(Prompt):
    """TSK-3130 criterion 1, REQ-0083: `reviewing.md` carries RES-0111's six reviewer points."""

    POINTS = {
        "the heading outline as the argument": (r"heading", r"outline", r"argument"),
        "a table against a list": (r"\btables?\b", r"\blists?\b"),
        "the language tag on a fence": (r"fence", r"language tag"),
        "reference links for a source cited more than twice": (r"reference[- ]links?", r"more than twice"),
        "links that survive a move": (r"\blinks?\b", r"\b(survives?|moved?|moving)\b"),
        "a diagram claiming what the prose doesn't": (r"diagram", r"\bprose\b"),
    }

    def test_criterion_1_reviewing_carries_each_reviewer_point(self):
        """TSK-3130 criterion 1, REQ-0083: each of the six points RES-0111 names is in `reviewing.md`."""
        for point, patterns in self.POINTS.items():
            with self.subTest(point=point):
                self.assertSaid("reviewing.md", *patterns)


class Skill(Prompt):
    """TSK-3130 criterion 2, REQ-0083: what the skill names, forbids and dates."""

    def test_criterion_2_the_skill_loads_reviewing_on_review(self):
        """TSK-3130 criterion 2, REQ-0083: the skill names `reviewing.md` as the file to load on review."""
        self.assertSaid("SKILL.md", r"reviewing\.md", r"\breview")

    def test_criterion_2_the_skill_forbids_markdownlint_cli_on_a_cli2_file(self):
        """TSK-3130 criterion 2, REQ-0083: running markdownlint-cli against a `.markdownlint-cli2.*` file is forbidden."""
        self.assertSaid("SKILL.md", FORBIDS.pattern, FRONT_END_CLI.pattern, r"\.markdownlint-cli2")

    def test_criterion_2_the_skill_forbids_an_unreachable_link_failing_unsaid(self):
        """TSK-3130 criterion 2, REQ-0083: failing a check on an unreachable link without saying so is forbidden."""
        self.assertSaid("SKILL.md", FORBIDS.pattern, r"unreachable", r"\bfail")

    def test_criterion_2_the_skill_forbids_a_spell_check_with_no_word_list(self):
        """TSK-3130 criterion 2, REQ-0083: a spell check with no project word list is forbidden."""
        self.assertSaid("SKILL.md", FORBIDS.pattern, r"spell", r"word list")

    def test_criterion_2_the_skill_names_meow_prose_as_the_writing_standard(self):
        """TSK-3130 criterion 2, REQ-0083: the skill names `meow-prose` as the owner of the writing standard."""
        self.assertSaid("SKILL.md", r"meow-prose", r"writing standard")

    def test_criterion_2_the_skill_names_the_versions_observed(self):
        """TSK-3130 criterion 2, REQ-0083: the skill names the tool versions RES-0294 observed."""
        for tool, version in (("lychee", "0.24.2"), ("markdownlint-cli2", "0.23.2"), ("markdownlint-cli", "0.49.1")):
            with self.subTest(tool=tool):
                self.assertSaid("SKILL.md", rf"{re.escape(tool)}`? {re.escape(version)}")


if __name__ == "__main__":
    unittest.main()
