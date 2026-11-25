"""MCP server: exposes the agent tools, and only the agent tools.

Run:  DOCLOOP_DOCS=path/to/docs python -m docloop.mcp_server
The human gate (approve, apply) is deliberately absent. Use the CLI for that.
"""
from __future__ import annotations

try:  # mcp 2.x
    from mcp.server import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

from .workspace import Workspace

mcp = _Server("docloop")
_ws: Workspace | None = None


def ws() -> Workspace:
    global _ws
    if _ws is None:
        _ws = Workspace()
    return _ws


@mcp.tool()
def classify_event(event_file: str) -> dict:
    """Classify a change event with rule-based detectors. Returns type, flags, confidence and the evidence."""
    return ws().classify_event(event_file)


@mcp.tool()
def route_event(event_file: str) -> dict:
    """Decide which steps run for this event, from a fixed table. Returns mode, steps and the reason."""
    return ws().route_event(event_file)


@mcp.tool()
def find_affected_pages(event_file: str) -> dict:
    """List pages the change touches: pages the event names first, then search results, capped at 8. Ids are always real."""
    return ws().find_affected_pages(event_file)


@mcp.tool()
def search_pages(query: str) -> dict:
    """Search the documentation. Returns at most 8 page ids with titles and scores."""
    return ws().search_pages(query)


@mcp.tool()
def read_page(page_id: str) -> dict:
    """Read one page by id. Fails if the id does not exist."""
    return ws().read_page(page_id)


@mcp.tool()
def propose_edit(event_id: str, page_id: str, new_body: str, rationale: str) -> dict:
    """Propose a full replacement body for one existing page. Nothing is written to the docs."""
    return ws().propose_edit(event_id, page_id, new_body, rationale)


@mcp.tool()
def propose_notice(event_id: str, subject: str, body: str) -> dict:
    """Save a customer notice draft for review. Nothing is sent."""
    return ws().propose_notice(event_id, subject, body)


@mcp.tool()
def review_status(event_id: str) -> dict:
    """Report where an event stands: route, proposals, approval, and a readiness score with its breakdown."""
    return ws().review_status(event_id)


@mcp.tool()
def corpus_census(index_file: str) -> dict:
    """Reconcile the docs store with a search index listing. Returns blind spots, ghosts and visibility mismatches."""
    return ws().corpus_census(index_file)


if __name__ == "__main__":
    mcp.run()
