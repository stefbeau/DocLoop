"""Impact mapping: which pages does this change touch?

Two rules, in this order:
1. Pages the event names, if they exist, come first.
2. Search fills the remaining places, up to the cap.

An id that the store does not know is never returned.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from .models import Candidate, ChangeEvent
from .stores import PageStore

MAX_CANDIDATES = 8
MIN_SCORE = 0.3
_WORD = re.compile(r"[a-z0-9]{3,}")
_STOP = set("the and for with that this from are was will not you your can now has have into than then when "
            "all any its our their there been being more must should would could about after before".split())


def _tokens(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in _STOP]


def explicit_references(event: ChangeEvent, store: PageStore) -> list[str]:
    text = event.text().lower()
    found = []
    for page_id in store.list_ids():
        needle = page_id.lower()
        if re.search(rf"(?<![\w/]){re.escape(needle)}(?:\.md)?(?![\w/])", text) or \
           re.search(rf"docs?/{re.escape(needle)}(?:\.md)?(?![\w/])", text):
            found.append(page_id)
    return found


def search(query: str, store: PageStore, limit: int = MAX_CANDIDATES) -> list[Candidate]:
    """Small BM25 search over titles and bodies. Swap in a vector index if you have one."""
    pages = store.pages()
    docs = {p.id: _tokens(" ".join([p.title, p.title, p.description, " ".join(p.keywords), p.body])) for p in pages}
    titles = {p.id: p.title for p in pages}
    n = len(docs) or 1
    avg_len = sum(len(t) for t in docs.values()) / n or 1
    df = Counter(term for toks in docs.values() for term in set(toks))
    q_terms = set(_tokens(query))
    if not q_terms:
        return []
    k1, b = 1.5, 0.75
    idf_of = lambda term: math.log(1 + (n - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5))
    known = {term for term in q_terms if df.get(term)}  # words the corpus has never seen cannot count against a page
    total_idf = sum(idf_of(term) for term in known) or 1.0
    need = 1 if len(q_terms) <= 2 else 2  # one incidental shared word is not evidence
    scored = []
    for pid, toks in docs.items():
        tf = Counter(toks)
        score = matched = 0.0
        hits = 0
        for term in q_terms:
            if term not in tf:
                continue
            idf = idf_of(term)
            score += idf * tf[term] * (k1 + 1) / (tf[term] + k1 * (1 - b + b * len(toks) / avg_len))
            matched += idf
            hits += 1
        scored.append((pid, score if hits >= need else 0.0, matched / total_idf))
    top = max((s for _, s, _ in scored), default=0.0)
    if top <= 0:
        return []
    # Score = how much of the query the page covers, scaled by its BM25 rank.
    # A page that matches one incidental word of a long query stays below the floor.
    results = [(pid, share * (0.5 + 0.5 * s / top)) for pid, s, share in scored if s > 0]
    results.sort(key=lambda x: -x[1])
    return [Candidate(pid, titles[pid], "search", round(score, 2)) for pid, score in results[:limit] if score >= MIN_SCORE]


def find_pages(event: ChangeEvent, store: PageStore, searcher=None) -> list[Candidate]:
    """Pages the event names come first; search fills the remaining places.

    `searcher(query, store)` replaces the built-in lexical search, for example
    with a vector index. Whatever the source, only ids the store holds are returned.
    """
    named = explicit_references(event, store)
    found = [Candidate(pid, store.get(pid).title, "explicit reference", 1.0) for pid in named]
    query = event.title + "\n" + event.body
    searched = searcher(query, store) if searcher else search(query, store)
    seen = set(named)
    for c in searched:
        if c.page_id not in seen and store.exists(c.page_id):
            found.append(c)
            seen.add(c.page_id)
    return found[:MAX_CANDIDATES]
