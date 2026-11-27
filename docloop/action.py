"""GitHub Action entry point: comment on a pull request with the docs pages it may affect.

It reads the pull request, maps it to documentation pages with the same deterministic
tools the agents use, and posts ONE comment (updated in place on each push).
It writes nothing to the docs, and it never fails a build over a comment it cannot post.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from .impact import find_pages
from .models import ChangeEvent
from .stores import open_store

MARKER = "<!-- docloop:impact -->"
MAX_FILES_LISTED = 40
METHOD_URL = "https://stefbeau.github.io/DocLoop/"


def event_from_pull_request(payload: dict, changed_files: list[str]) -> ChangeEvent:
    pr = payload["pull_request"]
    files = changed_files[:MAX_FILES_LISTED]
    body = (pr.get("body") or "").strip()
    if files:
        body += "\n\nFiles changed: " + ", ".join(files)
    return ChangeEvent(id=f"pr-{pr['number']}", title=pr.get("title", ""), body=body,
                       labels=[l["name"] for l in pr.get("labels", [])], source="pull_request")


def touches_only_docs(changed_files: list[str], docs_dir: str) -> bool:
    prefix = docs_dir.removeprefix("./").rstrip("/") + "/"
    return bool(changed_files) and all(f.startswith(prefix) for f in changed_files)


def render_comment(candidates: list[dict], search_mode: str, docs_dir: str) -> str:
    lines = [MARKER, "### DocLoop: documentation that may need an update", ""]
    if not candidates:
        lines += ["No page in the docs looks affected by this change. If it changes behaviour a user can see, "
                  "check the docs yourself: a search over words can miss a page.", ""]
    else:
        lines += ["| Page | Why it is listed |", "| --- | --- |"]
        for c in candidates:
            why = "named in the pull request" if c["basis"] == "explicit reference" else "similar wording"
            lines.append(f"| `{c['page_id']}` | {why} |")
        lines.append("")
        lines.append("These are leads to read, not verdicts. The list is capped at 8 and some listed pages "
                     "will not need a change.")
        lines.append("")
    lines.append(f"<sub>Search: {search_mode}. Nothing was written to your docs. "
                 f"How accurate this is, measured on public repositories: {METHOD_URL}</sub>")
    return "\n".join(lines)


class GitHubApi:
    def __init__(self, token: str, base: str = "https://api.github.com"):
        self.token, self.base = token, base

    def call(self, method: str, path: str, data: dict | None = None):
        req = urllib.request.Request(
            self.base + path, method=method,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json", "User-Agent": "docloop-action"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
        return json.loads(raw) if raw else None


def changed_files(api, repo: str, number: int) -> list[str]:
    names, page = [], 1
    while page <= 3:  # 300 files is enough to judge a change
        batch = api.call("GET", f"/repos/{repo}/pulls/{number}/files?per_page=100&page={page}") or []
        names += [f["filename"] for f in batch]
        if len(batch) < 100:
            break
        page += 1
    return names


def upsert_comment(api, repo: str, number: int, body: str) -> str:
    """Update the DocLoop comment if there is one, else create it. Returns 'updated' or 'created'."""
    for c in api.call("GET", f"/repos/{repo}/issues/{number}/comments?per_page=100") or []:
        if MARKER in (c.get("body") or ""):
            api.call("PATCH", f"/repos/{repo}/issues/comments/{c['id']}", {"body": body})
            return "updated"
    api.call("POST", f"/repos/{repo}/issues/{number}/comments", {"body": body})
    return "created"


def run(payload: dict, docs_dir: str, repo: str, api, search: str = "lexical",
        summary_path: str | None = None, skip_docs_only: bool = True,
        log: Callable[[str], None] = print) -> int:
    if "pull_request" not in payload:
        log("docloop: this action runs on pull_request events. Nothing to do.")
        return 0
    number = payload["pull_request"]["number"]
    try:
        files = changed_files(api, repo, number) if api else []
    except (urllib.error.URLError, OSError) as exc:
        log(f"docloop: could not list changed files ({exc}); using the title and description only.")
        files = []
    if skip_docs_only and touches_only_docs(files, docs_dir):
        log("docloop: this pull request only changes the docs. No comment.")
        return 0
    store = open_store(docs_dir, None, [])
    searcher, mode = None, "words"
    if search == "hybrid":
        try:
            from .embeddings import default_searcher
            searcher, mode = default_searcher(None, Path(".docloop") / "embeddings")
        except Exception as exc:  # a missing key or package must not fail the build
            log(f"docloop: hybrid search unavailable ({exc}); using words.")
    candidates = [c.to_dict() for c in find_pages(event_from_pull_request(payload, files), store, searcher)]
    body = render_comment(candidates, mode, docs_dir)
    try:
        if api is None:
            raise OSError("no GITHUB_TOKEN")
        log(f"docloop: comment {upsert_comment(api, repo, number, body)} ({len(candidates)} pages).")
    except (urllib.error.URLError, OSError) as exc:  # fork pull requests get a read-only token
        log(f"docloop: could not post the comment ({exc}); writing the job summary instead.")
        print(body)
        if summary_path:
            with open(summary_path, "a", encoding="utf-8") as fh:
                fh.write(body + "\n")
    return 0


def main() -> int:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("docloop: run this inside GitHub Actions (GITHUB_EVENT_PATH is not set).", file=sys.stderr)
        return 1
    payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    token = os.environ.get("GITHUB_TOKEN", "")
    api = GitHubApi(token) if token else None
    return run(payload, os.environ.get("INPUT_DOCS", "docs"), os.environ.get("GITHUB_REPOSITORY", ""), api,
               search=os.environ.get("INPUT_SEARCH", "lexical"), summary_path=os.environ.get("GITHUB_STEP_SUMMARY"),
               skip_docs_only=os.environ.get("INPUT_SKIP_DOCS_ONLY", "true") == "true")


if __name__ == "__main__":
    raise SystemExit(main())
