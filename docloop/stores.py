"""Page stores: one interface, several places documentation can live.

Every tool talks to a PageStore, never to files or an API directly. To support
a new documentation system, subclass PageStore and implement four methods.
"""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

from .models import Page


class PageStore(ABC):
    @abstractmethod
    def list_ids(self) -> list[str]: ...

    @abstractmethod
    def get(self, page_id: str) -> Page: ...

    @abstractmethod
    def write(self, page_id: str, body: str) -> None: ...

    def exists(self, page_id: str) -> bool:
        return page_id in set(self.list_ids())

    def pages(self) -> list[Page]:
        return [self.get(i) for i in self.list_ids()]


_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


class GitMarkdownStore(PageStore):
    """Docs-as-code: every .md file under a folder is a page.

    The page id is the path relative to the root, without the extension.
    Front matter may set `title:` and `visibility:`.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        if not self.root.is_dir():
            raise FileNotFoundError(f"Docs folder not found: {self.root}")

    def _path(self, page_id: str) -> Path:
        path = (self.root / f"{page_id}.md").resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError(f"Page id escapes the docs folder: {page_id}")
        return path

    def list_ids(self) -> list[str]:
        return sorted(p.relative_to(self.root).with_suffix("").as_posix() for p in self.root.rglob("*.md"))

    def get(self, page_id: str) -> Page:
        path = self._path(page_id)
        if not path.is_file():
            raise KeyError(f"No such page: {page_id}")
        text = path.read_text(encoding="utf-8")
        meta: dict[str, str] = {}
        match = _FRONT_MATTER.match(text)
        if match:
            for line in match.group(1).splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip().strip("\"'")
        title = meta.get("title")
        if not title:
            heading = re.search(r"^#\s+(.+)$", text, re.M)
            title = heading.group(1).strip() if heading else page_id
        return Page(id=page_id, title=title, body=text, visibility=meta.get("visibility", "public"), location=str(path))

    def write(self, page_id: str, body: str) -> None:
        path = self._path(page_id)
        if not path.is_file():
            raise KeyError(f"No such page: {page_id}")
        path.write_text(body, encoding="utf-8")


class JsonCmsStore(PageStore):
    """A content system represented as one JSON export.

    Shape: {"pages": [{"id", "title", "body", "visibility", "url"}]}.
    Use it as is for systems you can export and import, or as the reference
    for a live adapter: see docs/adapters.md.
    """

    def __init__(self, export_file: str | Path):
        self.file = Path(export_file)
        if not self.file.is_file():
            raise FileNotFoundError(f"CMS export not found: {self.file}")

    def _load(self) -> dict:
        return json.loads(self.file.read_text(encoding="utf-8"))

    def list_ids(self) -> list[str]:
        return sorted(str(p["id"]) for p in self._load()["pages"])

    def get(self, page_id: str) -> Page:
        for p in self._load()["pages"]:
            if str(p["id"]) == str(page_id):
                return Page(id=str(p["id"]), title=p.get("title", str(p["id"])), body=p.get("body", ""),
                            visibility=p.get("visibility", "public"), location=p.get("url", ""))
        raise KeyError(f"No such page: {page_id}")

    def write(self, page_id: str, body: str) -> None:
        data = self._load()
        for p in data["pages"]:
            if str(p["id"]) == str(page_id):
                p["body"] = body
                self.file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                return
        raise KeyError(f"No such page: {page_id}")


def open_store(location: str | Path) -> PageStore:
    """Open a folder of Markdown or a CMS export, whichever the path is."""
    path = Path(location)
    if path.is_dir():
        return GitMarkdownStore(path)
    if path.suffix == ".json":
        return JsonCmsStore(path)
    raise ValueError(f"Cannot open a page store at {location}: expected a folder or a .json export")
