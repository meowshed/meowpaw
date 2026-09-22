#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Improve a prompt by measuring candidates against the text they replace.

SPC-1020 states the loop: the current text is the baseline, each candidate
changes one thing, every candidate runs on the same cases with the same run
count and the same judge, and every candidate is published, including the ones
that lost. This runs it over one unit and prints one table.

    python3 tools/loop.py plugins/meow-core                      # baseline only
    python3 tools/loop.py plugins/meow-core --candidates DIR     # and each candidate

A candidate is a directory under DIR holding `candidate.toml`, whose `change`
names the one thing it changes, and the files it replaces, laid out as they are
in the unit. Everything else is copied from the unit unchanged.

A candidate lands when its delta holds and its token cost falls. Its delta
holds when it is no lower than the baseline's by more than twice their
combined standard error, because five runs of a model vary and a smaller fall
is indistinguishable from that variance. A candidate that scores better and
costs more is published with both numbers, and the owner decides.

In `--mode classifier` the cases carry a `defect` or a `clean` tag, the run has
no baseline arm, and the table reports how often each kind passed. That is how
SPC-1020 measures a prompt that blocks.

Every run is a real model call, so the gate never runs this.
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path

MODEL = "claude-sonnet-5"
JUDGE = "claude-opus-5-5"
RUNS = 5
PROBE = "Reply with the word ok."


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    block = text[4 : text.index("\n---\n", 4)]
    return dict(
        (m.group(1), m.group(2).strip())
        for m in re.finditer(r"^([a-z_]+):\s*(.*)$", block, re.M)
    )


def tags(unit, case):
    fm = front_matter(unit / "evals" / case / "prompt.md")
    return set(re.findall(r"[\w-]+", fm.get("tags", "")))


def thresholds(unit):
    path = unit / "evals" / "thresholds.toml"
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8")).get("cases", {})


def variant(unit, overlay, into):
    """The unit as a candidate sees it: the unit, with the candidate's files on top."""
    shutil.copytree(unit, into, ignore=shutil.ignore_patterns("results"))
    if overlay is None:
        return into
    for src in overlay.rglob("*"):
        if src.is_file() and src.name != "candidate.toml":
            dst = into / src.relative_to(overlay)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return into


def input_tokens(model, cwd, prompt_file=None):
    """Every input token one print-mode call reads, cached or not."""
    cmd = ["claude", "-p", PROBE, "--model", model, "--output-format", "json", "--max-turns", "1"]
    if prompt_file:
        cmd += ["--append-system-prompt-file", str(prompt_file)]
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True).stdout
    result = [e for e in json.loads(out) if e.get("type") == "result"][-1]["usage"]
    return sum(result.get(k, 0) for k in
               ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))


def token_cost(root, loads, model, cwd, empty):
    """What the unit's loaded text costs, measured as the model's own tokenizer counts it.

    The text is appended to a system prompt and the difference against an empty
    call is the cost, so it is a count and not an estimate from characters.
    """
    files = sorted(p for pattern in loads for p in root.glob(pattern))
    if not files:
        return 0
    joined = cwd / "loaded.md"
    joined.write_text("\n\n".join(p.read_text(encoding="utf-8") for p in files), encoding="utf-8")
    return input_tokens(model, cwd, joined) - empty


def evaluate(root, args, out, mode):
    report = out / "result.json"
    cmd = ["claude", "plugin", "eval", str(root), "--runs", str(args.runs),
           "-j", str(args.jobs), "--model", args.model, "--judge-model", args.judge,
           "--trust-plugin", "--no-publish", "--threshold", "0",
           "--json", str(report), "--output-dir", str(out)]
    if mode == "classifier":
        cmd += ["--ablation", "none"]
    if args.cases:
        cmd += ["--case", args.cases]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if not report.exists():
        sys.exit(f"the runner wrote no result, exit {run.returncode}:\n{run.stderr[-2000:]}")
    return json.loads(report.read_text(encoding="utf-8"))


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def var(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def summarise(result):
    """Per case: the two arms' scores, the delta and its variance; overall: the same."""
    cases, errors = {}, 0
    for case in result["cases"]:
        arms = {}
        for arm in ("with", "without"):
            runs = case["arms"].get(arm) or []
            errors += sum(1 for r in runs if r.get("error"))
            arms[arm] = [r["score"] for r in runs if not r.get("error") and r.get("score") is not None]
        w, wo = arms["with"], arms["without"]
        cases[case["name"]] = {
            "with": mean(w),
            "without": mean(wo),
            "delta": mean(w) - mean(wo) if wo else float("nan"),
            "var": (var(w) / len(w) if w else 0) + (var(wo) / len(wo) if wo else 0),
            "runs": len(w),
        }
    k = len(cases)
    delta = mean([c["delta"] for c in cases.values()])
    se = math.sqrt(sum(c["var"] for c in cases.values())) / k if k else float("nan")
    return {"cases": cases, "delta": delta, "se": se, "errors": errors,
            "partial": result.get("partial", False), "cost": result.get("costUsd", 0)}


def classify(result, unit):
    kinds = {"defect": [], "clean": []}
    errors = 0
    for case in result["cases"]:
        runs = case["arms"].get("with") or []
        errors += sum(1 for r in runs if r.get("error"))
        for kind in kinds:
            if kind in tags(unit, case["name"]):
                kinds[kind] += [r["passed"] for r in runs if not r.get("error")]
    return {"defect": mean(kinds["defect"]), "clean": mean(kinds["clean"]),
            "n": {k: len(v) for k, v in kinds.items()}, "errors": errors,
            "partial": result.get("partial", False), "cost": result.get("costUsd", 0)}


def verdict(base, cand):
    if cand["tokens"] is None or base["tokens"] is None:
        return "no token count"
    margin = 2 * math.sqrt(base["se"] ** 2 + cand["se"] ** 2)
    holds = cand["delta"] >= base["delta"] - margin
    better = cand["delta"] > base["delta"] + margin
    cheaper = cand["tokens"] < base["tokens"]
    if holds and cheaper:
        return "lands"
    if better and not cheaper:
        return "better and costlier: owner decides"
    if not holds:
        return f"loses: delta fell by more than {margin:.2f}"
    return "loses: costs no less"


def table_delta(rows, limits):
    lines = ["| Candidate | Change | Delta | 2SE | Tokens | Errors | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['change']} | {r['delta']:+.2f} | {2 * r['se']:.2f} | "
                     f"{r['tokens'] if r['tokens'] is not None else '-'} | {r['errors']} | {r['verdict']} |")
    base = rows[0]
    lines += ["", f"Per case, for {base['name']}:", "",
              "| Case | With | Without | Delta | Threshold | Meets it | Separates |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, c in base["cases"].items():
        limit = limits.get(name)
        meets = "no threshold set" if limit is None else ("yes" if c["with"] >= limit else "no")
        separates = "no, cannot discriminate" if c["with"] == c["without"] else "yes"
        lines.append(f"| {name} | {c['with']:.2f} | {c['without']:.2f} | {c['delta']:+.2f} | "
                     f"{limit if limit is not None else '-'} | {meets} | {separates} |")
    return "\n".join(lines)


def table_classifier(rows):
    lines = ["| Candidate | Change | Defects blocked | Clean passed | Tokens | Errors | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['change']} | {r['defect']:.2f} (n={r['n']['defect']}) | "
                     f"{r['clean']:.2f} (n={r['n']['clean']}) | {r['tokens']} | {r['errors']} | {r['verdict']} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("unit", type=Path)
    ap.add_argument("--candidates", type=Path)
    ap.add_argument("--mode", choices=("delta", "classifier"), default="delta")
    ap.add_argument("--loads", nargs="+", default=["output-styles/*.md"],
                    help="globs, relative to the unit, for the text whose token cost is reported")
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--cases")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--judge", default=JUDGE)
    args = ap.parse_args()

    unit = args.unit.resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = unit / "evals" / "results" / f"loop-{stamp}"
    out.mkdir(parents=True)

    entries = [("baseline", "the text as it stands", None)]
    if args.candidates:
        for d in sorted(p for p in args.candidates.iterdir() if (p / "candidate.toml").exists()):
            change = tomllib.loads((d / "candidate.toml").read_text(encoding="utf-8"))["change"]
            entries.append((d.name, change, d))

    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        probe = tmp / "probe"
        probe.mkdir()
        empty = input_tokens(args.model, probe)
        for name, change, overlay in entries:
            root = variant(unit, overlay, tmp / name / unit.name)
            result = evaluate(root, args, out / name, args.mode)
            row = (classify(result, root) if args.mode == "classifier" else summarise(result))
            row.update(name=name, change=change,
                       tokens=token_cost(root, args.loads, args.model, probe, empty))
            rows.append(row)
            print(f"{name}: done, ${row['cost']:.2f}", file=sys.stderr)

    if args.mode == "classifier":
        for r in rows:
            r["verdict"] = "baseline" if r is rows[0] else "see rates"
        text = table_classifier(rows)
    else:
        rows[0]["verdict"] = "baseline"
        for r in rows[1:]:
            r["verdict"] = verdict(rows[0], r)
        text = table_delta(rows, thresholds(unit))

    head = (f"{unit.name} at {stamp}: model {args.model}, judge {args.judge}, "
            f"{args.runs} runs per arm, ${sum(r['cost'] for r in rows):.2f}.\n"
            f"The judge is from the model's own family, so every judged score is a "
            f"smoke check (REQ-3028). A regression is a fall in the delta, never in the "
            f"absolute score (REQ-3036).")
    if any(r["partial"] for r in rows):
        head += "\nPartial: a cost ceiling or a usage limit stopped a run early."
    text = f"{head}\n\n{text}\n"
    (out / "loop.md").write_text(text, encoding="utf-8")
    (out / "loop.json").write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    print(text)
    print(f"written to {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
