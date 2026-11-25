"""Page stores: one interface, several places documentation can live.

Every tool talks to a PageStore, never to files or an API directly. To support
a new documentation system, subclass PageStore and implement four methods.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
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


DOC_SUFFIXES = (".md", ".mdx")


def split_front_matter(text: str) -> tuple[dict, str]:
    """Split a Markdown file into (front matter, body).

    A missing or malformed header yields an empty dict: one bad page must
    never stop the whole corpus from loading.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[4:end], text[end + 4:]
    try:
        import yaml  # optional: exact YAML when available
        try:
            meta = yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            return {}, body
        return (meta if isinstance(meta, dict) else {}), body
    except ImportError:
        return _simple_front_matter(raw), body


def _simple_front_matter(raw: str) -> dict:
    """Enough YAML for docs headers: `key: value`, inline lists and dash lists."""
    meta: dict = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"\s+-\s+(.*)$", line)
        if item and key:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(item.group(1).strip().strip("\"'"))
            continue
        pair = re.match(r"([\w\-]+):\s*(.*)$", line)
        if pair:
            key, value = pair.group(1), pair.group(2).strip()
            if value.startswith("[") and value.endswith("]"):
                meta[key] = [v.strip().strip("\"'") for v in value[1:-1].split(",") if v.strip()]
            else:
                meta[key] = value.strip("\"'")
    return meta


def _as_list(value) -> list[str]:
    if value is None or value == "":
        return []
    return [str(v) for v in value] if isinstance(value, list) else [str(value)]


class GitMarkdownStore(PageStore):
    """Docs-as-code: every .md or .mdx file under a folder is a page.

    The page id is the path relative to `root`, without the extension.
    `roots` limits the scan to some sub-folders and `exclude` skips others, so
    archived or versioned copies never receive an update proposal.
    Front matter may set `title`, `description`, `keywords` and `visibility`.
    """

    def __init__(self, root: str | Path, roots: tuple[str, ...] | list[str] | None = None,
                 exclude: tuple[str, ...] | list[str] = ()):
        self.root = Path(root)
        if not self.root.is_dir():
            raise FileNotFoundError(f"Docs folder not found: {self.root}")
        self.roots = tuple(roots) if roots else None
        self.exclude = tuple(e.strip("/") for e in exclude)
        for sub in self.roots or ():
            if not (self.root / sub).is_dir():
                raise FileNotFoundError(f"Docs sub-folder not found: {self.root / sub}")
        self._files: dict[str, Path] | None = None

    def _scan(self) -> dict[str, Path]:
        if self._files is None:
            files: dict[str, Path] = {}
            bases = [self.root / sub for sub in self.roots] if self.roots else [self.root]
            for base in bases:
                for path in sorted(base.rglob("*")):
                    if not path.is_file() or path.suffix not in DOC_SUFFIXES:
                        continue
                    rel = path.relative_to(self.root)
                    if any(part.startswith(".") for part in rel.parts):
                        continue
                    if any(rel.as_posix().startswith(e + "/") for e in self.exclude):
                        continue
                    page_id = rel.with_suffix("").as_posix()
                    if page_id in files:
                        raise ValueError(f"Duplicate page id {page_id!r}: {files[page_id].name} and {path.name}")
                    files[page_id] = path
            self._files = files
        return self._files

    def _path(self, page_id: str) -> Path:
        path = self._scan().get(page_id)
        if path is None:
            raise KeyError(f"No such page: {page_id}")
        return path

    def list_ids(self) -> list[str]:
        return sorted(self._scan())

    def exists(self, page_id: str) -> bool:
        return page_id in self._scan()

    def get(self, page_id: str) -> Page:
        path = self._path(page_id)
        # Agents always see "\n" line endings, whatever Git checked out on this machine.
        text = path.read_bytes().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
        meta, body = split_front_matter(text)
        title = meta.get("title")
        if not title:
            heading = re.search(r"^#\s+(.+)$", body, re.M)
            title = heading.group(1).strip() if heading else path.stem
        return Page(id=page_id, title=str(title), body=text, visibility=str(meta.get("visibility", "public")),
                    location=str(path), description=str(meta.get("description") or ""),
                    keywords=_as_list(meta.get("keywords")))

    def write(self, page_id: str, body: str) -> None:
        path = self._path(page_id)
        # Keep the file's own line endings: a Windows checkout stays CRLF, and
        # nothing is ever translated twice.
        crlf = b"\r\n" in path.read_bytes()
        text = body.replace("\r\n", "\n")
        if crlf:
            text = text.replace("\n", "\r\n")
        path.write_bytes(text.encode("utf-8"))

    def commit(self) -> str | None:
        """The Git commit the docs folder is at, or None if it is not a clone."""
        try:
            out = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                 capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    def registry(self) -> dict:
        """Every page that exists, tied to the exact corpus version it describes."""
        pages = []
        for page_id, path in sorted(self._scan().items()):
            page = self.get(page_id)
            raw = path.read_bytes()
            pages.append({"page_id": page_id, "path": path.relative_to(self.root).as_posix(), "title": page.title,
                          "description": page.description, "keywords": page.keywords,
                          "section": "/".join(Path(page_id).parts[:-1][:2]),
                          "words": len(split_front_matter(page.body)[1].split()),
                          "sha256": hashlib.sha256(raw).hexdigest()})
        return {"corpus_commit": self.commit(), "pages": pages}


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


def open_store(location: str | Path, roots=None, exclude=()) -> PageStore:
    """Open a folder of Markdown or a CMS export, whichever the path is."""
    path = Path(location)
    if path.is_dir():
        return GitMarkdownStore(path, roots, exclude)
    if path.suffix == ".json":
        return JsonCmsStore(path)
    raise ValueError(f"Cannot open a page store at {location}: expected a folder or a .json export")
