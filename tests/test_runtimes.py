import pytest

from conftest import ROOT, event
from docloop.agent import LeadAgent, ScriptedModel, demo_script, list_skills, load_skill
from docloop.workspace import Workspace


def test_skill_library_is_complete():
    skills = list_skills()
    assert set(skills) == {"docs-change-lead", "impact-mapping", "drafting-doc-edits", "customer-notice",
                           "review-rules", "corpus-census"}
    assert all(len(d) > 40 for d in skills.values()), "every skill needs a real description"
    lead = load_skill("docs-change-lead")
    for tool in Workspace.AGENT_TOOLS[:3] + ("propose_edit", "propose_notice", "review_status"):
        assert tool in lead, f"the lead skill should mention {tool}"


def test_the_gate_is_never_a_model_tool(ws):
    agent = LeadAgent(ws, ScriptedModel([]), log=lambda s: None)
    assert "approve" not in agent.tools and "apply" not in agent.tools


def test_scripted_run_reaches_the_gate_and_stops(ws):
    log = []
    ev = event("retire-csv")
    final = LeadAgent(ws, ScriptedModel(demo_script(ev, ws)), log=log.append).run(ev)
    assert "approve retire-csv" in final
    status = ws.review_status("retire-csv")
    assert status["mode"] == "both" and status["proposals"] == ["charts/exporting-data"] and status["notice_drafted"]
    assert status["readiness"]["state"] == "AWAITING_APPROVAL"          # everything ready except the human approval
    assert "CSV (legacy)** or" in ws.read_page("charts/exporting-data")["body"]   # docs untouched
    assert any(line.startswith("    ->") for line in log), "the subagent's calls should be logged, indented"


def test_tool_errors_go_back_to_the_model(ws):
    seen = []

    def bad(_m):
        return {"content": "", "tool_calls": [{"id": "1", "name": "read_page", "arguments": {"page_id": "nope"}}]}

    def check(messages):
        seen.append(messages[-1]["content"])
        return {"content": "ok", "tool_calls": []}

    LeadAgent(ws, ScriptedModel([bad, check]), log=lambda s: None).run(event("vague"))
    assert seen[0].startswith("ERROR")


def test_unknown_tool_is_reported(ws):
    seen = []
    script = [lambda m: {"content": "", "tool_calls": [{"id": "1", "name": "apply", "arguments": {"event_id": "x"}}]},
              lambda m: (seen.append(m[-1]["content"]), {"content": "ok", "tool_calls": []})[1]]
    LeadAgent(ws, ScriptedModel(script), log=lambda s: None).run(event("vague"))
    assert "no such tool 'apply'" in seen[0]


def test_mcp_server_lists_agent_tools_only():
    pytest.importorskip("mcp")
    import asyncio
    from docloop import mcp_server
    tools = asyncio.run(mcp_server.mcp.list_tools())
    names = {t.name for t in tools}
    assert names == set(Workspace.AGENT_TOOLS)


def test_smolagents_agents_build(monkeypatch, tmp_path):
    smol = pytest.importorskip("smolagents")
    import importlib.util, shutil
    shutil.copytree(ROOT / "examples" / "docs", tmp_path / "docs")
    monkeypatch.setenv("DOCLOOP_DOCS", str(tmp_path / "docs"))
    monkeypatch.setenv("DOCLOOP_HOME", str(tmp_path / "state"))
    spec = importlib.util.spec_from_file_location("smol_app", ROOT / "runtimes" / "smolagents" / "app.py")
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)

    class NoModel(smol.Model):
        def generate(self, *a, **k):
            raise AssertionError("not called in this test")

    lead = app.build(NoModel())
    assert "page_drafter" in lead.managed_agents
    assert {"approve", "apply"}.isdisjoint(lead.tools)
    assert "classify_event" in lead.tools and "load_skill" in lead.tools
    assert '"change_type": "change"' in app.classify_event(event("retire-csv"))
