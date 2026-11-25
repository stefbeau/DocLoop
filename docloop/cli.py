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
    args = parser.parse_args(argv)

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
        }[args.cmd]()
    except (KeyError, ValueError, PermissionError, FileNotFoundError) as exc:
        print(f"docloop: {exc.args[0] if exc.args else exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
