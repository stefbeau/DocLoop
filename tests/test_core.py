import json

import pytest

from conftest import ROOT, event
from docloop import rules
from docloop.detectors import classify
from docloop.models import ChangeEvent
from docloop.routing import route


def load(name):
    return ChangeEvent.from_dict(json.loads(open(event(name)).read()))


@pytest.mark.parametrize("name,kind,mode", [
    ("retire-csv", "change", "both"),
    ("share-views", "enhancement", "docs_only"),
    ("fix-screenshot", "direct", "docs_only"),
    ("restructure-start", "content_area", "docs_only"),
    ("vague", "unknown", "human_triage"),
])
def test_classify_and_route(name, kind, mode):
    c = classify(load(name))
    assert c.change_type == kind
    assert route(c).mode == mode


def test_notice_request_is_found_in_comments():
    e = load("share-views")
    assert classify(e).notice_required is False
    e.comments.append("Please notify customers when this ships.")
    assert classify(e).notice_required is True


def test_docs_check_is_the_default_and_needs_an_explicit_opt_out():
    e = load("retire-csv")
    assert classify(e).docs_changes_noted is True
    e.comments.append("Backend only, no docs impact.")
    c = classify(e)
    assert c.docs_changes_noted is False and route(c).mode == "notice_only"
    e = load("share-views")
    e.labels.append("no-docs")
    assert route(classify(e)).mode == "neither"


def test_a_date_is_not_mistaken_for_a_page_reference():
    c = classify(load("retire-csv"))
    assert c.effective_date == "15-JAN-2027"
    assert "page_refs" not in [s.detector for s in c.signals]


def test_retirement_without_a_date_loses_confidence():
    e = load("retire-csv")
    e.body = "The legacy CSV export option will be removed."
    assert classify(e).confidence < classify(load("retire-csv")).confidence


def test_low_confidence_goes_to_a_person():
    c = classify(load("retire-csv"))
    c.confidence = 0.5
    assert route(c).mode == "human_triage"


def test_explicit_references_win_and_stop(ws):
    pages = ws.find_affected_pages(event("fix-screenshot"))["candidates"]
    assert [p["page_id"] for p in pages] == ["charts/exporting-data"]
    assert pages[0]["basis"] == "explicit reference"


def test_search_finds_the_right_pages_and_only_real_ids(ws):
    pages = ws.find_affected_pages(event("retire-csv"))["candidates"]
    ids = [p["page_id"] for p in pages]
    assert ids[0] == "charts/exporting-data" and "charts/file-formats" in ids
    assert all(ws.store.exists(i) for i in ids)


def test_search_returns_nothing_for_noise(ws):
    assert ws.find_affected_pages(event("vague"))["candidates"] == []
    assert ws.search_pages("kubernetes cluster autoscaling")["results"] == []


def test_same_tools_work_on_a_cms_export(cms_ws):
    ids = [p["page_id"] for p in cms_ws.find_affected_pages(event("retire-csv"))["candidates"]]
    assert ids[0] == "charts/exporting-data"
    assert cms_ws.read_page("charts/saving-a-view")["title"] == "Saving a view"


def test_page_id_cannot_escape_the_docs_folder(ws):
    with pytest.raises((ValueError, KeyError)):
        ws.read_page("../../etc/passwd")


def test_lint_rules():
    assert any(i["rule"] == "placeholder" for i in rules.lint_page("# A\n\nTODO write this"))
    assert any(i["rule"] == "heading-skip" for i in rules.lint_page("# A\n\n### C\n"))
    assert rules.lint_page("# A\n\n## B\n\nText.\n") == []
    issues = [i["rule"] for i in rules.lint_notice("Product update", "We're removing it. It's gone.", "change")]
    assert {"subject-date", "body-date", "no-contractions", "closing-contact"} <= set(issues)


def test_census(ws):
    f = ws.corpus_census(str(ROOT / "examples" / "index.json"))["findings"]
    assert f["blind_spots"]["pages"] == ["account/team-workspaces"]
    assert f["ghosts"]["pages"] == ["charts/old-print-dialog"]
    assert f["wrongly_suppressed"]["pages"] == ["charts/file-formats"]
    assert f["leaked_internal"]["pages"] == []
