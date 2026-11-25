import hashlib
import json
import math
import re

import pytest

from conftest import event
from docloop.embeddings import CachedEmbedder, chunk_page, hybrid_search, make_searcher, vector_search
from docloop.impact import find_pages
from docloop.judge import Judge, parse_verdict
from docloop.models import Candidate, ChangeEvent
from docloop.replay import replay, to_markdown
from test_store_and_replay import history  # noqa: F401  (fixture)

SYNONYMS = {"teammates": "team", "colleagues": "team", "invite": "member", "spreadsheet": "csv"}


class FakeEmbedder:
    """Bag-of-words vectors with a few synonyms, so 'meaning' can be tested without a model."""
    name = "fake:bow"

    def __init__(self):
        self.texts_embedded = 0

    def embed(self, texts):
        self.texts_embedded += len(texts)
        out = []
        for text in texts:
            vec = [0.0] * 512
            for word in re.findall(r"[a-z]{3,}", text.lower()):
                word = SYNONYMS.get(word, word)
                vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % 512] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            out.append([x / norm for x in vec])
        return out


def test_chunks_carry_the_page_title(ws):
    chunks = chunk_page(ws.store.get("charts/exporting-data"))
    assert len(chunks) >= 3 and all(c.startswith("Exporting data") for c in chunks)


def test_vector_search_matches_on_meaning_where_words_differ(ws):
    query = "bring colleagues and teammates onboard"
    assert ws.search_pages(query)["results"] == []                 # lexical: no shared words
    top = vector_search(query, ws.store, FakeEmbedder())[0]
    assert top.page_id == "account/team-workspaces" and top.basis == "vector"


def test_embeddings_are_cached_by_content(ws, tmp_path):
    inner = FakeEmbedder()
    cached = CachedEmbedder(inner, tmp_path / "emb")
    vector_search("export csv", ws.store, cached)
    first = inner.texts_embedded
    vector_search("export csv", ws.store, cached)
    assert inner.texts_embedded == first, "a second identical search must embed nothing"
    again = CachedEmbedder(FakeEmbedder(), tmp_path / "emb")
    vector_search("export csv", ws.store, again)
    assert again.inner.texts_embedded == 0, "the cache survives on disk"


def test_hybrid_ranks_pages_both_methods_agree_on_first(ws):
    found = hybrid_search("legacy csv export option", ws.store, FakeEmbedder())
    assert found[0].page_id == "charts/exporting-data" and found[0].basis == "hybrid"
    assert len(found) <= 8 and len({c.page_id for c in found}) == len(found)


def test_a_searcher_cannot_smuggle_in_an_invented_page(ws):
    fake = lambda query, store: [Candidate("charts/made-up", "Made up", "vector", 0.99),
                                 Candidate("charts/exporting-data", "Exporting data", "vector", 0.9)]
    e = ChangeEvent.from_dict(json.loads(open(event("retire-csv")).read()))
    assert [c.page_id for c in find_pages(e, ws.store, fake)] == ["charts/exporting-data"]


def test_explicit_references_still_win_over_any_searcher(ws):
    boom = lambda query, store: pytest.fail("the searcher must not run when the event names its pages")
    e = ChangeEvent.from_dict(json.loads(open(event("fix-screenshot")).read()))
    assert [c.basis for c in find_pages(e, ws.store, boom)] == ["explicit reference"]


def test_make_searcher_validates_its_arguments(tmp_path):
    assert make_searcher("lexical", None, tmp_path) is None
    with pytest.raises(ValueError, match="needs an embedder"):
        make_searcher("hybrid", None, tmp_path)
    with pytest.raises(ValueError, match="Unknown embedder"):
        make_searcher("vector", "nope:model", tmp_path)


def test_parse_verdict_is_strict_but_tolerant_of_wrapping():
    assert parse_verdict('{"keep": true, "evidence": "x"}') == {"keep": True, "evidence": "x"}
    assert parse_verdict('Sure!\n```json\n{"keep": false, "evidence": "topic only"}\n```')["keep"] is False
    assert parse_verdict("I think yes") is None
    assert parse_verdict('{"verdict": "yes"}') is None


class ScriptedChat:
    name = "scripted"

    def __init__(self, rule):
        self.rule, self.calls = rule, 0

    def chat(self, messages):
        self.calls += 1
        return self.rule(messages[-1]["content"])


def test_replay_with_a_reading_step_reports_before_and_after(history, tmp_path):
    # A searcher that always proposes all three pages: recall 100%, precision 33%.
    everything = lambda query, store: [Candidate(i, i, "vector", 1.0) for i in store.list_ids()]

    def rule(prompt):   # a perfect reader: keep the page whose topic the change names
        change, page = prompt.split("PAGE id:")
        topic = {"docs/export": "csv", "docs/views": "views", "docs/team": "invite"}[page.split()[0]]
        return json.dumps({"keep": topic in change.lower(), "evidence": "..."})

    chat = ScriptedChat(rule)
    judge = Judge(chat, tmp_path / "judge.json")
    # drop the event that names its page, so both remaining events go through search
    report = replay(history, ["docs"], searcher=everything, judge=judge)
    reading = report["reading_step"]
    assert reading["model"] == "scripted" and reading["unparsed_replies"] == 0
    searched = [e for e in report["events"] if e["basis"] != "explicit reference"]
    assert searched and all(e["after_reading"]["precision"] == 1.0 and e["after_reading"]["recall"] == 1.0 for e in searched)
    assert all(e["precision"] < 0.5 for e in searched), "before reading, precision was low"
    assert reading["overall"]["after"]["mean_recall"] == 1.0
    assert reading["overall"]["mean_candidates_after"] < reading["overall"]["mean_candidates_before"]
    assert "## Reading step (scripted)" in to_markdown(report)
    calls = chat.calls
    replay(history, ["docs"], searcher=everything, judge=Judge(chat, tmp_path / "judge.json"))
    assert chat.calls == calls, "verdicts are cached: a rerun costs no model calls"


def test_an_unreadable_model_reply_keeps_the_page_and_is_counted(history):
    judge = Judge(ScriptedChat(lambda prompt: "hmm, maybe?"))
    report = replay(history, ["docs"], judge=judge)
    assert report["reading_step"]["unparsed_replies"] > 0
    for e in report["events"]:
        assert e["after_reading"]["kept"] == e["predicted"], "never drop a page on an answer we could not read"


def test_replay_reports_older_and_newer_halves(history):
    periods = replay(history, ["docs"])["summary"]["by_period"]
    assert set(periods) == {"older half", "newer half"}
    assert periods["older half"]["events"] + periods["newer half"]["events"] == 2
