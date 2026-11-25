"""The workspace: every tool an agent may call, and the two only a person may call.

Agent tools read, classify, search and PROPOSE. They never write to the docs.
`approve` and `apply` are the human gate: writes are single-threaded and happen
only after a recorded approval, and only if the page has not changed since the
proposal was made.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from . import rules
from .census import census as run_census
from .detectors import classify
from .impact import find_pages, search
from .models import ChangeEvent
from .routing import route
from .stores import PageStore, open_store


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "__" for c in name)


class Workspace:
    #: Tools an agent runtime may expose to a model.
    AGENT_TOOLS = ("classify_event", "route_event", "find_affected_pages", "search_pages", "read_page",
                   "propose_edit", "propose_notice", "review_status", "corpus_census")
    #: Tools reserved for a person. Never register these with a model.
    HUMAN_TOOLS = ("approve", "apply")

    def __init__(self, docs: str | Path | PageStore | None = None, home: str | Path | None = None):
        docs = docs or os.environ.get("DOCLOOP_DOCS", "docs")
        self.store = docs if isinstance(docs, PageStore) else open_store(docs)
        self.home = Path(home or os.environ.get("DOCLOOP_HOME", ".docloop"))
        self.home.mkdir(parents=True, exist_ok=True)

    # ---- helpers -------------------------------------------------------
    def _event(self, event_file: str) -> ChangeEvent:
        return ChangeEvent.from_dict(json.loads(Path(event_file).read_text(encoding="utf-8")))

    def _dir(self, kind: str, event_id: str) -> Path:
        path = self.home / kind / _safe(event_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _audit(self, event_id: str, action: str, **detail) -> None:
        with (self.home / "audit.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"at": _now(), "event": event_id, "action": action, **detail}, ensure_ascii=False) + "\n")

    def _save_state(self, event_id: str, key: str, value: dict) -> None:
        (self._dir("events", event_id) / f"{key}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_state(self, event_id: str, key: str) -> dict | None:
        path = self.home / "events" / _safe(event_id) / f"{key}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

    # ---- agent tools ---------------------------------------------------
    def classify_event(self, event_file: str) -> dict:
        """Classify a change event with rule-based detectors. Returns type, flags, confidence and the evidence."""
        event = self._event(event_file)
        result = classify(event).to_dict()
        self._save_state(event.id, "classification", result)
        self._audit(event.id, "classified", change_type=result["change_type"], confidence=result["confidence"])
        return result

    def route_event(self, event_file: str) -> dict:
        """Decide which steps run for this event, from a fixed table. Returns mode, steps and the reason."""
        event = self._event(event_file)
        result = route(classify(event)).to_dict()
        self._save_state(event.id, "route", result)
        self._audit(event.id, "routed", mode=result["mode"])
        return result

    def find_affected_pages(self, event_file: str) -> dict:
        """List pages the change touches. Pages named in the event win; otherwise a capped search. Ids are always real."""
        event = self._event(event_file)
        candidates = [c.to_dict() for c in find_pages(event, self.store)]
        result = {"event_id": event.id, "candidates": candidates,
                  "note": "explicit references returned as given" if any(c["basis"] == "explicit reference" for c in candidates)
                  else "search results: confirm relevance before proposing edits"}
        self._save_state(event.id, "impact", result)
        self._audit(event.id, "impact_mapped", pages=[c["page_id"] for c in candidates])
        return result

    def search_pages(self, query: str) -> dict:
        """Search the documentation. Returns at most 8 page ids with titles and scores."""
        return {"query": query, "results": [c.to_dict() for c in search(query, self.store)]}

    def read_page(self, page_id: str) -> dict:
        """Read one page by id. Fails if the id does not exist."""
        page = self.store.get(page_id)
        return {"page_id": page.id, "title": page.title, "visibility": page.visibility, "body": page.body}

    def propose_edit(self, event_id: str, page_id: str, new_body: str, rationale: str) -> dict:
        """Propose a full replacement body for one existing page. Nothing is written to the docs."""
        if not self.store.exists(page_id):
            raise KeyError(f"No such page: {page_id}. Use find_affected_pages or search_pages to get real ids.")
        old = self.store.get(page_id).body
        if old == new_body:
            raise ValueError("The proposed body is identical to the current page.")
        diff = "".join(difflib.unified_diff(old.splitlines(True), new_body.splitlines(True),
                                            fromfile=f"{page_id} (current)", tofile=f"{page_id} (proposed)"))
        proposal = {"event_id": event_id, "page_id": page_id, "base_hash": _hash(old), "new_body": new_body,
                    "rationale": rationale, "diff": diff, "lint": rules.lint_page(new_body), "created_at": _now()}
        (self._dir("proposals", event_id) / f"{_safe(page_id)}.json").write_text(
            json.dumps(proposal, indent=2, ensure_ascii=False), encoding="utf-8")
        self._audit(event_id, "edit_proposed", page=page_id, lint_issues=len(proposal["lint"]))
        return {"page_id": page_id, "diff": diff, "lint": proposal["lint"], "status": "awaiting human approval"}

    def propose_notice(self, event_id: str, subject: str, body: str) -> dict:
        """Save a customer notice draft for review. Nothing is sent."""
        classification = self._load_state(event_id, "classification") or {}
        lint = rules.lint_notice(subject, body, classification.get("change_type", "change"))
        draft = {"event_id": event_id, "subject": subject, "body": body, "lint": lint, "created_at": _now()}
        (self._dir("notices", event_id) / "notice.json").write_text(json.dumps(draft, indent=2, ensure_ascii=False), encoding="utf-8")
        self._audit(event_id, "notice_drafted", lint_issues=len(lint))
        return {"subject": subject, "lint": lint, "status": "draft for human review, not sent"}

    def review_status(self, event_id: str) -> dict:
        """Report where an event stands: route, proposals, approval, and a readiness score with its breakdown."""
        route_state = self._load_state(event_id, "route")
        proposals = self._proposals(event_id)
        notice_file = self.home / "notices" / _safe(event_id) / "notice.json"
        approval = self._load_state(event_id, "approval")
        mode = (route_state or {}).get("mode")
        needs_docs = mode in ("both", "docs_only")
        needs_notice = mode in ("both", "notice_only")
        critical = sum(1 for p in proposals for i in p["lint"] if i["severity"] == "critical")
        breakdown = {
            "routed": bool(route_state) and mode != "human_triage",
            "docs_proposed": (not needs_docs) or bool(proposals),
            "notice_drafted": (not needs_notice) or notice_file.is_file(),
            "no_critical_lint": critical == 0,
            "approved": bool(approval) and approval["decision"] == "approved",
        }
        score = round(sum(breakdown.values()) / len(breakdown), 2)
        if approval and approval["decision"] == "rejected" or mode == "human_triage":
            state = "BLOCKED"
        elif score == 1.0:
            state = "READY"
        elif all(v for k, v in breakdown.items() if k != "approved"):
            state = "AWAITING_APPROVAL"
        else:
            state = "AT_RISK"
        return {"event_id": event_id, "mode": mode, "proposals": [p["page_id"] for p in proposals],
                "notice_drafted": notice_file.is_file(), "approval": approval,
                "readiness": {"score": score, "state": state, "breakdown": breakdown}}

    def corpus_census(self, index_file: str) -> dict:
        """Reconcile the docs store with a search index listing. Returns blind spots, ghosts and visibility mismatches."""
        return run_census(self.store, index_file)

    # ---- human gate ----------------------------------------------------
    def _proposals(self, event_id: str) -> list[dict]:
        folder = self.home / "proposals" / _safe(event_id)
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []

    def approve(self, event_id: str, reviewer: str, decision: str, note: str = "") -> dict:
        """HUMAN ONLY. Record an approval or rejection for everything proposed under an event."""
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be 'approved' or 'rejected'")
        if not reviewer.strip():
            raise ValueError("a reviewer name is required")
        record = {"decision": decision, "reviewer": reviewer, "note": note, "at": _now(),
                  "covers": {p["page_id"]: p["base_hash"] for p in self._proposals(event_id)}}
        self._save_state(event_id, "approval", record)
        self._audit(event_id, decision, reviewer=reviewer)
        return record

    def apply(self, event_id: str) -> dict:
        """HUMAN ONLY. Write approved proposals to the docs, one page at a time, refusing stale ones."""
        approval = self._load_state(event_id, "approval")
        if not approval or approval["decision"] != "approved":
            raise PermissionError(f"Event {event_id} has no approval on record. Nothing was written.")
        written, refused = [], []
        for proposal in self._proposals(event_id):
            page_id = proposal["page_id"]
            if approval["covers"].get(page_id) != proposal["base_hash"]:
                refused.append({"page_id": page_id, "why": "proposal changed after approval"})
            elif _hash(self.store.get(page_id).body) != proposal["base_hash"]:
                refused.append({"page_id": page_id, "why": "page changed since the proposal was made"})
            else:
                self.store.write(page_id, proposal["new_body"])
                written.append(page_id)
        self._audit(event_id, "applied", written=written, refused=[r["page_id"] for r in refused])
        return {"written": written, "refused": refused}
