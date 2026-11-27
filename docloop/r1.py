"""The R1 benchmark: run the four registered corpora and judge them against the registered targets.

    python -m docloop.r1 run --corpus prometheus --workdir /tmp/r1 --out out      needs HF_TOKEN
    python -m docloop.r1 summarize --in out --out docs/benchmarks                  no model

See docs/r1-preregistration.md. A run is refused if hybrid search fell back to word search.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .replay import _as_ranked, _at, _mrr, _periods, replay, to_markdown
from .targets import CORPORA, TARGETS, check, pass_gain, pass_scope, release_verdict

CONFIG = Path(__file__).resolve().parent.parent / "benchmarks" / "r1-corpora.json"


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def prepare(corpus: dict, workdir: str | Path) -> Path:
    """Clone the corpus if needed and check out the pinned commit."""
    repo = Path(workdir) / corpus["slug"]
    if not repo.is_dir():
        subprocess.run(["git", "clone", "-q", corpus["repo"], str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--detach", corpus["ref"]], check=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, check=True, text=True).stdout.strip()
    if not head.startswith(corpus["ref"]):
        raise RuntimeError(f"{corpus['name']}: checked out {head[:8]}, expected {corpus['ref']}")
    return repo


def _figures(events: list[dict]) -> dict:
    newer = _periods(events).get("newer half", [])
    if not newer:
        return {"top_3_hit": None, "mrr": None}
    return {"top_3_hit": _at(newer, _as_ranked, 3)["hit_rate"], "mrr": _mrr(newer, _as_ranked)}


def _gain(before: dict, after: dict) -> dict:
    if None in (*before.values(), *after.values()):
        return {"hit_at_3_gain": None, "mrr_gain": None, "kept": False}
    return pass_gain(before, after)


def run(corpus: dict, repo: str | Path, out_dir: str | Path, searcher, label: str, judge, progress=None) -> dict:
    if searcher is None or label.startswith("lexical"):
        raise RuntimeError(f"search fell back to words ({label}); a hybrid benchmark cannot report that")
    common = dict(roots=corpus["roots"], limit=corpus["limit"], max_pages=corpus["max_pages"],
                  exclude=corpus.get("exclude") or [], skip_message=corpus.get("skip_message"))
    lexical = replay(repo, **common)
    report = replay(repo, searcher=searcher, judge=judge, progress=progress, **common)
    newer_triage = report["triage_step"]["by_period"].get("newer half", {})
    p1, p2 = _figures(lexical["events"]), _figures(report["events"])
    p3 = {"top_3_hit": newer_triage.get("top_3_hit_likely_first"), "mrr": newer_triage.get("mrr_likely_first")}
    report.update({
        "corpus": corpus["name"], "slug": corpus["slug"], "kind": corpus["kind"], "repo_url": corpus["repo"],
        "ref": corpus["ref"], "search": label, "reader": judge.name, "model_calls": judge.calls,
        "unparsed_replies": judge.unparsed, "check": check(report),
        "words_only_summary": lexical["summary"],
        "passes": {"pass1_words": {"figures": p1},
                   "pass2_hybrid": {"figures": p2, "gain": _gain(p1, p2)},
                   "pass3_reading": {"figures": p3, "gain": _gain(p2, p3)}}})
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{corpus['slug']}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (out / f"{corpus['slug']}.md").write_text(to_markdown(report, f"R1: {corpus['name']}"), encoding="utf-8")
    return report


def _pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:.0f}%"


def summarize(in_dir: str | Path, out_dir: str | Path) -> dict:
    cfg = load_config()
    found = {}
    for corpus in cfg["corpora"]:
        f = Path(in_dir) / f"{corpus['slug']}.json"
        if f.is_file():
            found[corpus["name"]] = json.loads(f.read_text(encoding="utf-8"))
    missing = [c["slug"] for c in cfg["corpora"] if c["name"] not in found]
    verdict = release_verdict(found)
    if missing and verdict["passed"] is True:
        verdict["passed"] = None
    scope = {}
    if not missing:
        for p in ("pass2_hybrid", "pass3_reading"):
            scope[p] = pass_scope({n: r["passes"][p]["gain"]["kept"] for n, r in found.items()})
    summary = {"verdict": verdict, "missing": missing, "pass_scope": scope,
               "corpora": {n: {"head": r["head"], "events": r["summary"]["overall"]["events"], "search": r["search"],
                               "reader": r["reader"], "model_calls": r["model_calls"],
                               "unparsed_replies": r["unparsed_replies"],
                               "newer_half": {**{k: r["summary"]["by_period"].get("newer half", {}).get(k) for k in ("hit_rate", "mean_recall")},
                                              **{k: r["triage_step"]["by_period"].get("newer half", {}).get(k)
                                                 for k in ("precision_likely", "precision_full_list", "right_in_likely", "wrong_in_also_check")}},
                               "passes": r["passes"]} for n, r in found.items()}}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "r1-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (out / "r1-report.md").write_text(_markdown(summary, found), encoding="utf-8")
    return summary


def _markdown(summary: dict, found: dict) -> str:
    verdict = summary["verdict"]["passed"]
    word = {True: "met on every corpus", False: "not met", None: "undecided"}[verdict]
    out = ["# R1 accuracy: results", "",
           "Registered in [r1-preregistration.md](../r1-preregistration.md) before any R1 measurement. "
           "Each corpus is judged on its own, on the newer half by date. Nothing is combined across corpora.", "",
           "## Verdict", "", f"Release R1 acceptance test: **{word}**.", ""]
    if summary["missing"]:
        out += [f"Corpora not yet run: {', '.join(summary['missing'])}.", ""]
    out += ["| Corpus | Kind | Events scored | Commit | Search | Reader | Model calls |", "| --- | --- | ---: | --- | --- | --- | ---: |"]
    for name, r in found.items():
        out.append(f"| {name} | {r['kind']} | {r['summary']['overall']['events']} | `{r['head'][:8]}` | {r['search']} | "
                   f"{r['reader']} | {r['model_calls']} ({r['unparsed_replies']} unreadable) |")
    labels = {"hit_rate": "Hit rate", "mean_recall": "Mean recall", "precision_likely": "Precision of the likely list",
              "right_in_likely": "Right pages placed in likely", "wrong_in_also_check": "Wrong pages placed in also check"}
    for name, r in found.items():
        c = r["check"]
        out += ["", f"## {name}", ""]
        if c["status"] != "evaluated":
            out += [f"Reported but not counted: {c['status']} ({c['events']} scored events, floor {60}).", ""]
            continue
        out += [f"Result: **{'every target met' if c['all_met'] else 'targets missed'}**.", "",
                "| Measure (newer half) | Target | Result | |", "| --- | ---: | ---: | --- |"]
        for key, m in c["measures"].items():
            out.append(f"| {labels[key]} | {_pct(m['target'])} | {_pct(m['value'])} | {'met' if m['met'] else 'missed'} |")
        lit = c["literal_precision_full_list"]
        out.append(f"| Precision of the full list (literal reading) | {_pct(lit['target'])} | {_pct(lit['value'])} | {'met' if lit['met'] else 'missed'} |")
        out += ["", f"Detail: [{r['slug']}.md]({r['slug']}.md)", ""]
    out += ["", "## What each pass added (newer half)", "",
            "| Corpus | Pass | Right page in top 3 | Reciprocal rank | Gain | Kept |", "| --- | --- | ---: | ---: | --- | --- |"]
    for name, r in found.items():
        p = r["passes"]
        rows = [("1 words", p["pass1_words"]["figures"], None), ("2 hybrid", p["pass2_hybrid"]["figures"], p["pass2_hybrid"]["gain"]),
                ("3 reading", p["pass3_reading"]["figures"], p["pass3_reading"]["gain"])]
        for label, fig, gain in rows:
            g = "" if gain is None else f"{_pct(gain['hit_at_3_gain'])} / {gain['mrr_gain']}"
            k = "" if gain is None else ("yes" if gain["kept"] else "no")
            mrr = "n/a" if fig["mrr"] is None else f"{fig['mrr']:.2f}"
            out.append(f"| {name} | {label} | {_pct(fig['top_3_hit'])} | {mrr} | {g} | {k} |")
    if summary["pass_scope"]:
        out += ["", "Scope of each pass, by the registered rule (kept on at least 3 corpora, fewer, or none): "
                + "; ".join(f"{k.replace('_', ' ')}: **{v}**" for k, v in summary["pass_scope"].items()) + "."]
    out += ["", "## Limits", "",
            "- The replay scores commit messages against the pages they edited. It is a floor for the first passes and a proxy for real change events.",
            "- The Hub and OpenBB newer halves were seen in earlier reports; the Prometheus and service manual halves were not.",
            "- The GOV.UK corpus is archived (2016) and many of its commit messages name the file they edit.",
            "- One reader model, on one date. Precision of the likely list is the registered reading; the literal full-list figure is shown beside it.", ""]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m docloop.r1")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("--corpus", required=True); p.add_argument("--workdir", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("summarize"); p.add_argument("--in", dest="in_dir", required=True); p.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "summarize":
        print(json.dumps(summarize(args.in_dir, args.out)["verdict"]["passed"]))
        return 0
    cfg = load_config()
    corpus = next((c for c in cfg["corpora"] if c["slug"] == args.corpus), None)
    if corpus is None:
        print(f"docloop.r1: unknown corpus {args.corpus!r}. Choose from {[c['slug'] for c in cfg['corpora']]}", file=sys.stderr)
        return 1
    if not (os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY")):
        print("docloop.r1: set HF_TOKEN (or OPENAI_API_KEY): the reader is a model.", file=sys.stderr)
        return 1
    from .embeddings import default_searcher
    from .judge import Judge, make_chat_model
    cache = Path(args.workdir) / "cache"
    searcher, label = default_searcher(cfg["embedder"], cache / "embeddings")
    judge = Judge(make_chat_model(cfg["model"]), cache / f"judge-{corpus['slug']}.json")
    repo = prepare(corpus, args.workdir)
    report = run(corpus, repo, args.out, searcher, label, judge, lambda n, s: print(f"  [{n}] {s[:60]}", file=sys.stderr))
    print(json.dumps({"corpus": corpus["name"], "events": report["summary"]["overall"]["events"], "check": report["check"]["status"],
                      "all_met": report["check"]["all_met"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
