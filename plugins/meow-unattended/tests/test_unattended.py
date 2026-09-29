# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Fixtures for what SPC-1200 states `meow-unattended plan` reads, prints and writes.

Each fixture is a scratch git repository with its home and its state directory
isolated, so a snapshot lands under `<fixture>/state/meowpaw/unattended/<key>/`
and nowhere a person keeps state. `MEOW_UNATTENDED_BIN` names the launcher to
test. Where no launcher exists yet, a run reports exit 127 and prints nothing,
so every check fails on what the program should have printed, and not on a
missing file (RES-0075). Each check counts what it matched and fails on a count
of zero where one was expected (EPC-1900 criterion 9).
"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

UNIT = Path(__file__).resolve().parent.parent
BIN = Path(os.environ.get("MEOW_UNATTENDED_BIN", UNIT / "bin" / "meow-unattended"))

GIT = '[git]\ntrunk = "main"\n'
RECORD = '[record]\nroot = "project"\n'
PLUGIN = '{{"name": "{name}", "version": "0.3.1", "description": "A fixture unit."}}\n'
UNITS = {f"units/{name}/.claude-plugin/plugin.json": PLUGIN.format(name=name) for name in ("alpha", "beta")}
REQUIRED = {
    "permission_mode": '"dontAsk"',
    "budget_usd": "2.5",
    "gates": '["verify", "review"]',
    "units": '["units/alpha", "units/beta"]',
}
NO_TABLE = "unresolved: no [unattended] table in .meowpaw/profile.toml"


def table(**keys):
    """An `[unattended]` table holding the required keys, each overridden or, where None, left out."""
    lines = ["[unattended]"]
    for key, value in {**REQUIRED, **keys}.items():
        if value is not None:
            lines.append(f"{key} = {value}")
    return "\n".join(lines) + "\n"


def record(status_of):
    """Record files under `project/`, each with the front matter its kind carries."""
    files = {}
    for path, status in status_of.items():
        ident = Path(path).name[:8]
        artifact = "requirement" if ident.startswith("REQ") else "adr"
        files[f"project/{path}"] = (f"---\nid: {ident}\nartifact: {artifact}\nstatus: {status}\n"
                                    f"revised: 2026-09-29\n---\n\n# {ident}\n\nA fixture record.\n")
    return files


RECORD_FILES = record({
    "requirements/REQ-0001-first.md": "approved",
    "requirements/REQ-0002-second.md": "approved",
    "requirements/REQ-0003-third.md": "draft",
    "adrs/ADR-0001-first.md": "approved",
    "adrs/ADR-0002-second.md": "draft",
})
APPROVED = ("requirements/REQ-0001-first.md", "requirements/REQ-0002-second.md", "adrs/ADR-0001-first.md")


class Repository:
    def __init__(self, files):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name).resolve()
        self.root = base / "repo"
        self.home = base / "home"
        self.state = base / "state"
        for directory in (self.root, self.home, self.state):
            directory.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("MISE_", "__MISE_", "MEOWPAW_", "XDG_STATE_HOME"))}
        self.env.update(HOME=str(self.home), XDG_STATE_HOME=str(self.state), GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, env=self.env)
        self.write(files)
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True, env=self.env)

    def write(self, files):
        for name, text in files.items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

    def run(self, *args, **env):
        if not BIN.exists():
            return subprocess.CompletedProcess([str(BIN), *args], 127, "", f"no launcher at {BIN}\n")
        return subprocess.run([str(BIN), *args], cwd=self.root, capture_output=True, text=True,
                              env={**self.env, **env}, stdin=subprocess.DEVNULL)

    def key(self):
        """The work tree's key, as the evidence ledger derives it (SPC-1040)."""
        return hashlib.sha256(str(self.root).encode()).hexdigest()[:16]

    def snapshot_folder(self):
        return self.state / "meowpaw" / "unattended" / self.key()

    def state_files(self):
        return sorted(p for p in self.state.rglob("*") if p.is_file())

    def tree(self):
        return subprocess.run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"],
                              cwd=self.root, capture_output=True, text=True, env=self.env).stdout


def tokens(output):
    """Every whitespace-separated word of the output, so a flag and its value read as neighbours."""
    return [word for line in output.splitlines() for word in line.split() if word != "\\"]


def following(words, flag):
    """The word after each occurrence of `flag`."""
    return [words[i + 1] for i, word in enumerate(words[:-1]) if word == flag]


class Fixture(unittest.TestCase):
    def repo(self, files):
        repository = Repository(files)
        self.addCleanup(repository.tmp.cleanup)
        return repository

    def profile(self, *tables):
        return {".meowpaw/profile.toml": "".join(tables), **UNITS}

    def refused(self, files, expected):
        repository = self.repo(files)
        done = repository.run("plan")
        said = done.stdout + done.stderr
        self.assertEqual(done.returncode, 3, said)
        self.assertEqual(said.count(expected), 1, said)
        self.assertEqual(repository.state_files(), [], said)
        return said

    def plan(self, repository, *args, **env):
        """Runs `plan`, and returns its output, its words and the snapshot `--settings` names."""
        done = repository.run("plan", *args, **env)
        said = done.stdout + done.stderr
        self.assertEqual(done.returncode, 0, said)
        words = tokens(done.stdout)
        settings = following(words, "--settings")
        self.assertEqual(len(settings), 1, done.stdout)
        return done.stdout, words, Path(settings[0])

    def snapshot(self, files, **env):
        repository = self.repo(files)
        output, _, path = self.plan(repository, **env)
        self.assertTrue(path.is_file(), f"no snapshot at {path}\n{output}")
        return repository, output, path, json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def deny(snapshot):
        return snapshot["permissions"]["deny"]


class Refusals(Fixture):
    """TSK-3300 criteria 1 to 3, REQ-2388: a missing or wrong authority is unresolved, exit 3, no snapshot."""

    def test_no_table(self):
        """TSK-3300 criterion 1, REQ-2388: a profile with no `[unattended]` table is unresolved."""
        self.refused(self.profile(GIT, RECORD), NO_TABLE)

    def test_no_profile(self):
        """TSK-3300 criterion 1, REQ-2388: no profile at all is unresolved the same way (SPC-1200)."""
        self.refused(dict(UNITS), NO_TABLE)

    def test_each_required_key_missing(self):
        """TSK-3300 criterion 2, REQ-2388: each missing required key is named, with exit 3."""
        checked = 0
        for key in REQUIRED:
            with self.subTest(key=key):
                self.refused(self.profile(GIT, table(**{key: None})),
                             f"unresolved: [unattended] {key} is not declared")
                checked += 1
        self.assertEqual(checked, 4)

    def test_refused_values(self):
        """TSK-3300 criterion 3, REQ-2388: bypassPermissions, an unknown gate, a zero budget and an
        unguarded `merge_protected` are each refused, naming the value."""
        cases = {
            "bypassPermissions": (table(permission_mode='"bypassPermissions"'),
                                  "unresolved: [unattended] permission_mode bypassPermissions is refused"),
            "unknown gate": (table(gates='["verify", "deploy"]'),
                             "unresolved: [unattended] gates names deploy, which is not a gate"),
            "zero budget": (table(budget_usd="0"),
                            "unresolved: [unattended] budget_usd 0 is not a positive number"),
            "merge_protected": (table(merge_protected="true"),
                                "unresolved: merge_protected is true and gates lacks merge"),
        }
        checked = 0
        for name, (text, expected) in cases.items():
            with self.subTest(case=name):
                self.refused(self.profile(GIT, text), expected)
                checked += 1
        self.assertEqual(checked, 4)

    def test_env_block_refused(self):
        """TSK-3310 criterion 4, REQ-2392: an `env` block with two keys in `.claude/settings.json`, and
        in `.claude/settings.local.json`, is unresolved naming the file and both keys, with exit 3."""
        env = json.dumps({"env": {"FIXTURE_ONE": "1", "FIXTURE_TWO": "2"}}) + "\n"
        checked = 0
        for name in (".claude/settings.json", ".claude/settings.local.json"):
            with self.subTest(file=name):
                said = self.refused({**self.profile(GIT, table()), name: env}, f"unresolved: {name} sets env ")
                lines = [line for line in said.splitlines() if f"unresolved: {name} sets env " in line]
                self.assertEqual(len(lines), 1, said)
                for key in ("FIXTURE_ONE", "FIXTURE_TWO"):
                    self.assertEqual(lines[0].count(key), 1, said)
                checked += 1
        self.assertEqual(checked, 2)


THREE = {
    "units/c": ("gamma", "2.0.1"),
    "units/a": ("alpha", "1.2.3"),
    "units/b": ("beta", "0.4.0"),
}


def walk(value):
    """Every object nested anywhere in a JSON value."""
    if isinstance(value, dict):
        yield value
        children = value.values()
    elif isinstance(value, list):
        children = value
    else:
        return
    for child in children:
        yield from walk(child)


def command_line(output):
    """The printed command, from the line that starts `claude` to the `--settings` flag."""
    start = re.search(r"^\s*claude\b", output, re.MULTILINE)
    if start is None:
        return ""
    end = output.find("--settings", start.start())
    return output[start.start():end if end >= 0 else len(output)]


class Units(Fixture):
    """TSK-3310 criteria 1 to 3, REQ-2392: `plan` loads each unit by name and nothing by discovery."""

    def test_url_and_folder_refused(self):
        """TSK-3310 criterion 1, REQ-2392: a URL entry and a folder of units that is no unit itself are
        each unresolved, naming the entry, with exit 3 and no snapshot."""
        cases = {
            "URL": ('["https://example.com/units/alpha"]',
                    "unresolved: unit https://example.com/units/alpha is a URL, and a unit loads from a directory"),
            "folder of units": ('["units"]', "unresolved: unit units is not a unit's own directory"),
        }
        checked = 0
        for name, (units, expected) in cases.items():
            with self.subTest(case=name):
                self.refused(self.profile(GIT, table(units=units)), expected)
                checked += 1
        self.assertEqual(checked, 2)

    @staticmethod
    def three_units():
        files = {f"{path}/.claude-plugin/plugin.json": json.dumps({"name": name, "version": version}) + "\n"
                 for path, (name, version) in THREE.items()}
        declared = "[" + ", ".join(f'"{path}"' for path in THREE) + "]"
        return {".meowpaw/profile.toml": GIT + table(units=declared), **files}

    def test_one_plugin_dir_for_each_unit(self):
        """TSK-3310 criterion 2, REQ-2392: `--bare` and exactly one `--plugin-dir` for each of three
        units in the declared order, and the output and the snapshot name each unit with the `name` and
        `version` its `plugin.json` holds."""
        repository, output, _, snapshot = self.snapshot(self.three_units())
        words = tokens(command_line(output))
        self.assertEqual(words.count("--bare"), 1, output)
        loaded = [(repository.root / value).resolve() for value in following(words, "--plugin-dir")]
        self.assertEqual(loaded, [(repository.root / path).resolve() for path in THREE], output)
        named = [obj for obj in walk(snapshot) if {"name", "version"} <= obj.keys()]
        checked = 0
        for name, version in THREE.values():
            with self.subTest(unit=name):
                lines = [line for line in output.splitlines()
                         if re.search(rf"\b{name}\b", line) and version in line]
                self.assertGreaterEqual(len(lines), 1, output)
                matched = [obj for obj in named if obj["name"] == name and obj["version"] == version]
                self.assertEqual(len(matched), 1, json.dumps(snapshot, indent=2))
                checked += 1
        self.assertEqual(checked, 3)

    def test_repository_hooks_and_servers_not_named(self):
        """TSK-3310 criterion 3, REQ-2392: a server in `.mcp.json` and a hook in `.claude/settings.json`
        are named by neither the command line nor the snapshot, while each declared unit is."""
        server = "fixture-discovered-server"
        hook = "fixture-discovered-hook.sh"
        files = {
            **self.three_units(),
            ".mcp.json": json.dumps({"mcpServers": {server: {"command": server}}}) + "\n",
            ".claude/settings.json": json.dumps({"hooks": {"SessionStart": [
                {"hooks": [{"type": "command", "command": hook}]}]}}) + "\n",
        }
        _, output, path, snapshot = self.snapshot(files)
        content = path.read_text(encoding="utf-8")
        command = command_line(output)
        self.assertEqual(len(following(tokens(command), "--plugin-dir")), 3, output)
        for text, where in ((command, "command line"), (content, "snapshot")):
            for name in (server, hook, ".mcp.json"):
                with self.subTest(where=where, name=name):
                    self.assertEqual(text.count(name), 0, text)
        named = [obj for obj in walk(snapshot) if {"name", "version"} <= obj.keys()]
        self.assertEqual(sorted((obj["name"], obj["version"]) for obj in named), sorted(THREE.values()),
                         content)


class Plan(Fixture):
    """TSK-3300 criteria 4, 5 and 10, REQ-2388: the printed plan states the declared posture."""

    def test_empty_gates_is_a_declaration(self):
        """TSK-3300 criterion 4, REQ-2388: `gates = []` declares no gate crossed, and `plan` exits 0."""
        repository = self.repo(self.profile(GIT, table(gates="[]")))
        done = repository.run("plan")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertNotIn("unresolved", done.stdout + done.stderr)
        self.assertEqual(len(following(tokens(done.stdout), "--settings")), 1, done.stdout)

    def test_command_line_states_the_posture(self):
        """TSK-3300 criterion 5, REQ-2388: the command carries the declared mode and budget, and the
        flags that keep the run from asking or loading by discovery."""
        repository = self.repo(self.profile(GIT, table()))
        output, words, path = self.plan(repository)
        for flag in ("claude", "-p", "--bare", "--permission-prompts", "--disallowed-tools", "--output-format",
                     "--verbose", "--max-budget-usd", "--permission-mode"):
            with self.subTest(flag=flag):
                self.assertGreaterEqual(words.count(flag), 1, output)
        self.assertEqual(following(words, "--permission-mode"), ["dontAsk"], output)
        self.assertEqual(following(words, "--max-budget-usd"), ["2.5"], output)
        self.assertEqual(following(words, "--permission-prompts"), ["none"], output)
        self.assertEqual(following(words, "--disallowed-tools"), ["AskUserQuestion"], output)
        self.assertEqual(following(words, "--output-format"), ["stream-json"], output)
        self.assertTrue(path.is_absolute(), output)
        self.assertEqual(path.parent, repository.snapshot_folder(), output)

    def test_output_states_the_limits(self):
        """TSK-3300 criterion 10, REQ-2388: the output states the four limits of the deny rules, the
        key the command needs and that a record approved later needs a new plan."""
        repository = self.repo(self.profile(GIT, RECORD, table()))
        repository.write(RECORD_FILES)
        output, _, _ = self.plan(repository)
        stated = {
            "a Bash rule stops only the forms it matches": r"git -C \. push origin main",
            "an Edit rule misses a script": r"script that opens the file",
            "a merge through the code host": r"code host",
            "a new record retires an approved one": r"supersedes or withdraws",
            "the command needs the key": r"ANTHROPIC_API_KEY",
            "a record approved later needs a new plan": r"approved after this plan",
        }
        for name, pattern in stated.items():
            with self.subTest(statement=name):
                self.assertGreaterEqual(len(re.findall(pattern, output, re.IGNORECASE)), 1, output)


class Snapshot(Fixture):
    """TSK-3300 criteria 6 to 8, REQ-2388: the snapshot `--settings` names holds the run's authority."""

    def test_denies_its_own_authority(self):
        """TSK-3300 criterion 6, REQ-2388: the snapshot denies Edit on the profile, `.claude` and its own
        folder, is named for its SHA-256 and holds no apiKeyHelper."""
        repository, output, path, snapshot = self.snapshot(self.profile(GIT, table()))
        deny = self.deny(snapshot)
        for rule in (f"Edit(/{repository.root}/.meowpaw/**)", f"Edit(/{repository.root}/.claude/**)",
                     f"Edit(/{path.parent}/**)"):
            with self.subTest(rule=rule):
                self.assertEqual(deny.count(rule), 1, deny)
        content = path.read_bytes()
        self.assertEqual(path.name, hashlib.sha256(content).hexdigest() + ".json")
        self.assertNotIn("apiKeyHelper", content.decode("utf-8"))
        self.assertEqual(len(re.findall(r"^\?\? ", repository.tree(), re.MULTILINE)), 0, repository.tree())

    def test_unchanged_after_the_profile_changes(self):
        """TSK-3300 criterion 6, REQ-2388: a later change to the profile leaves an earlier snapshot's
        content and hash unchanged."""
        repository, _, first, _ = self.snapshot(self.profile(GIT, table()))
        before = first.read_bytes()
        repository.write({".meowpaw/profile.toml": GIT + table(budget_usd="4")})
        _, words, second = self.plan(repository)
        self.assertEqual(following(words, "--max-budget-usd"), ["4"])
        self.assertNotEqual(second, first)
        self.assertTrue(first.is_file(), f"{first} was removed")
        self.assertEqual(first.read_bytes(), before)
        self.assertEqual(first.name, hashlib.sha256(before).hexdigest() + ".json")

    def test_push_rules(self):
        """TSK-3300 criterion 7, REQ-2388: the trunk's three push rules are denied unless
        `merge_protected = true` with `merge` in `gates`."""
        rules = ("Bash(git push *main*)", "Bash(git push)", "Bash(git push *HEAD*)")
        _, _, _, guarded = self.snapshot(self.profile(GIT, table()))
        for rule in rules:
            with self.subTest(merge_protected="absent", rule=rule):
                self.assertEqual(self.deny(guarded).count(rule), 1, self.deny(guarded))
        _, _, _, open_ = self.snapshot(self.profile(GIT, table(merge_protected="true",
                                                               gates='["verify", "merge"]')))
        deny = self.deny(open_)
        self.assertGreaterEqual(sum(rule.startswith("Edit(") for rule in deny), 3, deny)
        self.assertEqual([rule for rule in deny if rule.startswith("Bash(git push")], [], deny)

    def test_approved_records_are_denied(self):
        """TSK-3300 criterion 8, REQ-2388: each approved requirement and decision is denied Edit, none is
        where `amend_approved = true`, and no `[record]` says there is no record to protect."""
        repository, _, _, denied = self.snapshot({**self.profile(GIT, RECORD, table()), **RECORD_FILES})
        prefix = f"Edit(/{repository.root}/project/"
        on_record = sorted(rule for rule in self.deny(denied) if rule.startswith(prefix))
        self.assertEqual(on_record, sorted(f"{prefix}{path})" for path in APPROVED), self.deny(denied))

        repository, _, _, amended = self.snapshot({**self.profile(GIT, RECORD, table(amend_approved="true")),
                                                   **RECORD_FILES})
        deny = self.deny(amended)
        self.assertGreaterEqual(sum(rule.startswith("Edit(") for rule in deny), 3, deny)
        self.assertEqual([rule for rule in deny if rule.startswith(f"Edit(/{repository.root}/project/")], [],
                         deny)

        _, output, _, _ = self.snapshot({**self.profile(GIT, table()), **RECORD_FILES})
        self.assertEqual(output.count("no record to protect"), 1, output)


class State(Fixture):
    """TSK-3300 criterion 9, REQ-2388: state writing can be switched off, and kept plans purged."""

    def test_state_off(self):
        """TSK-3300 criterion 9, REQ-2388: with `MEOWPAW_STATE=off`, `plan` writes no file and says no
        snapshot was kept."""
        repository = self.repo(self.profile(GIT, table()))
        done = repository.run("plan", MEOWPAW_STATE="off")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(len(re.findall(r"no snapshot (was )?kept", done.stdout, re.IGNORECASE)), 1, done.stdout)
        self.assertEqual(repository.state_files(), [], done.stdout)
        self.assertEqual(len(re.findall(r"^\?\? ", repository.tree(), re.MULTILINE)), 0, repository.tree())
        self.assertGreaterEqual(done.stdout.count("--permission-mode"), 1, done.stdout)

    def test_purge(self):
        """TSK-3300 criterion 9, REQ-2388: `plan --purge` removes every snapshot of the work tree."""
        repository = self.repo(self.profile(GIT, table()))
        _, _, first = self.plan(repository)
        repository.write({".meowpaw/profile.toml": GIT + table(budget_usd="7")})
        _, _, second = self.plan(repository)
        kept = sorted(repository.snapshot_folder().glob("*.json"))
        self.assertEqual(kept, sorted((first, second)))
        done = repository.run("plan", "--purge")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertFalse(first.exists(), done.stdout)
        self.assertFalse(second.exists(), done.stdout)
        self.assertEqual(sorted(repository.snapshot_folder().glob("*.json")), [], done.stdout)


if __name__ == "__main__":
    unittest.main()
