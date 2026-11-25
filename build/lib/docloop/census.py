"""Corpus census: reconcile what the docs system holds with what a search index serves.

The index listing is a JSON file: {"entries": [{"id", "visibility"}]}.
"""
from __future__ import annotations

import json
from pathlib import Path

from .stores import PageStore


def census(store: PageStore, index_file: str | Path) -> dict:
    entries = json.loads(Path(index_file).read_text(encoding="utf-8"))["entries"]
    indexed = {str(e["id"]): e.get("visibility", "public") for e in entries}
    pages = {p.id: p for p in store.pages()}
    public = {pid for pid, p in pages.items() if p.visibility == "public"}

    blind_spots = sorted(pid for pid in public if pid not in indexed)
    ghosts = sorted(pid for pid in indexed if pid not in pages)
    suppressed = sorted(pid for pid in public if indexed.get(pid) == "internal")
    leaked = sorted(pid for pid, p in pages.items() if p.visibility == "internal" and indexed.get(pid) == "public")
    healthy = sorted(pid for pid in public if indexed.get(pid) == "public")
    return {
        "pages_in_store": len(pages), "public_pages": len(public), "index_entries": len(indexed),
        "retrievable_share": round(len(healthy) / len(public), 3) if public else None,
        "findings": {
            "blind_spots": {"meaning": "public pages absent from the index", "pages": blind_spots},
            "ghosts": {"meaning": "deleted pages the index still serves", "pages": ghosts},
            "wrongly_suppressed": {"meaning": "public pages indexed as internal", "pages": suppressed},
            "leaked_internal": {"meaning": "internal pages indexed as public", "pages": leaked},
        },
    }
