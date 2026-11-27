import urllib.error

from docloop import action

PR = {"pull_request": {"number": 7, "title": "Retire the legacy CSV export",
                       "body": "The legacy CSV export option will be removed. Use the Export menu.",
                       "labels": [{"name": "deprecation"}]}}


class FakeApi:
    def __init__(self, files=("src/export.py",), comments=(), fail_post=False):
        self.files, self.comments, self.fail_post, self.calls = list(files), list(comments), fail_post, []

    def call(self, method, path, data=None):
        self.calls.append((method, path, data))
        if method == "GET" and "/files" in path:
            return [{"filename": f} for f in self.files]
        if method == "GET":
            return self.comments
        if self.fail_post:
            raise urllib.error.URLError("403 read-only token")
        return {}


def test_event_includes_changed_files_and_labels():
    ev = action.event_from_pull_request(PR, ["src/export.py"])
    assert ev.id == "pr-7" and ev.labels == ["deprecation"] and "src/export.py" in ev.body


def test_docs_only_detection():
    assert action.touches_only_docs(["docs/a.md", "docs/b/c.md"], "docs")
    assert not action.touches_only_docs(["docs/a.md", "src/x.py"], "docs")
    assert not action.touches_only_docs([], "docs")


def test_comment_is_created_with_real_pages_only(tmp_path):
    (tmp_path / "export.md").write_text("# Export data\nUse the legacy CSV export option.\n", encoding="utf-8")
    (tmp_path / "billing.md").write_text("# Billing\nInvoices and payment methods.\n", encoding="utf-8")
    api = FakeApi()
    assert action.run(PR, str(tmp_path), "o/r", api) == 0
    method, path, data = [c for c in api.calls if c[0] == "POST"][0]
    assert path == "/repos/o/r/issues/7/comments"
    assert action.MARKER in data["body"] and "`export`" in data["body"] and "billing" not in data["body"]
    assert "Nothing was written" in data["body"]


def test_existing_comment_is_updated_not_duplicated(tmp_path):
    (tmp_path / "export.md").write_text("# Export\nlegacy CSV export\n", encoding="utf-8")
    api = FakeApi(comments=[{"id": 99, "body": action.MARKER + " old"}])
    action.run(PR, str(tmp_path), "o/r", api)
    assert [c[0] for c in api.calls if c[0] != "GET"] == ["PATCH"]
    assert api.calls[-1][1] == "/repos/o/r/issues/comments/99"


def test_docs_only_pr_gets_no_comment(tmp_path):
    (tmp_path / "export.md").write_text("# Export\n", encoding="utf-8")
    api = FakeApi(files=["docs/export.md"])
    action.run(PR, "docs", "o/r", api)
    assert not [c for c in api.calls if c[0] in ("POST", "PATCH")]


def test_read_only_token_falls_back_to_summary_and_does_not_fail(tmp_path):
    (tmp_path / "export.md").write_text("# Export\nlegacy CSV export option\n", encoding="utf-8")
    summary = tmp_path / "summary.md"
    code = action.run(PR, str(tmp_path), "o/r", FakeApi(fail_post=True), summary_path=str(summary), log=lambda m: None)
    assert code == 0 and action.MARKER in summary.read_text(encoding="utf-8")


def test_no_match_says_so_and_does_not_invent_pages(tmp_path):
    (tmp_path / "billing.md").write_text("# Billing\nInvoices only.\n", encoding="utf-8")
    pr = {"pull_request": {"number": 8, "title": "Bump lint config", "body": "", "labels": []}}
    api = FakeApi(files=["setup.cfg"])
    action.run(pr, str(tmp_path), "o/r", api)
    body = [c for c in api.calls if c[0] == "POST"][0][2]["body"]
    assert "No page in the docs looks affected" in body and "`billing`" not in body


def test_non_pull_request_event_is_a_noop(tmp_path):
    assert action.run({"push": {}}, str(tmp_path), "o/r", FakeApi(), log=lambda m: None) == 0
