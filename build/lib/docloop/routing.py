"""Routing: a lookup table, not a judgement call."""
from __future__ import annotations

from .models import Classification, Route

CONFIDENCE_FLOOR = 0.7
ALWAYS_DOCS_ONLY = {"content_area", "direct"}

STEPS = {
    "both": ["impact", "draft", "human_gate", "notice", "audit"],
    "docs_only": ["impact", "draft", "human_gate", "audit"],
    "notice_only": ["notice", "human_gate", "audit"],
    "neither": ["audit"],
    "human_triage": ["human_triage"],
}


def route(c: Classification) -> Route:
    if c.change_type == "unknown" or c.confidence < CONFIDENCE_FLOOR:
        mode, reason = "human_triage", f"confidence {c.confidence} is below {CONFIDENCE_FLOOR} or the type is unknown"
    elif c.change_type in ALWAYS_DOCS_ONLY:
        mode, reason = "docs_only", f"{c.change_type} requests never need a customer notice"
    elif c.docs_changes_noted and c.notice_required:
        mode, reason = "both", "docs change and customer notice both detected"
    elif c.docs_changes_noted:
        mode, reason = "docs_only", "docs change detected, no notice needed"
    elif c.notice_required:
        mode, reason = "notice_only", "customer notice needed, no docs change detected"
    else:
        mode, reason = "neither", "no docs change and no notice detected"
    return Route(mode=mode, steps=STEPS[mode], reason=reason)
