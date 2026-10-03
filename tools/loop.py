#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Andrew Vasilyev <me@retran.me>
# SPDX-License-Identifier: Apache-2.0

"""Improve a prompt by measuring candidates against the text they replace.

SPC-1020 states the loop: the current text is the baseline, each candidate
changes one thing, every candidate runs on the same cases with the same run
count and the same judge, and every candidate is published, including the ones
that lost. This runs it over one unit and prints one table.

    python3 tools/loop.py plugins/*/                             # every unit, baseline only
    python3 tools/loop.py plugins/meow-core --candidates DIR     # and each candidate

A candidate is a directory under DIR holding `candidate.toml`, whose `change`
names the one thing it changes, and the files it replaces, laid out as they are
in the unit. Everything else is copied from the unit unchanged.

Every candidate runs on each model the prompts serve, Sonnet 5 and Opus 5.5 by
default, and lands only when it lands on every one of them. On one model, a
candidate lands when its delta holds and its token cost falls. Its delta
holds when it is no lower than the baseline's by more than twice their
combined standard error, because five runs of a model vary and a smaller fall
is indistinguishable from that variance. A candidate that scores better and
costs more is published with both numbers, and the owner decides.

In `--mode classifier` the cases carry a `defect` or a `clean` tag, the run has
no baseline arm, and the table reports how often each kind passed. That is how
SPC-1020 measures a prompt that blocks.

Every run grants the unit read access to its own directory. An installed unit
reads its own supporting files in a normal session, and the eval's sandbox
refuses any read outside the working directory, so without the grant a unit
that reads its own files measures the sandbox.

A case whose work writes files, such as a step that writes a record, needs
the runner to grant it the tool: `--allow-tool Write --allow-tool Edit`. The
runner grants nothing the case's own front matter names.

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

MODELS = ["claude-sonnet-5", "claude-opus-5-5"]
JUDGE = "claude-opus-5-5"
RUNS = 5
PROBE = "Reply with the word ok."
# ADR-1500: a case whose interval lies within this of zero scores the same
# without the unit, stated here so it is fixed before any run.
MARGIN = 0.10
# REQ-3026: the platform's default run count, which supports no claim.
PLATFORM_RUNS = 3


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


def git(unit, *args):
    return subprocess.run(["git", *args], cwd=unit, capture_output=True, text=True)


def threshold_commit(unit):
    """The commit the unit's thresholds were last committed at, with its time,
    or why the loop can't run: the file differs from that commit (REQ-0159)."""
    path = unit / "evals" / "thresholds.toml"
    if not path.exists():
        return None, None
    rel = str(path.relative_to(unit))
    tracked = git(unit, "ls-files", "--error-unmatch", rel).returncode == 0
    if not tracked or git(unit, "diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        return None, (f"{path} differs from the last commit; commit the thresholds before the run "
                      f"that judges against them (REQ-0159)")
    line = git(unit, "log", "-1", "--format=%h %cI", "--", rel).stdout.strip()
    return line or None, None


def baseline_graders(unit):
    """Each grader of `type: baseline`, a judged comparison whose order the
    runner doesn't document and the harness can't shuffle (REQ-0153)."""
    found = []
    for grader in sorted((unit / "evals").glob("*/graders/*.md")):
        if front_matter(grader).get("type", "").strip() == "baseline":
            found.append(grader)
    return found


def family(model):
    """The family a model identifier names, such as `claude` for `claude-opus-5-5`."""
    return model.split("-", 1)[0] if "-" in model else model


def judge_line(judge, models, runs):
    """What the header says about the judge and the run count (REQ-0160, REQ-3026, REQ-3028)."""
    lines = [f"Judge {judge}, of the {family(judge)} family; {runs} runs per arm."]
    if all(family(m) == family(judge) for m in models):
        lines.append("The judge is from the candidates' own family, so every judged score, a verdict "
                     "included, is a smoke check and no evidence for a claim (REQ-3028).")
    else:
        lines.append("The judge is from another family, so the result is no smoke check by family, and "
                     "still no claim, because which judge counts as stronger is unsettled (REQ-3028).")
    if judge in models:
        lines.append(f"The judge is also a candidate model, {judge}.")
    if runs <= PLATFORM_RUNS:
        lines.append(f"{runs} runs per arm supports no claim (REQ-3026).")
    return lines


def label(delta, se):
    """Whether a case separates the arms, scores the same, or can't yet be told (REQ-3022)."""
    if delta != delta:
        return "no arm without the unit"
    low, high = delta - 2 * se, delta + 2 * se
    if -MARGIN <= low and high <= MARGIN:
        return "delete: scores the same without the unit"
    if low > 0 or high < 0:
        return "separates"
    return "undetermined: run more"


def rate(passes):
    """A pass rate and its standard error, from a list of booleans."""
    n = len(passes)
    if not n:
        return float("nan"), 0.0, 0
    p = sum(passes) / n
    return p, math.sqrt(p * (1 - p) / n), n


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
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True,
                         stdin=subprocess.DEVNULL).stdout
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


def evaluate(root, args, out, mode, model):
    report = out / "result.json"
    cmd = ["claude", "plugin", "eval", str(root), "--runs", str(args.runs),
           "-j", str(args.jobs), "--model", model, "--judge-model", args.judge,
           "--trust-plugin", "--no-publish", "--threshold", "0",
           "--json", str(report), "--output-dir", str(out),
           "--allow-tools", f"Read(/{root.resolve()}/**)", *args.allow_tools]
    if args.cases:
        cmd += ["--case", args.cases]
    for tag in args.tags or []:
        cmd += ["--tag", tag]
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
        delta = mean(w) - mean(wo) if wo else float("nan")
        variance = (var(w) / len(w) if w else 0) + (var(wo) / len(wo) if wo else 0)
        cases[case["name"]] = {
            "with": mean(w),
            "without": mean(wo),
            "delta": delta,
            "var": variance,
            "se": math.sqrt(variance),
            "label": label(delta, math.sqrt(variance)),
            "runs": len(w),
        }
    k = len(cases)
    delta = mean([c["delta"] for c in cases.values()])
    se = math.sqrt(sum(c["var"] for c in cases.values())) / k if k else float("nan")
    return {"cases": cases, "delta": delta, "se": se, "errors": errors,
            "partial": result.get("partial", False), "cost": result.get("costUsd", 0)}


def classify(result, unit):
    """Per kind and per case: the pass rate with the unit and without it, each
    with its error, and the delta (REQ-0160, REQ-3022)."""
    kinds = {k: {"with": [], "without": []} for k in ("defect", "clean")}
    cases, errors = {}, 0
    for case in result["cases"]:
        arms = {}
        for arm in ("with", "without"):
            runs = case["arms"].get(arm) or []
            errors += sum(1 for r in runs if r.get("error"))
            arms[arm] = [bool(r["passed"]) for r in runs if not r.get("error")]
        for kind in kinds:
            if kind in tags(unit, case["name"]):
                for arm in arms:
                    kinds[kind][arm] += arms[arm]
        cases[case["name"]] = compare(arms["with"], arms["without"])
    return {"kinds": {k: compare(v["with"], v["without"]) for k, v in kinds.items()},
            "cases": cases, "errors": errors,
            "partial": result.get("partial", False), "cost": result.get("costUsd", 0)}


def compare(with_, without):
    """Two arms' pass rates, their errors and the delta's, as the report prints them."""
    w, w_se, n = rate(with_)
    wo, wo_se, _ = rate(without)
    delta = w - wo if without else float("nan")
    se = math.sqrt(w_se ** 2 + wo_se ** 2)
    return {"with": w, "with_se": w_se, "without": wo, "without_se": wo_se,
            "delta": delta, "se": se, "runs": n, "label": label(delta, se)}


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
    lines = ["| Candidate | Model | Change | Delta | 2SE | Tokens | Errors | Verdict |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['model']} | {r['change']} | {r['delta']:+.2f} | {2 * r['se']:.2f} | "
                     f"{r['tokens'] if r['tokens'] is not None else '-'} | {r['errors']} | {r['verdict']} |")
    for base in (r for r in rows if r["name"] == "baseline"):
        lines += per_case(base, limits)
    return "\n".join(lines)


def meets(score, limit):
    """Whether a case reached the minimum its committed threshold states (REQ-0159)."""
    if limit is None:
        return "no threshold set before the run"
    return "yes" if score >= limit else "no"


def per_case(base, limits):
    lines = ["", f"Per case, for the baseline on {base['model']}:", "",
              "| Case | Runs | With | Without | Delta | 2SE | Threshold | Meets it | Label |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, c in base["cases"].items():
        limit = limits.get(name)
        se = c["se"]
        lines.append(f"| {name} | {c['runs']} | {c['with']:.2f} | {c['without']:.2f} | {c['delta']:+.2f} | "
                     f"{2 * se:.2f} | {limit if limit is not None else '-'} | {meets(c['with'], limit)} | "
                     f"{c['label']} |")
    return lines


def table_classifier(rows, limits):
    lines = ["| Candidate | Model | Change | Kind | With | Without | Delta | 2SE | Runs | Label | Tokens | Errors |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        for kind, k in r["kinds"].items():
            if not k["runs"]:
                continue
            lines.append(f"| {r['name']} | {r['model']} | {r['change']} | {kind} | "
                         f"{k['with']:.2f} ±{2 * k['with_se']:.2f} | {k['without']:.2f} ±{2 * k['without_se']:.2f} | "
                         f"{k['delta']:+.2f} | {2 * k['se']:.2f} | {k['runs']} | {k['label']} | "
                         f"{r['tokens']} | {r['errors']} |")
    for base in (r for r in rows if r["name"] == "baseline"):
        lines += per_case(base, limits)
    return "\n".join(lines)


def loop(unit, args, entries):
    """Run the baseline and every candidate over one unit, and publish its table."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = unit / "evals" / "results" / f"loop-{stamp}"
    for n in range(2, 100):
        try:
            out.mkdir(parents=True)
            break
        except FileExistsError:
            out = out.with_name(f"loop-{stamp}-{n}")

    commit, refusal = threshold_commit(unit)
    if refusal:
        sys.exit(f"{unit.name}: {refusal}")
    comparisons = baseline_graders(unit)
    if comparisons:
        names = ", ".join(str(g.relative_to(unit)) for g in comparisons)
        sys.exit(f"{unit.name}: {names} is a judged comparison whose order the runner doesn't document "
                 f"and the harness can't shuffle (REQ-0153); rewrite it to judge one output")

    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        probe = tmp / "probe"
        probe.mkdir()
        for model in args.models:
            empty = input_tokens(model, probe)
            for name, change, overlay in entries:
                root = variant(unit, overlay, tmp / model / name / unit.name)
                result = evaluate(root, args, out / model / name, args.mode, model)
                row = (classify(result, root) if args.mode == "classifier" else summarise(result))
                row.update(name=name, change=change, model=model,
                           tokens=token_cost(root, args.loads, model, probe, empty))
                rows.append(row)
                print(f"{unit.name} {name} on {model}: done, ${row['cost']:.2f}", file=sys.stderr)

    baselines = {r["model"]: r for r in rows if r["name"] == "baseline"}
    if args.mode == "classifier":
        for r in rows:
            r["verdict"] = "baseline" if r["name"] == "baseline" else "see rates"
        text = table_classifier(rows, thresholds(unit))
    else:
        for r in rows:
            r["verdict"] = "baseline" if r["name"] == "baseline" else verdict(baselines[r["model"]], r)
        for name in {r["name"] for r in rows} - {"baseline"}:
            mine = [r for r in rows if r["name"] == name]
            if len(mine) > 1 and not all(r["verdict"] == "lands" for r in mine):
                for r in mine:
                    if r["verdict"] == "lands":
                        r["verdict"] = "holds here, loses on another model"
        text = table_delta(rows, thresholds(unit))

    head = "\n".join([
        f"{unit.name} at {stamp}: models {', '.join(args.models)}, ${sum(r['cost'] for r in rows):.2f}.",
        *judge_line(args.judge, args.models, args.runs),
        (f"Thresholds as committed at {commit}, before this run (REQ-0159)." if commit
         else "No thresholds file: no case gets a verdict (REQ-0159)."),
        "A regression is a fall in the delta, never in the absolute score (REQ-3036).",
    ])
    if any(r["partial"] for r in rows):
        head += "\nPartial: a cost ceiling or a usage limit stopped a run early."
    text = f"{head}\n\n{text}\n"
    (out / "loop.md").write_text(text, encoding="utf-8")
    (out / "loop.json").write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    print(text)
    print(f"written to {out}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("units", type=Path, nargs="+")
    ap.add_argument("--candidates", type=Path)
    ap.add_argument("--mode", choices=("delta", "classifier"), default="delta")
    ap.add_argument("--loads", nargs="+", default=["output-styles/*.md"],
                    help="globs, relative to the unit, for the text whose token cost is reported")
    ap.add_argument("--runs", type=int, default=RUNS)
    ap.add_argument("--cases")
    ap.add_argument("--tag", dest="tags", action="append",
                    help="run only the cases carrying this tag; repeat for several")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--model", dest="models", action="append",
                    help="a model to run the candidates on; repeat for several (default: Sonnet 5 and Opus 5.5)")
    ap.add_argument("--judge", default=JUDGE)
    ap.add_argument("--allow-tool", dest="allow_tools", action="append", default=[],
                    help="a further tool the runner grants each case, such as Write, for a case whose work writes files; repeat for more")
    args = ap.parse_args()
    args.models = args.models or MODELS

    units = [u.resolve() for u in args.units]
    if args.candidates and len(units) > 1:
        sys.exit("candidates replace one unit's files, so name exactly one unit")

    entries = [("baseline", "the text as it stands", None)]
    if args.candidates:
        for d in sorted(p for p in args.candidates.iterdir() if (p / "candidate.toml").exists()):
            change = tomllib.loads((d / "candidate.toml").read_text(encoding="utf-8"))["change"]
            entries.append((d.name, change, d))

    for unit in units:
        if not (unit / "evals").is_dir():
            print(f"{unit.name}: no evals, nothing to measure\n")
            continue
        if not has_cases(unit):
            print(f"{unit.name}: no eval case, nothing to measure\n")
            continue
        loop(unit, args, entries)
    return 0


def has_cases(unit):
    """Whether the unit's `evals/` holds a case, as a `prompt.md` one directory
    down or a `case.yaml` at any depth, and not only a hand run (REQ-3752)."""
    evals = unit / "evals"
    return any(evals.glob("*/prompt.md")) or any(evals.glob("**/case.yaml"))


if __name__ == "__main__":
    sys.exit(main())
