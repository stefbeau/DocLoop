"""The reading step, scored: a model reads each candidate page and keeps or drops it.

This is what the lead agent does after search, following the impact-mapping
skill. Here it runs alone so its effect on precision and recall can be measured.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Protocol

from .models import ChangeEvent, Page
from .stores import split_front_matter

PAGE_CHARS = 6000

INSTRUCTIONS = """You decide whether ONE documentation page must be edited because of ONE product or documentation change.

Keep the page only if you can point to text on it that the change makes false, incomplete or outdated,
or to the place where the change clearly has to be documented on this page.
Drop it if it merely shares a topic or some words with the change.

Reply with one JSON object and nothing else:
{"keep": true or false, "evidence": "the sentence from the page that must change, or why you drop it"}"""


class ChatModel(Protocol):
    def chat(self, messages: list[dict]) -> str: ...


def make_chat_model(model: str, base_url: str | None = None):
    """An OpenAI-compatible chat client. With only HF_TOKEN set, it uses the Hugging Face router."""
    from openai import OpenAI  # optional dependency
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("HF_TOKEN")
    if not key:
        raise ValueError("Set HF_TOKEN (Hugging Face) or OPENAI_API_KEY before using a model.")
    url = base_url or os.environ.get("OPENAI_BASE_URL")
    if not url and not os.environ.get("OPENAI_API_KEY"):
        url = "https://router.huggingface.co/v1"
    client = OpenAI(base_url=url, api_key=key)

    class _Chat:
        name = model

        def chat(self, messages: list[dict]) -> str:
            reply = client.chat.completions.create(model=model, messages=messages, temperature=0)
            return reply.choices[0].message.content or ""

    return _Chat()


def parse_verdict(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return {"keep": bool(data["keep"]), "evidence": str(data.get("evidence", ""))} if "keep" in data else None


class Judge:
    def __init__(self, model: ChatModel, cache_file: str | Path | None = None, name: str = ""):
        self.model, self.name = model, name or getattr(model, "name", "model")
        self.file = Path(cache_file) if cache_file else None
        self.cache: dict[str, dict] = json.loads(self.file.read_text()) if self.file and self.file.is_file() else {}
        self.calls = self.unparsed = 0

    def keep(self, event: ChangeEvent, page: Page) -> dict:
        body = split_front_matter(page.body)[1][:PAGE_CHARS]
        prompt = (f"CHANGE\n{event.title}\n{event.body}".strip()
                  + f"\n\nPAGE id: {page.id}\nPAGE title: {page.title}\n\n{body}")
        key = hashlib.sha1((self.name + "\x00" + prompt).encode("utf-8")).hexdigest()
        if key not in self.cache:
            reply = self.model.chat([{"role": "system", "content": INSTRUCTIONS}, {"role": "user", "content": prompt}])
            self.calls += 1
            verdict = parse_verdict(reply)
            if verdict is None:
                # An unreadable answer must not silently drop a page: keep it and count it.
                verdict = {"keep": True, "evidence": "unparsed model reply", "unparsed": True}
            self.cache[key] = verdict
            if self.file:
                self.file.parent.mkdir(parents=True, exist_ok=True)
                self.file.write_text(json.dumps(self.cache), encoding="utf-8")
        if self.cache[key].get("unparsed"):
            self.unparsed += 1
        return self.cache[key]
