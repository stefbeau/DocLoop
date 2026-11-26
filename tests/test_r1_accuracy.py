"""Release R1 (accuracy). Written before the R1 code, against docs/r1-preregistration.md.

What is pinned here: the registered targets cannot drift, hybrid search is the default and its fallback is
never silent, the reading pass sorts but never deletes, and the figures that decide the release are computed
per corpus on the newer half.
"""
import json
import re
from pathlib import Path

import pytest

from docloop.models import Candidate
from docloop.replay import replay
from test_search_and_judge import FakeEmbedder, ScriptedChat  # noqa: F401
from test_store_and_replay import history  # noqa: F401  (fixture)

ROOT = Path(__file__).resolve().parents[1]
PREREG = (ROOT / "docs" / "r1-preregistration.md").read_text(encoding="utf-8")


# --- the registration itself -------------------------------------------------------------------------------

def test_targets_in_code_are_the_registered_ones():
    from docloop.targets import CORPORA, TARGETS
    assert TARGETS == {"hit_rate": 0.90, "mean_recall": 0.80, "precision_likely": 0.60,
                       "right_in_likely": 0.95, "wrong_in_also_check": 0.85}
    for pct in ("90%", "80%", "60%", "95%", "85%"):
        assert pct in PREREG
    assert len(CORPORA) == 4
    for name in CORPORA:
        assert name in PREREG, f"corpus {name!r} is not in the pre-registration"


def test_the_literal_precision_reading_is_reported_with_the_same_target():
    from docloop.targets import LITERAL_PRECISION_TARGET
    assert LITERAL_PRECISION_TARGET == 0.60
    assert "literal reading" in PREREG.lower() and "expected to be missed" in PREREG


# --- pass 2: hybrid by default, fallback never silent ----------------------------------------------------------

def test_hybrid_is_the_default_when_an_embedder_can_be_built(tmp_path):
    from docloop.embeddings import default_searcher
    searcher, label = default_searcher(None, tmp_path, factory=lambda spec: FakeEmbedder(), env={})
    assert searcher is not None and label.startswith("hybrid (")


def test_default_embedder_comes_from_the_environment_then_the_built_in_choice(tmp_path):
    from docloop.embeddings import DEFAULT_EMBEDDER, default_searcher
    seen = []
    default_searcher(None, tmp_path, factory=lambda spec: seen.append(spec) or FakeEmbedder(), env={})
    default_searcher(None, tmp_path, factory=lambda spec: seen.append(spec) or FakeEmbedder(),
                     env={"DOCLOOP_EMBEDDER": "local:all-MiniLM-L6-v2"})
    default_searcher("openai:text-embedding-3-small", tmp_path,
                     factory=lambda spec: seen.append(spec) or FakeEmbedder(), env={})
    assert seen == [DEFAULT_EMBEDDER, "local:all-MiniLM-L6-v2", "openai:text-embedding-3-small"]
    assert DEFAULT_EMBEDDER == "hf:BAAI/bge-small-en-v1.5"


@pytest.mark.parametrize("failure", [ImportError("No module named 'huggingface_hub'"), ValueError("no token")])
def test_when_no_embedder_works_the_fallback_is_lexical_and_says_why(tmp_path, failure):
    from docloop.embeddings import default_searcher

    def broken(spec):
        raise failure

    searcher, label = default_searcher(None, tmp_path, factory=broken, env={})
    assert searcher is None, "the fallback is the word search"
    assert label.startswith("lexical (fallback") and str(failure) in label


def test_replay_cli_defaults_to_hybrid_and_labels_the_report(history, tmp_path, monkeypatch):
    import docloop.embeddings as emb
    from docloop.cli import main
    monkeypatch.setattr(emb, "make_embedder", lambda spec: FakeEmbedder())
    out = tmp_path / "r.json"
    assert main(["replay", "--repo", str(history), "--roots", "docs", "--home", str(tmp_path / "h"),
                 "--out", str(out)]) == 0
    assert json.loads(out.read_text())["search"].startswith("hybrid (")


def test_replay_cli_fallback_is_written_in_the_report(history, tmp_path, monkeypatch):
    import docloop.embeddings as emb
    from docloop.cli import main

    def broken(spec):
        raise ImportError("no vector extras")

    monkeypatch.setattr(emb, "make_embedder", broken)
    out = tmp_path / "r.json"
    assert main(["replay", "--repo", str(history), "--roots", "docs", "--home", str(tmp_path / "h"),
                 "--out", str(out)]) == 0
    assert json.loads(out.read_text())["search"].startswith("lexical (fallback")


def test_explicit_lexical_stays_available(history, tmp_path):
    from docloop.cli import main
    out = tmp_path / "r.json"
    assert main(["replay", "--repo", str(history), "--roots", "docs", "--search", "lexical", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["search"] == "lexical"


# --- pass 3: the reader sorts, it never deletes ------------------------------------------------------------------

def _candidates(*ids):
    return [Candidate(i, i, "hybrid", 1.0 - n / 10) for n, i in enumerate(ids)]


class _Store:
    def __init__(self, ids):
        from docloop.models import Page
        self.pages_ = {i: Page(i, i.upper(), f"body of {i}") for i in ids}

    def get(self, page_id):
        return self.pages_[page_id]


class _Judge:
    def __init__(self, keep):
        self.keep_ids, self.unparsed = keep, 0

    def keep(self, event, page):
        return {"keep": page.id in self.keep_ids, "evidence": "x"}


def test_triage_never_deletes_and_puts_likely_first():
    from docloop.models import ChangeEvent
    from docloop.reading import ALSO_CHECK, LIKELY, triage
    found = _candidates("a", "b", "c", "d")
    out = triage(ChangeEvent("e", "change"), found, _Store("abcd"), _Judge({"c", "d"}))
    assert sorted(c.page_id for c in out) == ["a", "b", "c", "d"], "same pages in, same pages out"
    assert [c.page_id for c in out] == ["c", "d", "a", "b"]       # likely first, search order kept inside each tier
    assert [c.tier for c in out] == [LIKELY, LIKELY, ALSO_CHECK, ALSO_CHECK]
    assert all(c.to_dict()["tier"] == c.tier for c in out)


def test_triage_with_nothing_kept_keeps_every_page_as_also_check():
    from docloop.models import ChangeEvent
    from docloop.reading import ALSO_CHECK, triage
    out = triage(ChangeEvent("e", "change"), _candidates("a", "b"), _Store("ab"), _Judge(set()))
    assert [c.page_id for c in out] == ["a", "b"] and {c.tier for c in out} == {ALSO_CHECK}


def test_an_unreadable_reply_is_likely_not_dropped():
    from docloop.models import ChangeEvent
    from docloop.reading import LIKELY, triage

    class Unreadable:
        unparsed = 0

        def keep(self, event, page):
            return {"keep": True, "evidence": "unparsed model reply", "unparsed": True}

    out = triage(ChangeEvent("e", "change"), _candidates("a"), _Store("a"), Unreadable())
    assert out[0].tier == LIKELY


def test_triage_of_an_empty_list_is_empty():
    from docloop.models import ChangeEvent
    from docloop.reading import triage
    assert triage(ChangeEvent("e", "change"), [], _Store(""), _Judge(set())) == []


# --- the measures that decide the release --------------------------------------------------------------------------

def _event(date, truth, predicted, kept):
    hits = [p for p in predicted if p in truth]
    kept_hits = [p for p in kept if p in truth]
    rank = next((i + 1 for i, p in enumerate(predicted) if p in truth), None)
    return {"sha": date, "date": date, "subject": "s", "message_words": 10, "truth": truth, "predicted": predicted,
            "basis": "hybrid", "recall": len(hits) / len(truth), "precision": len(hits) / len(predicted) if predicted else None,
            "reciprocal_rank": 1 / rank if rank else 0.0, "hit": bool(hits), "new_pages": 0,
            "after_reading": {"kept": kept, "recall": len(kept_hits) / len(truth),
                              "precision": len(kept_hits) / len(kept) if kept else None, "hit": bool(kept_hits)}}


def test_triage_summary_measures_the_registered_quantities():
    from docloop.replay import summarise_triage
    rows = [_event("2026-01-01", ["p1"], ["p1", "p2", "p3", "p4"], ["p1"]),          # perfect reader
            _event("2026-01-02", ["p1", "p2"], ["p3", "p1", "p2", "p4"], ["p1", "p3"]),
            _event("2026-01-03", ["p9"], ["p3", "p4"], [])]                              # nothing found, nothing kept
    block = summarise_triage(rows)["overall"]
    assert block["events"] == 3
    assert block["hit_rate"] == round(2 / 3, 3) and block["mean_recall"] == round((1 + 1 + 0) / 3, 3)
    # precision_likely: mean over events whose likely list is not empty: (1/1 + 1/2) / 2
    assert block["precision_likely"] == 0.75 and block["events_with_empty_likely"] == 1
    # right pages in likely: 1 of 1 and 1 of 2 -> 2 of 3
    assert block["right_in_likely"] == round(2 / 3, 3)
    # wrong pages in total: ev1 p2 p3 p4 (3, all also-check), ev2 p3 p4 (p3 is likely, p4 also-check), ev3 p3 p4 (2, also-check)
    assert block["wrong_in_also_check"] == round((3 + 1 + 2) / (3 + 2 + 2), 3)
    assert block["precision_full_list"] is not None


def test_triage_summary_has_periods_and_the_search_order_baseline():
    from docloop.replay import summarise_triage
    rows = [_event(f"2026-01-{d:02d}", ["p1"], ["p2", "p1", "p3"], ["p1"]) for d in range(1, 9)]
    out = summarise_triage(rows)
    assert set(out["by_period"]) == {"older half", "newer half"}
    block = out["overall"]
    assert block["top_3_hit_search_order"] == 1.0 and block["mrr_search_order"] == 0.5
    assert block["mrr_likely_first"] == 1.0, "putting the likely page first lifts the rank"


def test_replay_records_likely_and_also_check_for_each_event(history, tmp_path):
    from docloop.judge import Judge
    everything = lambda query, store: [Candidate(i, i, "vector", 1.0) for i in store.list_ids()]

    def rule(prompt):
        change, page = prompt.split("PAGE id:")
        topic = {"docs/export": "csv", "docs/views": "views", "docs/team": "invite"}[page.split()[0]]
        return json.dumps({"keep": topic in change.lower(), "evidence": "..."})

    report = replay(history, ["docs"], searcher=everything, judge=Judge(ScriptedChat(rule)))
    for e in report["events"]:
        t = e["triage"]
        assert sorted(t["likely"] + t["also_check"]) == sorted(e["predicted"]), "nothing is deleted"
    assert report["triage_step"]["overall"]["hit_rate"] == report["summary"]["overall"]["hit_rate"], \
        "recall and hit rate are measured on the full list, which the reader does not shrink"


def test_old_reports_can_be_rescored_into_the_triage_figures_with_no_model():
    from docloop.replay import rescore
    saved = json.loads((ROOT / "docs" / "benchmarks" / "openbb-hybrid-reading.json").read_text(encoding="utf-8"))
    again = rescore(saved)
    block = again["triage_step"]["overall"]
    assert block["events"] == 80
    assert block["hit_rate"] == saved["summary"]["overall"]["hit_rate"]
    assert 0 <= block["precision_likely"] <= 1


# --- judging a corpus: newer half only, never averaged ------------------------------------------------------------------

def _report(newer, n=100):
    return {"summary": {"overall": {"events": n}, "by_period": {"newer half": {"hit_rate": newer["hit_rate"],
                                                                               "mean_recall": newer["mean_recall"]}}},
            "triage_step": {"by_period": {"newer half": {k: newer[k] for k in
                                                         ("precision_likely", "right_in_likely", "wrong_in_also_check",
                                                          "precision_full_list")}}}}


GOOD = {"hit_rate": 0.91, "mean_recall": 0.81, "precision_likely": 0.61, "right_in_likely": 0.96,
        "wrong_in_also_check": 0.86, "precision_full_list": 0.2}


def test_a_corpus_that_meets_every_target_is_met():
    from docloop.targets import check
    result = check(_report(GOOD))
    assert result["status"] == "evaluated" and result["all_met"] is True
    assert all(m["met"] for m in result["measures"].values())


def test_a_miss_is_recorded_not_moved():
    from docloop.targets import TARGETS, check
    result = check(_report({**GOOD, "hit_rate": 0.89}))
    assert result["all_met"] is False
    assert result["measures"]["hit_rate"] == {"value": 0.89, "target": 0.90, "met": False}
    assert TARGETS["hit_rate"] == 0.90, "checking never edits the target"


def test_the_target_is_inclusive_at_the_line():
    from docloop.targets import check
    assert check(_report({**GOOD, "hit_rate": 0.90}))["measures"]["hit_rate"]["met"] is True


def test_literal_full_list_precision_is_reported_beside_the_primary_one():
    from docloop.targets import check
    result = check(_report(GOOD))
    literal = result["literal_precision_full_list"]
    assert literal == {"value": 0.2, "target": 0.60, "met": False}
    assert result["all_met"] is True, "the primary reading decides the release; the literal one is published beside it"


def test_a_corpus_with_too_few_events_is_not_counted():
    from docloop.targets import check
    result = check(_report(GOOD, n=59))
    assert result["status"] == "too few events" and result["all_met"] is None


def test_release_needs_every_corpus_and_never_averages():
    from docloop.targets import release_verdict
    verdict = release_verdict({"a": _report(GOOD), "b": _report({**GOOD, "mean_recall": 0.5})})
    assert verdict["passed"] is False
    assert verdict["corpora"]["a"]["all_met"] is True and verdict["corpora"]["b"]["all_met"] is False
    assert "average" not in json.dumps(verdict).lower()


# --- the rule for keeping a pass ---------------------------------------------------------------------------------------

def test_a_pass_is_kept_only_where_it_shows_a_gain():
    from docloop.targets import pass_gain
    assert pass_gain({"top_3_hit": 0.60, "mrr": 0.40}, {"top_3_hit": 0.62, "mrr": 0.40})["kept"] is True
    assert pass_gain({"top_3_hit": 0.60, "mrr": 0.40}, {"top_3_hit": 0.60, "mrr": 0.42})["kept"] is True
    assert pass_gain({"top_3_hit": 0.60, "mrr": 0.40}, {"top_3_hit": 0.61, "mrr": 0.41})["kept"] is False
    assert pass_gain({"top_3_hit": 0.60, "mrr": 0.40}, {"top_3_hit": 0.50, "mrr": 0.30})["kept"] is False


def test_a_pass_kept_on_fewer_than_three_corpora_is_published_as_corpus_dependent():
    from docloop.targets import pass_scope
    assert pass_scope({"a": True, "b": True, "c": True, "d": False}) == "kept"
    assert pass_scope({"a": True, "b": True, "c": False, "d": False}) == "corpus-dependent"
    assert pass_scope({"a": False, "b": False, "c": False, "d": False}) == "removed"


# --- the workspace (agent tools, MCP) follows the same default --------------------------------------------------------

def test_workspace_defaults_to_hybrid_and_says_which_search_ran(tmp_path, monkeypatch):
    import shutil

    import docloop.embeddings as emb
    from docloop.workspace import Workspace
    monkeypatch.delenv("DOCLOOP_SEARCH", raising=False)
    monkeypatch.delenv("DOCLOOP_EMBEDDER", raising=False)
    monkeypatch.setattr(emb, "make_embedder", lambda spec: FakeEmbedder())
    shutil.copytree(ROOT / "examples" / "docs", tmp_path / "docs")
    ws = Workspace(tmp_path / "docs", tmp_path / "state")
    found = ws.search_pages("bring colleagues and teammates onboard")
    assert found["search"].startswith("hybrid (")
    assert "account/team-workspaces" in [r["page_id"] for r in found["results"]]


def test_workspace_falls_back_to_words_and_says_so_when_the_embedder_cannot_be_built(tmp_path, monkeypatch):
    import shutil

    import docloop.embeddings as emb
    from docloop.workspace import Workspace
    monkeypatch.delenv("DOCLOOP_SEARCH", raising=False)

    def broken(spec):
        raise ImportError("no vector extras")

    monkeypatch.setattr(emb, "make_embedder", broken)
    shutil.copytree(ROOT / "examples" / "docs", tmp_path / "docs")
    found = Workspace(tmp_path / "docs", tmp_path / "state").search_pages("export csv")
    assert found["search"].startswith("lexical (fallback") and found["results"]


def test_workspace_falls_back_when_the_provider_fails_during_a_search(tmp_path, monkeypatch):
    import shutil

    import docloop.embeddings as emb
    from docloop.workspace import Workspace
    monkeypatch.delenv("DOCLOOP_SEARCH", raising=False)

    class Down:
        name = "down"

        def embed(self, texts):
            raise RuntimeError("402 Payment Required")

    monkeypatch.setattr(emb, "make_embedder", lambda spec: Down())
    shutil.copytree(ROOT / "examples" / "docs", tmp_path / "docs")
    found = Workspace(tmp_path / "docs", tmp_path / "state").search_pages("export csv")
    assert found["search"].startswith("lexical (fallback") and "402" in found["search"] and found["results"]


def test_explicit_lexical_in_the_environment_is_respected(tmp_path, monkeypatch):
    import shutil

    from docloop.workspace import Workspace
    monkeypatch.setenv("DOCLOOP_SEARCH", "lexical")
    shutil.copytree(ROOT / "examples" / "docs", tmp_path / "docs")
    assert Workspace(tmp_path / "docs", tmp_path / "state").search_pages("export csv")["search"] == "lexical"
