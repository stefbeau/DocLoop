"""Optional vector search: match on meaning, not only on shared words.

Pick an embedder with a short spec:

    hf:BAAI/bge-small-en-v1.5            Hugging Face Inference (needs HF_TOKEN)
    openai:text-embedding-3-small        any OpenAI-compatible endpoint (needs OPENAI_API_KEY)
    local:all-MiniLM-L6-v2               sentence-transformers on this machine (no key)

Vectors are cached on disk by content hash, so re-running a search or a
replay only embeds text that changed.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Callable, Protocol

from .impact import MAX_CANDIDATES, search as lexical_search
from .models import Candidate, Page
from .stores import PageStore, split_front_matter

CHUNK_WORDS = 220
BATCH = 32


class Embedder(Protocol):
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HFEmbedder:
    def __init__(self, model: str):
        from huggingface_hub import InferenceClient  # optional dependency
        self.client, self.model, self.name = InferenceClient(token=os.environ.get("HF_TOKEN")), model, f"hf:{model}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        out = self.client.feature_extraction(texts, model=self.model)
        rows = out.tolist() if hasattr(out, "tolist") else list(out)
        if rows and isinstance(rows[0], (int, float)):   # a single text can come back as one flat vector
            rows = [rows]
        return [_pool(r) for r in rows]


class OpenAIEmbedder:
    def __init__(self, model: str):
        from openai import OpenAI  # optional dependency
        self.client, self.model, self.name = OpenAI(), model, f"openai:{model}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [d.embedding for d in self.client.embeddings.create(model=self.model, input=texts).data]


class LocalEmbedder:
    def __init__(self, model: str):
        from sentence_transformers import SentenceTransformer  # optional dependency
        self.st, self.name = SentenceTransformer(model), f"local:{model}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.st.encode(texts, normalize_embeddings=True).tolist()


def _pool(row) -> list[float]:
    """Some models return one vector per token: average them into one vector."""
    if row and isinstance(row[0], list):
        n = len(row)
        return [sum(tok[i] for tok in row) / n for i in range(len(row[0]))]
    return [float(x) for x in row]


def make_embedder(spec: str) -> Embedder:
    kind, _, model = spec.partition(":")
    makers = {"hf": HFEmbedder, "openai": OpenAIEmbedder, "local": LocalEmbedder}
    if kind not in makers or not model:
        raise ValueError(f"Unknown embedder {spec!r}. Use hf:<model>, openai:<model> or local:<model>.")
    return makers[kind](model)


class CachedEmbedder:
    """Wraps an embedder with a JSON cache keyed by the hash of each text."""

    def __init__(self, embedder: Embedder, cache_dir: str | Path):
        self.inner, self.name = embedder, embedder.name
        self.file = Path(cache_dir) / (re.sub(r"[^\w.-]+", "_", embedder.name) + ".json")
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.cache: dict[str, list[float]] = json.loads(self.file.read_text()) if self.file.is_file() else {}
        self.calls = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
        missing = [(k, t) for k, t in dict(zip(keys, texts)).items() if k not in self.cache]
        for i in range(0, len(missing), BATCH):
            batch = missing[i:i + BATCH]
            vectors = self.inner.embed([t for _, t in batch])
            self.calls += 1
            for (k, _), v in zip(batch, vectors):
                self.cache[k] = [round(float(x), 5) for x in v]
        if missing:
            self.file.write_text(json.dumps(self.cache), encoding="utf-8")
        return [self.cache[k] for k in keys]


def chunk_page(page: Page) -> list[str]:
    """Split a page at headings, then by length. Every chunk carries the page title."""
    body = split_front_matter(page.body)[1]
    sections = [s.strip() for s in re.split(r"\n(?=#{1,6}\s)", body) if s.strip()] or [body.strip() or page.title]
    chunks = []
    for section in sections:
        words = section.split()
        for i in range(0, len(words), CHUNK_WORDS):
            chunks.append(f"{page.title}\n{' '.join(words[i:i + CHUNK_WORDS])}")
    head = " ".join(x for x in [page.title, page.description, " ".join(page.keywords)] if x)
    return [head] + chunks


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def vector_search(query: str, store: PageStore, embedder: Embedder, limit: int = MAX_CANDIDATES) -> list[Candidate]:
    """Rank pages by their best-matching chunk."""
    pages = store.pages()
    owners, texts = [], []
    for page in pages:
        for chunk in chunk_page(page):
            owners.append(page.id)
            texts.append(chunk)
    if not texts or not query.strip():
        return []
    vectors = embedder.embed(texts)
    q = embedder.embed([query])[0]
    best: dict[str, float] = {}
    for owner, vec in zip(owners, vectors):
        score = _cosine(q, vec)
        if score > best.get(owner, -1.0):
            best[owner] = score
    titles = {p.id: p.title for p in pages}
    ranked = sorted(best.items(), key=lambda x: -x[1])[:limit]
    return [Candidate(pid, titles[pid], "vector", round(score, 3)) for pid, score in ranked]


def hybrid_search(query: str, store: PageStore, embedder: Embedder, limit: int = MAX_CANDIDATES) -> list[Candidate]:
    """Reciprocal rank fusion of the lexical and the vector rankings."""
    lexical = lexical_search(query, store, limit)
    vector = vector_search(query, store, embedder, limit)
    fused: dict[str, float] = {}
    titles: dict[str, str] = {}
    for ranking in (lexical, vector):
        for rank, c in enumerate(ranking, start=1):
            fused[c.page_id] = fused.get(c.page_id, 0.0) + 1.0 / (60 + rank)
            titles[c.page_id] = c.title
    ranked = sorted(fused.items(), key=lambda x: -x[1])[:limit]
    top = ranked[0][1] if ranked else 1.0
    return [Candidate(pid, titles[pid], "hybrid", round(score / top, 3)) for pid, score in ranked]


Searcher = Callable[[str, PageStore], list[Candidate]]


def make_searcher(mode: str, embedder_spec: str | None, cache_dir: str | Path) -> Searcher | None:
    """Build the search function for a mode. Returns None for plain lexical search."""
    if mode == "lexical":
        return None
    if mode not in ("vector", "hybrid"):
        raise ValueError("search mode must be lexical, vector or hybrid")
    if not embedder_spec:
        raise ValueError(f"{mode} search needs an embedder, for example hf:BAAI/bge-small-en-v1.5")
    embedder = CachedEmbedder(make_embedder(embedder_spec), cache_dir)
    fn = vector_search if mode == "vector" else hybrid_search
    return lambda query, store: fn(query, store, embedder)
