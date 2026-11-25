"""Historical replay: score page mapping against what people really edited.

For every past commit that changed documentation, take the commit message as
the change event, rebuild the docs as they were just before, ask
`find_pages` which pages the change affects, and compare with the pages the
commit actually modified.

    docloop replay --repo path/to/docs-repo --roots content --limit 200

Nothing here calls a model. This measures the deterministic first pass an
agent starts from, so it is a floor, not the system's final accuracy.
"""
from __future__ import annotations

import io
import re
import subprocess
import tarfile
import tempfile
from collections import defaultdict
from pathlib import Path

from .impact import MAX_CANDIDATES, find_pages
from .models import ChangeEvent
from .stores import DOC_SUFFIXES, GitMarkdownStore

_WORD = re.compile(r"[A-Za-z]{3,}")


def _git(repo: Path, *args: str, binary: bool = False):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return out.stdout if binary else out.stdout.decode("utf-8", errors="replace")


def _page_id(path: str) -> str | None:
    p = Path(path)
    return p.with_suffix("").as_posix() if p.suffix in DOC_SUFFIXES else None


def list_changes(repo: Path, roots: list[str], limit: int) -> list[dict]:
    """Past commits that touched docs, newest first, with the pages each one modified."""
    log = _git(repo, "log", "--no-merges", f"-n{limit}", "--format=%H%x1f%P%x1f%ad%x1f%s%x1f%b%x1e",
               "--date=short", "--", *roots)
    changes = []
    for record in log.split("\x1e"):
        if not record.strip():
            continue
        sha, parents, date, subject, body = (record.strip("\n").split("\x1f") + ["", ""])[:5]
        if not parents:
            continue  # the first commit has nothing to compare with
        status = _git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", "-M", sha, "--", *roots)
        modified, added, removed = [], [], []
        for line in status.splitlines():
            parts = line.split("\t")
            code = parts[0][0]
            page = _page_id(parts[1])
            if not page:
                continue
            if code in "MR":
                modified.append(page)   # for a rename, the page as it was named before
            elif code == "A":
                added.append(page)
            elif code == "D":
                removed.append(page)
        changes.append({"sha": sha, "parent": parents.split()[0], "date": date, "subject": subject.strip(),
                        "body": body.strip(), "modified": sorted(set(modified)), "added": sorted(set(added)),
                        "removed": sorted(set(removed))})
    return changes


def _checkout(repo: Path, revision: str, roots: list[str], into: Path) -> None:
    present = [r for r in roots if _git(repo, "ls-tree", "-d", "--name-only", revision, "--", r).strip()]
    if not present:
        return
    data = _git(repo, "archive", "--format=tar", revision, "--", *present, binary=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(into, filter="data")


def _strip_noise(subject: str, body: str) -> tuple[str, str]:
    subject = re.sub(r"\s*\(#\d+\)\s*$", "", subject)
    lines = [ln for ln in body.splitlines() if not re.match(r"\s*(co-authored-by|signed-off-by):", ln, re.I)]
    return subject, "\n".join(lines).strip()


def replay(repo: str | Path, roots: list[str], limit: int = 200, max_pages: int = 10, min_words: int = 3,
           exclude: list[str] | None = None, searcher=None, judge=None, judge_max: int | None = None,
           progress=None) -> dict:
    """`searcher` swaps the search method. `judge` adds the reading step: a model keeps or drops each candidate."""
    repo = Path(repo)
    results, skipped = [], defaultdict(int)
    judged = 0
    for change in list_changes(repo, roots, limit):
        subject, body = _strip_noise(change["subject"], change["body"])
        truth = change["modified"]
        if not truth:
            skipped["no existing page modified (new pages, assets or config only)"] += 1
            continue
        if len(truth) > max_pages:
            skipped[f"more than {max_pages} pages modified (bulk edit, not one change)"] += 1
            continue
        words = len(_WORD.findall(subject + " " + body))
        if words < min_words:
            skipped[f"message shorter than {min_words} words"] += 1
            continue
        with tempfile.TemporaryDirectory() as tmp:
            _checkout(repo, change["parent"], roots, Path(tmp))
            available = [r for r in roots if (Path(tmp) / r).is_dir()]
            if not available:
                skipped["docs folders did not exist yet"] += 1
                continue
            store = GitMarkdownStore(tmp, available, exclude or ())
            truth = [t for t in truth if store.exists(t)]
            if not truth:
                skipped["modified pages are outside the scanned folders"] += 1
                continue
            event = ChangeEvent(id=change["sha"][:8], title=subject, body=body, source="commit")
            found = find_pages(event, store, searcher)
            kept = None
            if judge and found and (judge_max is None or judged < judge_max):
                kept = [c.page_id for c in found if judge.keep(event, store.get(c.page_id))["keep"]]
                judged += 1
        if progress:
            progress(len(results) + 1, subject)
        predicted = [c.page_id for c in found]
        hits = [p for p in predicted if p in truth]
        rank = next((i + 1 for i, p in enumerate(predicted) if p in truth), None)
        results.append({
            "sha": change["sha"][:8], "date": change["date"], "subject": subject, "message_words": words,
            "truth": truth, "predicted": predicted,
            "basis": found[0].basis if found else "nothing returned",
            "recall": round(len(hits) / len(truth), 3),
            "precision": round(len(hits) / len(predicted), 3) if predicted else None,
            "reciprocal_rank": round(1 / rank, 3) if rank else 0.0,
            "hit": bool(hits), "new_pages": len(change["added"])})
        if kept is not None:
            kept_hits = [p for p in kept if p in truth]
            results[-1]["after_reading"] = {
                "kept": kept, "recall": round(len(kept_hits) / len(truth), 3),
                "precision": round(len(kept_hits) / len(kept), 3) if kept else None, "hit": bool(kept_hits)}
    report = {"repo": str(repo), "head": _git(repo, "rev-parse", "HEAD").strip(), "roots": roots,
              "candidate_cap": MAX_CANDIDATES, "summary": summarise(results), "skipped": dict(skipped),
              "events": results}
    if judge:
        report["reading_step"] = summarise_reading(results, judge)
    return report


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 3) if values else None


def _block(rows: list[dict]) -> dict:
    answered = [r for r in rows if r["predicted"]]
    return {"events": len(rows),
            "hit_rate": _mean([float(r["hit"]) for r in rows]),
            "mean_recall": _mean([r["recall"] for r in rows]),
            "mean_reciprocal_rank": _mean([r["reciprocal_rank"] for r in rows]),
            "answered": len(answered),
            "precision_when_answered": _mean([r["precision"] for r in answered])}


def _periods(results: list[dict]) -> dict[str, list[dict]]:
    """Older and newer half by date: tune on the older one, report on the newer one."""
    ordered = sorted(results, key=lambda r: r["date"])
    half = len(ordered) // 2
    return {"older half": ordered[:half], "newer half": ordered[half:]} if len(ordered) >= 2 else {}


def _reading_block(rows: list[dict]) -> dict:
    before = _block(rows)
    answered = [r for r in rows if r["after_reading"]["kept"]]
    return {"events": len(rows),
            "before": {k: before[k] for k in ("hit_rate", "mean_recall", "precision_when_answered")},
            "after": {"hit_rate": _mean([float(r["after_reading"]["hit"]) for r in rows]),
                      "mean_recall": _mean([r["after_reading"]["recall"] for r in rows]),
                      "precision_when_answered": _mean([r["after_reading"]["precision"] for r in answered]),
                      "events_with_nothing_kept": len(rows) - len(answered)},
            "mean_candidates_before": _mean([float(len(r["predicted"])) for r in rows]),
            "mean_candidates_after": _mean([float(len(r["after_reading"]["kept"])) for r in rows])}


def summarise_reading(results: list[dict], judge) -> dict:
    rows = [r for r in results if "after_reading" in r]
    out = {"model": judge.name, "model_calls": judge.calls, "unparsed_replies": judge.unparsed,
           "overall": _reading_block(rows) if rows else None}
    out["by_period"] = {name: _reading_block(part) for name, part in _periods(rows).items() if part}
    return out


def summarise(results: list[dict]) -> dict:
    by_basis, by_size, by_length = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in results:
        by_basis[r["basis"]].append(r)
        n = len(r["truth"])
        by_size["1 page" if n == 1 else "2-3 pages" if n <= 3 else "4+ pages"].append(r)
        w = r["message_words"]
        by_length["under 8 words" if w < 8 else "8-30 words" if w <= 30 else "over 30 words"].append(r)
    return {"overall": _block(results),
            "by_period": {k: _block(v) for k, v in _periods(results).items()},
            "by_basis": {k: _block(v) for k, v in sorted(by_basis.items())},
            "by_pages_modified": {k: _block(v) for k, v in sorted(by_size.items())},
            "by_message_length": {k: _block(v) for k, v in by_length.items()}}


def to_markdown(report: dict, title: str = "Replay report") -> str:
    def pct(x):
        return "n/a" if x is None else f"{x * 100:.0f}%"

    def table(blocks: dict) -> list[str]:
        rows = ["| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for name, b in blocks.items():
            mrr = "n/a" if b["mean_reciprocal_rank"] is None else f'{b["mean_reciprocal_rank"]:.2f}'
            rows.append(f'| {name} | {b["events"]} | {pct(b["hit_rate"])} | {pct(b["mean_recall"])} | {mrr} | '
                        f'{b["answered"]} | {pct(b["precision_when_answered"])} |')
        return rows

    s = report["summary"]
    out = [f"# {title}", "",
           f"Corpus at `{report['head'][:8]}`, folders: {', '.join(report['roots'])}. "
           f"At most {report['candidate_cap']} candidates per event.", "",
           "## Overall", "", *table({"All scored events": s["overall"]}), "",
           "## By period (tune on the older half, report on the newer half)", "", *table(s.get("by_period", {})), "",
           "## By how the pages were found", "", *table(s["by_basis"]), "",
           "## By number of pages the commit modified", "", *table(s["by_pages_modified"]), "",
           "## By length of the commit message", "", *table(s["by_message_length"]), "",
           "## Commits left out", ""]
    out += [f"- {n} × {why}" for why, n in report["skipped"].items()] or ["- none"]
    reading = report.get("reading_step")
    if reading and reading.get("overall"):
        out += ["", f"## Reading step ({reading['model']})", "",
                f"{reading['model_calls']} model calls, {reading['unparsed_replies']} unparsed replies (kept by default).", "",
                "| Group | Events | Hit rate before | after | Recall before | after | Precision before | after | Candidates before | after |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for name, b in {"All judged events": reading["overall"], **reading["by_period"]}.items():
            out.append(f'| {name} | {b["events"]} | {pct(b["before"]["hit_rate"])} | {pct(b["after"]["hit_rate"])} | '
                       f'{pct(b["before"]["mean_recall"])} | {pct(b["after"]["mean_recall"])} | '
                       f'{pct(b["before"]["precision_when_answered"])} | {pct(b["after"]["precision_when_answered"])} | '
                       f'{b["mean_candidates_before"]} | {b["mean_candidates_after"]} |')
    out += ["", "## Every scored event", "",
            "| Date | Commit | Message | Truth | Found | Recall |", "| --- | --- | --- | ---: | ---: | ---: |"]
    for r in report["events"]:
        msg = r["subject"].replace("|", "/")[:70]
        out.append(f'| {r["date"]} | `{r["sha"]}` | {msg} | {len(r["truth"])} | {len(r["predicted"])} | {pct(r["recall"])} |')
    return "\n".join(out) + "\n"
