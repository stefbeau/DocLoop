"""docloop on smolagents: a lead agent, one managed drafting agent, and a Gradio UI.

Local:  pip install -r requirements.txt && python app.py
Space:  create a Gradio Space, copy this folder plus the `docloop/`, `skills/` and
        `examples/` folders into it, and add an HF_TOKEN secret.

The agents can read, search and propose. Approval and apply stay with a person,
through the docloop command line. Neither is registered as a tool here.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for candidate in (ROOT, ROOT.parent.parent):  # Space layout, then repository layout
    if (candidate / "docloop").is_dir():
        sys.path.insert(0, str(candidate))
        REPO = candidate
        break

from smolagents import GradioUI, InferenceClientModel, ToolCallingAgent, tool  # noqa: E402

from docloop.agent import list_skills, load_skill as _load_skill  # noqa: E402
from docloop.workspace import Workspace  # noqa: E402

os.environ.setdefault("DOCLOOP_SKILLS", str(REPO / "skills"))
ws = Workspace(os.environ.get("DOCLOOP_DOCS", str(REPO / "examples" / "docs")))


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


@tool
def classify_event(event_file: str) -> str:
    """Classify a change event with rule-based detectors. Returns type, flags, confidence and the evidence.

    Args:
        event_file: Path of the change event JSON file.
    """
    return _json(ws.classify_event(event_file))


@tool
def route_event(event_file: str) -> str:
    """Decide which steps run for this event, from a fixed table. Returns mode, steps and the reason.

    Args:
        event_file: Path of the change event JSON file.
    """
    return _json(ws.route_event(event_file))


@tool
def find_affected_pages(event_file: str) -> str:
    """List pages the change touches: pages the event names first, then search results, capped at 8. Ids are always real.

    Args:
        event_file: Path of the change event JSON file.
    """
    return _json(ws.find_affected_pages(event_file))


@tool
def search_pages(query: str) -> str:
    """Search the documentation. Returns at most 8 page ids with titles and scores.

    Args:
        query: Words to look for, such as a feature name or menu path.
    """
    return _json(ws.search_pages(query))


@tool
def read_page(page_id: str) -> str:
    """Read one documentation page by id. Fails if the id does not exist.

    Args:
        page_id: A page id returned by find_affected_pages or search_pages.
    """
    return _json(ws.read_page(page_id))


@tool
def propose_edit(event_id: str, page_id: str, new_body: str, rationale: str) -> str:
    """Propose a full replacement body for one existing page. Nothing is written to the docs.

    Args:
        event_id: Id of the change event this edit belongs to.
        page_id: A real page id.
        new_body: The complete new text of the page.
        rationale: One sentence saying why, naming the change.
    """
    return _json(ws.propose_edit(event_id, page_id, new_body, rationale))


@tool
def propose_notice(event_id: str, subject: str, body: str) -> str:
    """Save a customer notice draft for review. Nothing is sent.

    Args:
        event_id: Id of the change event.
        subject: Subject line of the notice.
        body: Body text of the notice.
    """
    return _json(ws.propose_notice(event_id, subject, body))


@tool
def review_status(event_id: str) -> str:
    """Report where an event stands: route, proposals, approval, and a readiness score with its breakdown.

    Args:
        event_id: Id of the change event.
    """
    return _json(ws.review_status(event_id))


@tool
def corpus_census(index_file: str) -> str:
    """Reconcile the docs with a search index listing. Returns blind spots, ghosts and visibility mismatches.

    Args:
        index_file: Path of the index listing JSON file.
    """
    return _json(ws.corpus_census(index_file))


@tool
def load_skill(name: str) -> str:
    """Load the full instructions of one skill from the library.

    Args:
        name: Skill name, for example drafting-doc-edits.
    """
    return _load_skill(name)


def build(model=None) -> ToolCallingAgent:
    model = model or InferenceClientModel(model_id=os.environ.get("DOCLOOP_MODEL") or None)
    drafter = ToolCallingAgent(
        tools=[read_page, search_pages, propose_edit, load_skill], model=model, max_steps=8,
        name="page_drafter",
        description=("Drafts the edit for ONE documentation page and proposes it. Give it a brief that stands alone: "
                     "event id, what changed with the date, the page id, the specific edit, and what to report."),
        instructions="Load the drafting-doc-edits skill first. You can only propose; you cannot write to the docs.")
    catalogue = "\n".join(f"- {n}: {d}" for n, d in list_skills().items() if n != "docs-change-lead")
    lead_instructions = (_load_skill("docs-change-lead")
                         + "\n\nIn this runtime, `delegate` means calling the managed agent `page_drafter`."
                         + "\n\n## Other skills you can load with load_skill\n" + catalogue)
    return ToolCallingAgent(
        tools=[classify_event, route_event, find_affected_pages, search_pages, read_page, propose_edit,
               propose_notice, review_status, corpus_census, load_skill],
        model=model, managed_agents=[drafter], max_steps=20, instructions=lead_instructions)


if __name__ == "__main__":
    GradioUI(build()).launch()
