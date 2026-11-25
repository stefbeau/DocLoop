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
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # never crash on a console that cannot show a character
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    if args.cmd == "replay":
        from pathlib import Path
        from .replay import replay, to_markdown
        report = replay(args.repo, args.roots, args.limit, args.max_pages, exclude=args.exclude)
        if args.report:
            Path(args.report).write_text(to_markdown(report), encoding="utf-8")
        print(json.dumps({k: report[k] for k in ("head", "roots", "summary", "skipped")}, indent=2))
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
