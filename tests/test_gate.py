import pytest

from conftest import event

PAGE = "charts/exporting-data"


def propose(ws):
    ws.route_event(event("fix-screenshot"))
    old = ws.read_page(PAGE)["body"]
    new = old.replace("You can export", "You can always export")
    return old, new, ws.propose_edit("fix-screenshot", PAGE, new, "test")


def test_proposing_never_writes(ws):
    old, new, result = propose(ws)
    assert ws.read_page(PAGE)["body"] == old
    assert "+You can always export" in result["diff"]


def test_cannot_propose_for_an_invented_page(ws):
    with pytest.raises(KeyError):
        ws.propose_edit("e", "charts/does-not-exist", "x", "y")


def test_apply_refuses_without_approval(ws):
    old, _, _ = propose(ws)
    with pytest.raises(PermissionError):
        ws.apply("fix-screenshot")
    assert ws.read_page(PAGE)["body"] == old


def test_rejection_blocks_and_nothing_is_written(ws):
    old, _, _ = propose(ws)
    ws.approve("fix-screenshot", "A. Writer", "rejected")
    with pytest.raises(PermissionError):
        ws.apply("fix-screenshot")
    assert ws.review_status("fix-screenshot")["readiness"]["state"] == "BLOCKED"
    assert ws.read_page(PAGE)["body"] == old


def test_approved_proposal_is_written(ws):
    _, new, _ = propose(ws)
    assert ws.review_status("fix-screenshot")["readiness"]["state"] == "AWAITING_APPROVAL"
    ws.approve("fix-screenshot", "A. Writer", "approved")
    assert ws.review_status("fix-screenshot")["readiness"]["state"] == "READY"
    assert ws.apply("fix-screenshot")["written"] == [PAGE]
    assert ws.read_page(PAGE)["body"] == new


def test_stale_page_is_refused(ws):
    old, _, _ = propose(ws)
    ws.approve("fix-screenshot", "A. Writer", "approved")
    ws.store.write(PAGE, old + "\nSomeone else edited this.\n")
    result = ws.apply("fix-screenshot")
    assert result["written"] == [] and "page changed" in result["refused"][0]["why"]


def test_proposal_changed_after_approval_is_refused(ws):
    old, _, _ = propose(ws)
    ws.approve("fix-screenshot", "A. Writer", "approved")
    ws.store.write(PAGE, old + "\nNew baseline.\n")
    ws.propose_edit("fix-screenshot", PAGE, old + "\nSneaky.\n", "after approval")
    assert ws.apply("fix-screenshot")["written"] == []


def test_approval_needs_a_name(ws):
    propose(ws)
    with pytest.raises(ValueError):
        ws.approve("fix-screenshot", " ", "approved")


def test_gate_works_on_a_cms_export(cms_ws):
    old = cms_ws.read_page(PAGE)["body"]
    cms_ws.propose_edit("e1", PAGE, old + "\nMore.\n", "test")
    cms_ws.approve("e1", "A. Writer", "approved")
    assert cms_ws.apply("e1")["written"] == [PAGE]
    assert cms_ws.read_page(PAGE)["body"].endswith("More.\n")


def test_audit_log_records_every_step(ws):
    propose(ws)
    ws.approve("fix-screenshot", "A. Writer", "approved")
    ws.apply("fix-screenshot")
    actions = [line.split('"action": "')[1].split('"')[0] for line in (ws.home / "audit.jsonl").read_text().splitlines()]
    assert actions == ["routed", "edit_proposed", "approved", "applied"]
