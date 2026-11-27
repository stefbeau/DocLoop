import shutil
from pathlib import Path

import pytest

from docloop.workspace import Workspace

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "examples" / "events"


@pytest.fixture
def ws(tmp_path):
    docs = tmp_path / "docs"
    shutil.copytree(ROOT / "examples" / "docs", docs)
    return Workspace(docs, tmp_path / "state")


@pytest.fixture
def cms_ws(tmp_path):
    export = tmp_path / "pages.json"
    shutil.copy(ROOT / "examples" / "cms" / "pages.json", export)
    return Workspace(export, tmp_path / "state")


def event(name: str) -> str:
    return str(EVENTS / f"{name}.json")


@pytest.fixture(autouse=True)
def _words_only_search_unless_a_test_says_otherwise(monkeypatch):
    """Hybrid search is the product default and needs an embedder; the older tests check the word search."""
    monkeypatch.setenv("DOCLOOP_SEARCH", "lexical")
