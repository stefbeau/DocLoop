"""The R1 benchmark runner: fixed corpora, a hybrid run that cannot silently be a word-search run, per-corpus reports."""
import json
import re
from pathlib import Path

import pytest

from docloop.embeddings import default_searcher
from docloop.judge import Judge
from test_r1_accuracy import GOOD, _report
from test_search_and_judge import FakeEmbedder, ScriptedChat  # noqa: F401
from test_store_and_replay import history  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]


def test_the_corpus_config_matches_the_registration():
    from docloop.r1 import load_config
    from docloop.targets import CORPORA
    cfg = load_config()
    assert [c["name"] for c in cfg["corpora"]] == list(CORPORA)
    assert cfg["model"] == "openai/gpt-oss-120b:fastest" and cfg["embedder"] == "hf:BAAI/bge-small-en-v1.5"
    for c in cfg["corpora"]:
        assert c["repo"].startswith("https://github.com/") and re.fullmatch(r"[0-9a-f]{8,40}", c["ref"])
        assert c["roots"] and c["limit"] == 300 and c["max_pages"] == 10
    assert {c["kind"] for c in cfg["corpora"]} == {"technical", "non-technical"}
    assert sum(c["kind"] == "non-technical" for c in cfg["corpora"]) == 1, "exactly one non-technical corpus"


def _rule(prompt):
    change, page = prompt.split("PAGE id:")
    topic = {"docs/export": "csv", "docs/views": "views", "docs/team": "invite"}[page.split()[0]]
    return json.dumps({"keep": topic in change.lower(), "evidence": "..."})


CORPUS = {"name": "Test docs", "slug": "test", "kind": "technical", "roots": ["docs"], "limit": 50, "max_pages": 10,
          "skip_message": None, "exclude": [], "repo": "https://example.invalid/x", "ref": "abcdef12"}


def test_run_writes_the_report_the_check_and_the_pass_gains(history, tmp_path):
    from docloop.r1 import run
    searcher, label = default_searcher(None, tmp_path / "e", factory=lambda s: FakeEmbedder(), env={})
    result = run(CORPUS, history, tmp_path / "out", searcher, label, Judge(ScriptedChat(_rule)))
    saved = json.loads((tmp_path / "out" / "test.json").read_text(encoding="utf-8"))
    assert saved["corpus"] == "Test docs" and saved["search"].startswith("hybrid (") and saved["reader"] == "scripted"
    assert saved["check"]["status"] == "too few events", "two events are below the 60-event floor"
    assert set(saved["passes"]) == {"pass1_words", "pass2_hybrid", "pass3_reading"}
    assert {"top_3_hit", "mrr"} <= set(saved["passes"]["pass2_hybrid"]["figures"])
    assert "kept" in saved["passes"]["pass2_hybrid"]["gain"] and "kept" in saved["passes"]["pass3_reading"]["gain"]
    assert "## Reading as sorting" in (tmp_path / "out" / "test.md").read_text(encoding="utf-8")
    assert result["slug"] == "test"


def test_a_run_that_fell_back_to_words_is_refused(history, tmp_path):
    from docloop.r1 import run
    with pytest.raises(RuntimeError, match="fell back"):
        run(CORPUS, history, tmp_path / "out", None, "lexical (fallback: no token)", Judge(ScriptedChat(_rule)))
    assert not (tmp_path / "out" / "test.json").exists(), "an invalid run leaves no report behind"


def _fake_result(slug, name, report, kept2=True, kept3=True):
    return {"corpus": name, "slug": slug, "kind": "non-technical" if slug == "service-manual" else "technical",
            "head": "abcdef12", "search": "hybrid (hf:BAAI/bge-small-en-v1.5)", "reader": "openai/gpt-oss-120b:fastest",
            "model_calls": 10, "unparsed_replies": 0,
            "summary": report["summary"], "triage_step": report["triage_step"], "check": __import__("docloop.targets", fromlist=["x"]).check(report),
            "passes": {"pass1_words": {"figures": {"top_3_hit": 0.4, "mrr": 0.3}},
                       "pass2_hybrid": {"figures": {"top_3_hit": 0.5, "mrr": 0.4}, "gain": {"hit_at_3_gain": 0.1, "mrr_gain": 0.1, "kept": kept2}},
                       "pass3_reading": {"figures": {"top_3_hit": 0.6, "mrr": 0.5}, "gain": {"hit_at_3_gain": 0.1, "mrr_gain": 0.1, "kept": kept3}}}}


def _write(dirpath, results):
    dirpath.mkdir(parents=True, exist_ok=True)
    for r in results:
        (dirpath / f"{r['slug']}.json").write_text(json.dumps(r), encoding="utf-8")


def test_summary_is_per_corpus_states_misses_and_never_averages(tmp_path):
    from docloop.r1 import summarize
    from docloop.targets import CORPORA
    miss = {**GOOD, "hit_rate": 0.70, "precision_likely": 0.30}
    slugs = ["hub", "openbb", "prometheus", "service-manual"]
    results = [_fake_result(s, n, _report(miss if s == "openbb" else GOOD)) for s, n in zip(slugs, CORPORA)]
    _write(tmp_path / "in", results)
    summary = summarize(tmp_path / "in", tmp_path / "out")
    assert summary["verdict"]["passed"] is False
    md = (tmp_path / "out" / "r1-report.md").read_text(encoding="utf-8")
    for name in CORPORA:
        assert name in md
    assert "average" not in md.lower() and "mean across" not in md.lower()
    assert re.search(r"OpenBB docs.*missed", md, re.S), "the miss is published, not hidden"
    assert (tmp_path / "out" / "r1-summary.json").is_file()


def test_summary_states_the_scope_of_each_pass(tmp_path):
    from docloop.r1 import summarize
    from docloop.targets import CORPORA
    slugs = ["hub", "openbb", "prometheus", "service-manual"]
    results = [_fake_result(s, n, _report(GOOD), kept2=True, kept3=(s in ("hub", "openbb"))) for s, n in zip(slugs, CORPORA)]
    _write(tmp_path / "in", results)
    summary = summarize(tmp_path / "in", tmp_path / "out")
    assert summary["pass_scope"] == {"pass2_hybrid": "kept", "pass3_reading": "corpus-dependent"}


def test_summary_of_an_incomplete_set_says_so(tmp_path):
    from docloop.r1 import summarize
    from docloop.targets import CORPORA
    _write(tmp_path / "in", [_fake_result("hub", CORPORA[0], _report(GOOD))])
    summary = summarize(tmp_path / "in", tmp_path / "out")
    assert summary["verdict"]["passed"] is None and summary["missing"] == ["openbb", "prometheus", "service-manual"]


def test_the_benchmark_workflow_runs_exactly_the_registered_corpora_and_needs_the_secret():
    from docloop.r1 import load_config
    text = (ROOT / ".github" / "workflows" / "r1-benchmark.yml").read_text(encoding="utf-8")
    slugs = re.search(r"slug:\s*\[([^\]]*)\]", text).group(1).replace(" ", "").split(",")
    assert slugs == [c["slug"] for c in load_config()["corpora"]]
    assert "secrets.HF_TOKEN" in text and "workflow_dispatch" in text
    assert "--force" not in text and "push -f" not in text, "no force-push"
    assert "summarize" in text, "the same job set ends in the summary"
