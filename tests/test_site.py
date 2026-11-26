"""The public site: every figure shown comes from a replay report, pages exist, internal links resolve, text is readable on a phone."""
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("markdown")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site_src"))
import build as site  # noqa: E402


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    d = tmp_path_factory.mktemp("site")
    site.build(d)
    return d


def test_figures_are_read_from_the_reports_not_typed():
    f = site.figures()
    assert f["hub"] == {"events": 186, "hit": 75, "recall": 65, "answered": 180, "precision": 32, "commit": "2c3f84c8"}   # the committed report, as published
    src = (ROOT / "site_src" / "build.py").read_text(encoding="utf-8")
    body = src[src.index("def home"):src.index("def render_markdown")]
    assert not re.search(r"\b(75|65|32|51|69|40|15|12|186|80)\s?%", body), "a benchmark figure is typed into the page instead of read from its report"


def test_home_shows_the_report_figures_and_the_caveat(out):
    html = (out / "index.html").read_text(encoding="utf-8")
    f = site.figures()
    assert f'<b>{f["hub"]["hit"]}%</b>' in html and f'{f["openbb"]["hit"]}% to {f["openbb_hybrid"]["hit"]}%' in html
    assert "a floor, not a result" in html and f'{f["hub"]["precision"]}% and {f["openbb"]["precision"]}%' in html   # low precision is stated next to the headline figures
    assert "named person" in html


def test_reproduce_page_has_the_exact_recipe(out):
    html = (out / "reproduce.html").read_text(encoding="utf-8")
    f = site.figures()["hub"]
    assert f"checkout {f['commit']}" in html and "--limit 300" in html and "--skip-message" in html and "--demo" in html
    assert f"<td>{f['events']}</td><td>{f['hit']}%</td><td>{f['recall']}%</td><td>{f['precision']}%</td>" in html


def test_all_pages_exist_and_internal_links_resolve(out):
    names = {p.name for p in out.glob("*.html")}
    assert {"index.html", "reproduce.html", "method.html", "benchmarks.html", "evolution.html", "adapters.html", "benchmark-hub.html",
            "benchmark-openbb.html", "benchmark-openbb-hybrid.html"} <= names
    for p in out.glob("*.html"):
        for href in re.findall(r'href="([^"]+)"', p.read_text(encoding="utf-8")):
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            assert (out / href.split("#")[0]).exists(), f"{p.name}: broken link {href}"


def test_readable_on_a_phone(out):
    css = (out / "style.css").read_text(encoding="utf-8")
    assert "html{font-size:17px}" in css
    for size in re.findall(r"font-size:\.(\d+)rem", css):
        assert float("0." + size) * 17 >= 14, f"text smaller than 14 px: .{size}rem"
    for p in out.glob("*.html"):
        assert 'name="viewport"' in p.read_text(encoding="utf-8")
