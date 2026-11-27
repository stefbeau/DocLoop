"""Plain data shapes shared by every tool."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ChangeEvent:
    """A product change that may affect documentation.

    It can come from a pull request, an issue, a release note or a ticket.
    """

    id: str
    title: str
    body: str = ""
    comments: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    source: str = "manual"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChangeEvent":
        known = {k: data[k] for k in ("id", "title", "body", "comments", "labels", "source") if k in data}
        return cls(**known)

    def text(self, include_comments: bool = True) -> str:
        parts = [self.title, self.body]
        if include_comments:
            parts.extend(self.comments)
        return "\n".join(p for p in parts if p)


@dataclass
class Page:
    id: str
    title: str
    body: str
    visibility: str = "public"  # "public" or "internal"
    location: str = ""  # file path or URL, for humans
    description: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Signal:
    detector: str
    evidence: str


@dataclass
class Classification:
    event_id: str
    change_type: str  # change | enhancement | content_area | direct | unknown
    docs_changes_noted: bool
    notice_required: bool
    effective_date: str | None
    confidence: float
    signals: list[Signal]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Route:
    mode: str  # both | docs_only | notice_only | neither | human_triage
    steps: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Candidate:
    page_id: str
    title: str
    basis: str  # "explicit reference" or "search"
    score: float
    tier: str = ""  # "likely" or "also check" once a model has read the page (pass 3); empty before

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
