import subprocess
from pathlib import Path

import pytest

from docloop.replay import replay, to_markdown
from docloop.stores import GitMarkdownStore, split_front_matter


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    write(tmp_path / "content/guides/one.md",
          "---\ntitle: One\ndescription: First page\nkeywords:\n  - alpha\n  - beta\n---\nHello world again\n")
    write(tmp_path / "content-odp/index.mdx", "No front matter here\n")
    write(tmp_path / "content/guides/sidebar.json", "{}")
    write(tmp_path / "archive/v1/old.md", "# Old\n")
    return tmp_path


def test_registry_describes_each_page(corpus):
    registry = GitMarkdownStore(corpus, roots=["content", "content-odp"]).registry()
    by_id = {p["page_id"]: p for p in registry["pages"]}
    assert set(by_id) == {"content/guides/one", "content-odp/index"}
    one = by_id["content/guides/one"]
    assert (one["title"], one["description"], one["keywords"]) == ("One", "First page", ["alpha", "beta"])
    assert one["section"] == "content/guides" and one["words"] == 3 and len(one["sha256"]) == 64
    assert by_id["content-odp/index"]["title"] == "index"


def test_roots_and_exclude_keep_archives_out(corpus):
    assert "archive/v1/old" in GitMarkdownStore(corpus).list_ids()
    assert "archive/v1/old" not in GitMarkdownStore(corpus, exclude=["archive"]).list_ids()
    assert "archive/v1/old" not in GitMarkdownStore(corpus, roots=["content"]).list_ids()


def test_duplicate_page_ids_are_an_error(corpus):
    write(corpus / "content/guides/one.mdx", "# Also one\n")
    with pytest.raises(ValueError, match="Duplicate page id"):
        GitMarkdownStore(corpus).list_ids()


def test_hash_changes_when_page_changes(corpus):
    before = {p["page_id"]: p["sha256"] for p in GitMarkdownStore(corpus, roots=["content"]).registry()["pages"]}
    write(corpus / "content/guides/one.md", "---\ntitle: One\n---\nChanged text\n")
    after = {p["page_id"]: p["sha256"] for p in GitMarkdownStore(corpus, roots=["content"]).registry()["pages"]}
    assert before["content/guides/one"] != after["content/guides/one"]


def test_front_matter_edge_cases():
    assert split_front_matter("---\r\ntitle: Win\r\n---\r\nBody\r\n")[0] == {"title": "Win"}
    assert split_front_matter("no header\n") == ({}, "no header\n")
    assert split_front_matter("---\ntitle: [unclosed\n---\nBody\n")[1].strip() == "Body"
    assert split_front_matter("---\nkeywords: [a, b]\n---\nx")[0]["keywords"] == ["a", "b"]


def test_mdx_pages_can_be_read_and_written(corpus):
    store = GitMarkdownStore(corpus, roots=["content-odp"])
    store.write("content-odp/index", "# Index\n")
    assert store.get("content-odp/index").title == "Index"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


@pytest.fixture
def history(tmp_path):
    repo = tmp_path / "repo"
    write(repo / "docs/export.md", "# Exporting data\n\nChoose legacy CSV or CSV from the Export menu.\n")
    write(repo / "docs/views.md", "# Saving a view\n\nSaved views are visible only to you.\n")
    write(repo / "docs/team.md", "# Team workspaces\n\nInvite a member from the Team menu.\n")
    git(repo, "init", "-q", "-b", "main"); git(repo, "add", "-A"); git(repo, "commit", "-q", "-m", "Initial docs")
    write(repo / "docs/export.md", "# Exporting data\n\nChoose CSV from the Export menu.\n")
    git(repo, "commit", "-qam", "Remove the legacy CSV export option from the export menu")
    write(repo / "docs/views.md", "# Saving a view\n\nSaved views can be shared with your team.\n")
    git(repo, "commit", "-qam", "Saved views can now be shared: update docs/views.md")
    write(repo / "docs/team.md", "# Team workspaces\n\nInvite a member from the Team page.\n")
    git(repo, "commit", "-qam", "wip")
    write(repo / "docs/new.md", "# New page\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "Add a brand new page about printing charts")
    return repo


def test_replay_scores_against_what_was_really_edited(history):
    report = replay(history, ["docs"])
    events = {e["subject"]: e for e in report["events"]}
    assert len(events) == 2
    search = events["Remove the legacy CSV export option from the export menu"]
    assert search["truth"] == ["docs/export"] and search["predicted"][0] == "docs/export" and search["recall"] == 1.0
    named = events["Saved views can now be shared: update docs/views.md"]
    assert named["basis"] == "explicit reference" and named["predicted"] == ["docs/views"]
    assert report["summary"]["overall"]["hit_rate"] == 1.0
    assert sum(report["skipped"].values()) == 2          # "wip" is too short; the last commit only adds a page
    assert "## Overall" in to_markdown(report)


def test_replay_uses_the_docs_as_they_were_before_the_commit(history):
    """The page text after the change must not leak into the search."""
    write(history / "docs/team.md", "# Team workspaces\n\nZebra quokka pangolin onboarding.\n")
    git(history, "commit", "-qam", "Document zebra quokka pangolin onboarding for teams")
    event = replay(history, ["docs"], limit=1)["events"][0]
    assert event["truth"] == ["docs/team"]
    assert "docs/team" not in event["predicted"], "found only because the post-change text leaked in"
