"""Build the public site into a folder (default _site/). Nothing built is committed.

Every figure on the home page is read from the replay reports in docs/benchmarks/, never typed here: if a report changes,
the site changes with it, and tests/test_site.py fails if the two disagree.

    pip install markdown
    python site_src/build.py [out_dir]
"""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPO_URL = "https://github.com/stefbeau/DocLoop"

#: (key, label, corpus line, report file). The label says what was run; the numbers come from the file.
REPORTS = [
    ("hub", "Hugging Face Hub docs", "186 human-written changes, word-matching search", "benchmarks/hub-docs-replay.md"),
    ("openbb", "OpenBB docs", "80 changes, word-matching search", "benchmarks/openbb-docs-replay.md"),
    ("openbb_hybrid", "OpenBB docs, hybrid search", "80 changes, words and meaning", "benchmarks/openbb-hybrid-reading.md"),
]
PAGES = [  # (output, source markdown, nav label, title)
    ("method.html", "evaluation.md", "Method", "How accuracy is measured"),
    ("evolution.html", "evolution.md", "Evolution", "From seven agents to one"),
    ("adapters.html", "adapters.md", "Adapters", "Where your docs live"),
    ("benchmark-hub.html", "benchmarks/hub-docs-replay.md", None, "Replay report: Hugging Face Hub docs"),
    ("benchmark-openbb.html", "benchmarks/openbb-docs-replay.md", None, "Replay report: OpenBB docs"),
    ("benchmark-openbb-hybrid.html", "benchmarks/openbb-hybrid-reading.md", None, "Replay report: OpenBB docs, hybrid search and reading step"),
]
NAV = [("index.html", "Home"), ("reproduce.html", "Reproduce"), ("method.html", "Method"), ("benchmarks.html", "Benchmarks"),
       ("evolution.html", "Evolution"), ("adapters.html", "Adapters")]
LINKS = {"evaluation.md": "method.html", "evolution.md": "evolution.html", "adapters.md": "adapters.html",
         "benchmarks/hub-docs-replay.md": "benchmark-hub.html", "benchmarks/openbb-docs-replay.md": "benchmark-openbb.html",
         "benchmarks/openbb-hybrid-reading.md": "benchmark-openbb-hybrid.html", "hub-docs-replay.md": "benchmark-hub.html",
         "openbb-docs-replay.md": "benchmark-openbb.html", "openbb-hybrid-reading.md": "benchmark-openbb-hybrid.html"}


def overall(report: str) -> dict:
    """The 'All scored events' row of a replay report: events, hit rate, mean recall, precision when answered (percent, as printed)."""
    text = (DOCS / report).read_text(encoding="utf-8")
    m = re.search(r"^\| All scored events \| (\d+) \| (\d+)% \| (\d+)% \| ([\d.]+) \| (\d+) \| (\d+)% \|", text, re.M)
    if not m:
        raise ValueError(f"no 'All scored events' row in {report}")
    corpus = re.search(r"Corpus at `([0-9a-f]+)`", text)
    return {"events": int(m.group(1)), "hit": int(m.group(2)), "recall": int(m.group(3)), "answered": int(m.group(5)),
            "precision": int(m.group(6)), "commit": corpus.group(1) if corpus else ""}


def figures() -> dict:
    return {key: overall(path) for key, _, _, path in REPORTS}


def page(name: str, title: str, body: str) -> str:
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == name else ""}>{html.escape(t)}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · DocLoop</title>
<meta name="description" content="DocLoop keeps documentation in step with product changes: an agent proposes, a named person approves. Open source, with benchmarks anyone can re-run.">
<link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="brand" href="index.html">DocLoop</a><nav aria-label="Main">{nav}</nav></header>
<main id="main">{body}</main>
<footer><p>Open source under Apache 2.0. <a href="{REPO_URL}">Source on GitHub</a>. Every figure on this site comes from a report in the repository and can be re-run.</p></footer>
</body></html>
"""


def bar(label: str, value: int, strong: bool = False) -> str:
    return (f'<div class="bar{" strong" if strong else ""}"><span class="bl">{html.escape(label)}</span>'
            f'<span class="bt" role="img" aria-label="{value} percent"><span class="bf" style="width:{value}%"></span></span><span class="bv">{value}%</span></div>')


def home(f: dict) -> str:
    hub, ob, obh = f["hub"], f["openbb"], f["openbb_hybrid"]
    rows = ""
    for key, label, corpus, _ in REPORTS:
        d = f[key]
        rows += (f'<section class="corpus"><h3>{html.escape(label)}</h3><p class="sub">{html.escape(corpus)}; docs at commit <code>{d["commit"]}</code></p>'
                 + bar("Found a right page", d["hit"], True) + bar("Share of right pages found", d["recall"]) + bar("Candidates that were right", d["precision"]) + "</section>")
    return f"""
<section class="hero"><h1>Keep your documentation in step with your product</h1>
<p class="lead">DocLoop takes a product change, works out which pages it affects, drafts the edits and the customer notice, and stops. A named person approves before anything is written.</p>
<p class="cta"><a class="btn" href="reproduce.html">Try it in one minute</a> <a class="btn ghost" href="{REPO_URL}">Source on GitHub</a></p></section>

<section aria-labelledby="k"><h2 id="k">What is measured today</h2>
<div class="tiles">
<div class="tile"><b>{hub["hit"]}%</b><span>of {hub["events"]} human-written changes to the Hugging Face Hub docs: a right page is among the candidates</span></div>
<div class="tile"><b>{ob["hit"]}% to {obh["hit"]}%</b><span>on the OpenBB docs ({ob["events"]} changes), when search matches on meaning as well as words</span></div>
<div class="tile"><b>0</b><span>pages written without a named person's approval: the write commands are never given to a model</span></div>
</div>
<p class="note"><strong>Read these as a floor, not a result.</strong> They score the first, model-free pass on past commits. Precision is low: only {hub["precision"]}% and {ob["precision"]}% of the candidates were pages that really changed. The next release is about raising these numbers, and misses will be published here too.</p></section>

<section aria-labelledby="b"><h2 id="b">Finding the affected pages: where it stands</h2>
<p>For each past change, DocLoop rebuilds the docs as they were, proposes at most 8 pages, and is scored against the pages that were really edited. <a href="method.html">How this is measured</a>.</p>
<div class="corpora">{rows}</div>
<p><a href="benchmarks.html">Full reports, every scored change</a> · <a href="reproduce.html">Re-run them yourself</a></p></section>

<section aria-labelledby="h"><h2 id="h">How it works</h2>
<div class="cols">
<div><h3>Skills</h3><p>What the agent knows. Six plain Markdown procedures, loaded on demand. You adapt DocLoop to your house style by editing them.</p></div>
<div><h3>Tools</h3><p>What the agent can do. Classify, route, search, read, propose. None of them calls a model and none of them writes to your docs.</p></div>
<div><h3>The gate</h3><p>What only a person does. <code>approve</code> records who approved. <code>apply</code> writes the approved pages and refuses any page that changed meanwhile.</p></div>
</div>
<p>It reads Markdown in Git or a content system through one adapter, and runs under Claude Code, as a standalone Python loop with any compatible model, or with smolagents. <a href="evolution.html">Why one lead agent replaced a seven-agent pipeline</a>.</p></section>

<section aria-labelledby="q"><h2 id="q">Quality in passes</h2>
<p>Not every page deserves the same effort. DocLoop is being built to escalate: pages named in the change, then word search, then search by meaning, then a model reading each candidate, then a second check of each drafted edit, with more passes for riskier content such as legal, pricing or API reference pages. Each pass has to show a measured gain to stay. Today the first three passes exist and the reading pass is experimental.</p></section>
"""


def reproduce(f: dict) -> str:
    hub = f["hub"]
    return f"""
<h1>Try it, then check our numbers</h1>
<p class="lead">Two things you can do from a clean clone, with no account and no API key.</p>
<h2>1. Watch the loop in one minute</h2>
<pre><code>git clone {REPO_URL} &amp;&amp; cd DocLoop
pip install -e .

python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --demo
docloop --docs examples/docs status  retire-csv
docloop --docs examples/docs approve retire-csv --reviewer "Your Name"
docloop --docs examples/docs apply   retire-csv
git diff examples/docs</code></pre>
<p>The <code>--demo</code> run replays a fixed script in place of a model. You see the lead agent classify the change, route it, hand one page to a subagent, draft the notice and stop at the gate. Nothing is written until you run <code>approve</code> and <code>apply</code>.</p>
<h2>2. Reproduce a published figure</h2>
<p>The {hub["hit"]}% on the home page comes from the public Hugging Face Hub documentation history. This re-runs it:</p>
<pre><code>git clone https://github.com/huggingface/hub-docs
git -C hub-docs checkout {hub["commit"]}

docloop replay --repo hub-docs --roots docs/hub docs/inference-providers \\
  --limit 300 --skip-message "\\(automated\\)" --report report.md</code></pre>
<p>You should get this first table in <code>report.md</code>:</p>
<div class="tw"><table><thead><tr><th>Events</th><th>Hit rate</th><th>Mean recall</th><th>Precision when answered</th></tr></thead>
<tbody><tr><td>{hub["events"]}</td><td>{hub["hit"]}%</td><td>{hub["recall"]}%</td><td>{hub["precision"]}%</td></tr></tbody></table></div>
<p class="note"><strong>Checked on 26 November 2026.</strong> From a clean install, the command above gave the same table in about 50 seconds on a Linux machine. No model is involved, so the result does not depend on a provider. If you get something else, <a href="{REPO_URL}/issues">open an issue</a>: that is a bug in the claim.</p>
<p>On Windows Command Prompt, write the replay command on one line: remove the backslash at the end of the first line and join the two lines.</p>
"""


def benchmarks(f: dict) -> str:
    rows = "".join(f'<tr><td><a href="{LINKS[path]}">{html.escape(label)}</a><br><span class="sub">{html.escape(corpus)}</span></td><td>{f[key]["events"]}</td>'
                   f'<td>{f[key]["hit"]}%</td><td>{f[key]["recall"]}%</td><td>{f[key]["precision"]}%</td></tr>' for key, label, corpus, path in REPORTS)
    return f"""<h1>Benchmarks</h1>
<p class="lead">Three replay reports on two public documentation histories. Each links to every scored change.</p>
<div class="tw"><table><thead><tr><th>Report</th><th>Events</th><th>Found a right page</th><th>Mean recall</th><th>Precision when answered</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Figures are per corpus and are not averaged. Two corpora are not enough to call a figure general. A model reading the candidates raised precision on OpenBB but lost right pages when it was allowed to drop them, so it now only sorts. <a href="method.html">Method and limits</a>.</p>"""


def render_markdown(src: str) -> str:
    import markdown
    text = (DOCS / src).read_text(encoding="utf-8")
    out = markdown.markdown(text, extensions=["tables", "fenced_code"])
    out = re.sub(r'href="(?!https?://|#|mailto:)([^"#]+\.md)(#[^"]*)?"', lambda m: f'href="{LINKS.get(m.group(1).replace("../", ""), REPO_URL + "/blob/main/docs/" + m.group(1))}{m.group(2) or ""}"', out)
    out = re.sub(r'href="(?!https?://|#|mailto:)(\.\./)?([^"#]+)"', lambda m: m.group(0) if m.group(2).endswith(".html") else f'href="{REPO_URL}/blob/main/{m.group(2)}"', out)
    return out.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    f = figures()
    (out / "style.css").write_text((Path(__file__).parent / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    (out / "index.html").write_text(page("index.html", "Documentation that keeps up with the product", home(f)), encoding="utf-8")
    (out / "reproduce.html").write_text(page("reproduce.html", "Reproduce", reproduce(f)), encoding="utf-8")
    (out / "benchmarks.html").write_text(page("benchmarks.html", "Benchmarks", benchmarks(f)), encoding="utf-8")
    for name, src, _, title in PAGES:
        (out / name).write_text(page(name, title, '<article class="doc">' + render_markdown(src) + "</article>"), encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    build(target)
    print(f"built {len(list(target.glob('*.html')))} pages in {target}")
