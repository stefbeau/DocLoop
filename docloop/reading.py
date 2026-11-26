"""Pass 3: a model reads each candidate and sorts it. It never deletes one.

Earlier measurements showed that a reader which deletes loses about a quarter of the right pages.
So the reader only orders the list into two tiers, and the reviewer sees the "likely" pages first.
"""
from __future__ import annotations

from dataclasses import replace

from .models import Candidate, ChangeEvent
from .stores import PageStore

LIKELY = "likely"
ALSO_CHECK = "also check"


def triage(event: ChangeEvent, candidates: list[Candidate], store: PageStore, judge) -> list[Candidate]:
    """Same pages in, same pages out. Likely pages first; search order is kept inside each tier.

    An unreadable model reply counts as "likely", so a page is never pushed down for an answer we could not read.
    """
    sorted_: list[Candidate] = []
    for c in candidates:
        verdict = judge.keep(event, store.get(c.page_id))
        sorted_.append(replace(c, tier=LIKELY if verdict["keep"] else ALSO_CHECK))
    return [c for c in sorted_ if c.tier == LIKELY] + [c for c in sorted_ if c.tier == ALSO_CHECK]
