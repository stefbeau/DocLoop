"""Deterministic checks that run before a person sees a draft.

These catch what a rule can catch, so the model and the reviewer spend their
attention on what needs judgement. Add your own house rules here.
"""
from __future__ import annotations

import re

_CONTRACTION = re.compile(r"\b\w+(?:n't|'re|'ll|'ve)\b|\b(?:it|that|there|here|what)'s\b", re.I)
_VAGUE_LINK = re.compile(r"\[(?:click here|here|this link|link)\]\(", re.I)


def lint_page(body: str) -> list[dict]:
    issues = []
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", body, re.M)]
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            issues.append({"rule": "heading-skip", "severity": "important", "detail": f"heading jumps from level {prev} to {cur}"})
            break
    if levels.count(1) > 1:
        issues.append({"rule": "single-h1", "severity": "important", "detail": "more than one top-level heading"})
    if _VAGUE_LINK.search(body):
        issues.append({"rule": "link-text", "severity": "suggestion", "detail": "link text should say where the link goes"})
    if re.search(r"\b(TODO|TBD|FIXME|lorem ipsum)\b", body, re.I):
        issues.append({"rule": "placeholder", "severity": "critical", "detail": "placeholder text left in the page"})
    if re.search(r"!\[\s*\]\(", body):
        issues.append({"rule": "alt-text", "severity": "important", "detail": "image without alt text"})
    return issues


def lint_notice(subject: str, body: str, change_type: str = "change") -> list[dict]:
    issues = []
    if len(subject) > 90:
        issues.append({"rule": "subject-length", "severity": "suggestion", "detail": "subject is longer than 90 characters"})
    if change_type == "change" and not re.search(r"\d", subject):
        issues.append({"rule": "subject-date", "severity": "important", "detail": "a change notice should carry its date in the subject"})
    if change_type == "change" and not re.search(r"\b\d{4}\b", body):
        issues.append({"rule": "body-date", "severity": "critical", "detail": "no effective date in the body"})
    if _CONTRACTION.search(body):
        issues.append({"rule": "no-contractions", "severity": "suggestion", "detail": "contractions in a customer notice"})
    if not re.search(r"\b(support|contact|help)\b", body, re.I):
        issues.append({"rule": "closing-contact", "severity": "important", "detail": "no support contact or help link at the end"})
    if len(body.split()) > 180:
        issues.append({"rule": "length", "severity": "suggestion", "detail": "notice is longer than 180 words"})
    return issues
