"""Command line: the same tools the agents call, plus the human gate.

    docloop classify examples/events/retire-csv.json
    docloop status retire-csv
    docloop approve retire-csv --reviewer "A. Writer"
    docloop apply retire-csv
"""
from __future__ import annotations

import argparse
import json
import sys

from .workspace import Workspace


def _provider_hint(exc: Exception) -> str:
    """Turn a provider's HTTP error into one line a person can act on."""
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    hints = {
        401: "401 Unauthorized: the token is missing, mistyped or revoked. Check HF_TOKEN or OPENAI_API_KEY.",
        402: "402 Payment Required: the token works, but the account has no inference credits. "
             "Add credits with the provider, or use a free local option: --embedder local:all-MiniLM-L6-v2, "
             "and --base-url pointing at a local model server for --judge-model.",
        403: "403 Forbidden: the token lacks permission to call inference. Create one that allows it.",
        404: "404 Not Found: the provider does not serve this model id. Try another model.",
        429: "429 Too Many Requests: rate limited. Wait a little and run the same command again.",
    }
    first_line = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return hints.get(status, f"{type(exc).__name__}: {first_line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="docloop", description=__doc__.splitlines()[0])
    parser.add_argument("--docs", help="docs folder or CMS export (.json). Default: $DOCLOOP_DOCS or ./docs")
    parser.add_argument("--home", help="state folder. Default: $DOCLOOP_HOME or ./.docloop")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("classify", "route", "impact"):
        sub.add_parser(name).add_argument("event_file")
    sub.add_parser("search").add_argument("query")
    sub.add_parser("read").add_argument("page_id")
    sub.add_parser("status").add_argument("event_id")
    sub.add_parser("census").add_argument("index_file")
    p = sub.add_parser("approve", help="human gate: approve everything proposed for an event")
    p.add_argument("event_id"); p.add_argument("--reviewer", required=True); p.add_argument("--note", default="")
    p = sub.add_parser("reject", help="human gate: reject and return to the writer")
    p.add_argument("event_id"); p.add_argument("--reviewer", required=True); p.add_argument("--note", default="")
    sub.add_parser("apply", help="human gate: write approved proposals to the docs").add_argument("event_id")
    sub.add_parser("registry", help="list every page with its hash, tied to the corpus commit")
    p = sub.add_parser("replay", help="score page mapping against past commits of a docs repository")
    p.add_argument("--repo", required=True); p.add_argument("--roots", nargs="+", required=True)
    p.add_argument("--exclude", nargs="*", default=[]); p.add_argument("--limit", type=int, default=200)
    p.add_argument("--max-pages", type=int, default=10); p.add_argument("--report", help="also write a Markdown report here")
    p.add_argument("--search", choices=["lexical", "vector", "hybrid"], default="lexical")
    p.add_argument("--embedder", help="for vector or hybrid: hf:<model>, openai:<model> or local:<model>")
    p.add_argument("--judge-model", help="add the reading step: a model keeps or drops each candidate")
    p.add_argument("--base-url", help="OpenAI-compatible endpoint for the judge model")
    p.add_argument("--judge-max", type=int, help="judge only the newest N events, to limit cost")
    p.add_argument("--out", help="write the full JSON result here")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # never crash on a console that cannot show a character
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    if args.cmd == "replay":
        from pathlib import Path
        from .replay import replay, to_markdown
        import os
        home = Path(args.home or os.environ.get("DOCLOOP_HOME", ".docloop"))
        try:
            from .embeddings import make_searcher
            searcher = make_searcher(args.search, args.embedder, home / "embeddings")
            judge = None
            if args.judge_model:
                from .judge import Judge, make_chat_model
                judge = Judge(make_chat_model(args.judge_model, args.base_url), home / "judge-cache.json")
        except ImportError as exc:
            print(f"docloop: {exc}. Install the extras first: pip install -e \".[agent,vector]\"", file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"docloop: {exc}", file=sys.stderr)
            return 1
        note = (lambda n, subject: print(f"  [{n}] {subject[:70]}", file=sys.stderr)) if (judge or searcher) else None
        try:
            report = replay(args.repo, args.roots, args.limit, args.max_pages, exclude=args.exclude,
                            searcher=searcher, judge=judge, judge_max=args.judge_max, progress=note)
        except Exception as exc:  # a provider error should read as one, not as a crash
            if not (searcher or judge):
                raise
            print(f"docloop: the model provider refused the request.\n  {_provider_hint(exc)}\n"
                  "  Work already done is cached under .docloop, so a rerun resumes where this stopped.", file=sys.stderr)
            return 1
        report["search"] = args.search if args.search == "lexical" else f"{args.search} ({args.embedder})"
        if args.report:
            Path(args.report).write_text(to_markdown(report), encoding="utf-8")
        if args.out:
            Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        shown = {"search": report["search"], "overall": report["summary"]["overall"],
                 "by_period": report["summary"]["by_period"]}
        if "reading_step" in report:
            shown["reading_step"] = report["reading_step"]
        print(json.dumps(shown, indent=2))
        return 0
    try:
        ws = Workspace(args.docs, args.home)
        result = {
            "classify": lambda: ws.classify_event(args.event_file),
            "route": lambda: ws.route_event(args.event_file),
            "impact": lambda: ws.find_affected_pages(args.event_file),
            "search": lambda: ws.search_pages(args.query),
            "read": lambda: ws.read_page(args.page_id),
            "status": lambda: ws.review_status(args.event_id),
            "census": lambda: ws.corpus_census(args.index_file),
            "approve": lambda: ws.approve(args.event_id, args.reviewer, "approved", args.note),
            "reject": lambda: ws.approve(args.event_id, args.reviewer, "rejected", args.note),
            "apply": lambda: ws.apply(args.event_id),
            "registry": lambda: ws.store.registry(),
        }[args.cmd]()
    except (KeyError, ValueError, PermissionError, FileNotFoundError) as exc:
        print(f"docloop: {exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
