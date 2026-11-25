"""Intake: rule-based detectors. No model call anywhere in this file.

Each detector looks for one kind of evidence in the change event and reports
what it matched, so every routing decision can be audited afterwards.
"""
from __future__ import annotations

import re

from .models import ChangeEvent, Classification, Signal

_DATE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[- ](?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*[- ]\d{4})\b", re.I)
_PAGE_REF = re.compile(
    r"(?:docs?/[\w\-/]+(?:\.md)?|\b(?!(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-)[A-Z]{2,5}-\d{2,6}\b|/pages?/[\w\-/]+)")


def _find(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.I)
    return match.group(0) if match else None


def detect_retirement(text: str) -> str | None:
    return _find(r"\b(retir\w+|deprecat\w+|sunset\w*|end[- ]of[- ]life|will be removed|no longer (?:supported|available))\b", text)


def detect_breaking(text: str) -> str | None:
    return _find(r"\b(breaking change|behaviou?r change|renam\w+|migrat\w+|replac\w+ by|must (?:now|update))\b", text)


def detect_new_capability(text: str) -> str | None:
    return _find(r"\b(can now|new feature|now supports?|introduc\w+|adds? (?:support|the ability)|enhancement)\b", text)


def detect_docs_fix(text: str) -> str | None:
    return _find(r"\b(typo|outdated screenshot|broken link|wrong in the docs|docs? (?:fix|bug|error)|screenshot)\b", text)


def detect_restructure(text: str) -> str | None:
    return _find(r"\b(reorgani[sz]e\w*|restructur\w+|new section|split (?:the|this) page|merge (?:the|these) pages|information architecture)\b", text)


def detect_page_refs(text: str) -> str | None:
    return _find(_PAGE_REF.pattern, text)


def detect_notice_request(text: str) -> str | None:
    return _find(r"\b(notify (?:customers|clients|users)|customer notice|client notice|release note|announce\w*|heads[- ]up to (?:customers|clients))\b", text)


def detect_no_docs_impact(text: str) -> str | None:
    return _find(r"\b(no (?:docs?|documentation) (?:impact|change|update)s?(?: needed| required)?|internal[- ]only|not user[- ]facing|no user[- ]facing change)\b", text)


def detect_effective_date(text: str) -> str | None:
    match = _DATE.search(text)
    return match.group(1) if match else None


def classify(event: ChangeEvent) -> Classification:
    """Classify a change event from its text, comments included.

    Comments matter: the request for a customer notice is often made there
    and not in the form fields.
    """
    text = event.text(include_comments=True)
    labels = {label.lower() for label in event.labels}
    signals: list[Signal] = []

    def run(name: str, fn) -> str | None:
        hit = fn(text)
        if hit:
            signals.append(Signal(name, hit))
        return hit

    retirement = run("retirement", detect_retirement)
    breaking = run("breaking", detect_breaking)
    capability = run("new_capability", detect_new_capability)
    docs_fix = run("docs_fix", detect_docs_fix)
    restructure = run("restructure", detect_restructure)
    page_refs = run("page_refs", detect_page_refs)
    notice = run("notice_request", detect_notice_request)
    date = run("effective_date", detect_effective_date)
    no_docs = run("no_docs_impact", detect_no_docs_impact) or ("no-docs" in labels)

    if retirement or breaking or "breaking" in labels or "deprecation" in labels:
        change_type = "change"
    elif restructure or "content-area" in labels:
        change_type = "content_area"
    elif docs_fix or "docs" in labels or "documentation" in labels:
        change_type = "direct"
    elif capability or "enhancement" in labels or "feature" in labels:
        change_type = "enhancement"
    else:
        change_type = "unknown"

    type_votes = sum(bool(x) for x in (retirement or breaking, restructure, docs_fix, capability))
    if change_type == "unknown":
        confidence = 0.3
    elif type_votes == 1:
        confidence = 0.9
    else:
        confidence = 0.75  # several kinds of evidence: plausible, worth a second look
    if change_type == "change" and not date:
        confidence -= 0.1  # a retirement with no date is incomplete

    # A known kind of change always gets a docs check: a retired feature must not
    # stay documented, and a new one must not go undocumented. The only way out is
    # an explicit statement that users see no difference.
    docs_noted = change_type != "unknown" and not no_docs
    notice_required = bool(notice or retirement or breaking)

    return Classification(
        event_id=event.id, change_type=change_type, docs_changes_noted=docs_noted,
        notice_required=notice_required, effective_date=date,
        confidence=round(max(confidence, 0.0), 2), signals=signals)
