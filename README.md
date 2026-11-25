# docloop

Keep documentation in step with product changes: one lead agent, a skill
library, deterministic tools, and a human gate.

When an AI assistant answers from your docs, a stale page is bad data.
`docloop` takes a product change (a pull request, an issue, a release note, a
ticket), works out which pages it affects, drafts the edits and the customer
notice, and stops. A named person approves before anything is written.

This is the second version of a system that first ran as a seven-agent
pipeline. [What changed and why](docs/evolution.md).

## Try it in one minute, with no API key

```
git clone https://github.com/stefbeau/DocLoop && cd DocLoop
pip install -e .

docloop --docs examples/docs classify examples/events/retire-csv.json
docloop --docs examples/docs route    examples/events/retire-csv.json
docloop --docs examples/docs impact   examples/events/retire-csv.json

python -m docloop.agent examples/events/retire-csv.json --docs examples/docs --demo
docloop --docs examples/docs status  retire-csv
docloop --docs examples/docs approve retire-csv --reviewer "Your Name"
docloop --docs examples/docs apply   retire-csv
git diff examples/docs
```

The `--demo` run replays a fixed script in place of a model, so you can watch
the lead agent classify, route, delegate one page to a subagent, draft the
notice and stop at the gate.

## How it is put together

```
skills/      what the agent knows     six SKILL.md files, loaded on demand
docloop/     what the agent can do    deterministic tools, no model calls
runtimes/    what runs the agent      three thin front ends over the same core
```

### The core: tools an agent may call

| Tool | What it does | Uses a model |
| --- | --- | --- |
| `classify_event` | Rule-based detectors over the event text and comments, with evidence | No |
| `route_event` | Lookup table: which steps run, or hand to a person | No |
| `find_affected_pages` | Pages named in the event, else a capped search. Real ids only | No |
| `search_pages`, `read_page` | Look things up | No |
| `propose_edit` | Saves a proposed page body, a diff and lint results. Writes nothing | No |
| `propose_notice` | Saves a customer notice draft with lint results. Sends nothing | No |
| `review_status` | Readiness score with its breakdown | No |
| `corpus_census` | Compares the docs with a search index: blind spots, ghosts, wrong visibility | No |

### The gate: commands only a person runs

`docloop approve` records who approved. `docloop apply` writes the approved
proposals, one page at a time, and refuses any page that changed since it was
proposed. Neither is ever registered as a model tool, in any runtime.

### The skill library

| Skill | Use |
| --- | --- |
| `docs-change-lead` | The lead procedure: classify, route, find, draft or delegate, report, stop |
| `impact-mapping` | Deciding which search candidates a change really affects |
| `drafting-doc-edits` | Minimal, reviewable edits to one page |
| `customer-notice` | Drafting the notice |
| `review-rules` | House rules that need judgement, by severity |
| `corpus-census` | Auditing what an assistant can retrieve |

Skills are plain Markdown in the open Agent Skills layout. Edit them to match
your house style. That is the main way to adapt `docloop` to your organisation.

### Three runtimes, one core

| Runtime | What it is | Status |
| --- | --- | --- |
| [Claude Code](runtimes/claude-code/) | Skills, one subagent, an MCP server, and a rule that blocks direct edits to the docs | MCP server tested; full session not run in the test suite |
| [Standalone Python](runtimes/standalone/) | A tool-calling loop for any OpenAI-compatible endpoint, with delegation | Loop, delegation and gate tested with a scripted model |
| [smolagents](runtimes/smolagents/) | Lead agent plus a managed agent, with a Gradio UI ready for a Hugging Face Space | Agents and tools constructed in tests; full run needs a model |

### Where your docs live

Markdown in Git (`.md` and `.mdx`) and CMS exports both work through one
interface. For Git, you can limit the scan to some folders and exclude
archived ones (`DOCLOOP_ROOTS`, `DOCLOOP_EXCLUDE`), and `docloop registry`
lists every page with its hash, tied to the corpus commit. See
[adapters](docs/adapters.md) to connect a live content system.

## Measured, not assumed

`docloop replay` scores page mapping against the real history of a docs
repository: for each past commit, it rebuilds the docs as they were, asks
which pages the change affects, and compares with the pages that were really
edited.

```
docloop replay --repo path/to/docs-repo --roots content --report report.md
```

On the public OpenBB docs history (80 scored commits), word-matching search
puts at least one right page among its candidates 51% of the time. Hybrid
search, which also matches on meaning, raises that to 69%. A first version of
the model reading step tripled precision but threw away a quarter of the right
pages, which is the wrong trade for a human-gated system and is being
reworked. [Method, full results and what they mean](docs/evaluation.md).

## Tests

```
pip install -e ".[dev,mcp,smolagents]"
pytest
```

55 tests cover the detectors, routing, search, both page stores, the gate
(including stale pages and proposals changed after approval), the audit log,
the agent loop, the replay, vector and hybrid search, the reading-step
judge, and the construction of all three runtimes.

## What this does not do yet

- It has no benchmark of draft quality, and the page-mapping benchmark covers
  the deterministic first pass only, not the agent's reading step.
- Search is lexical by default. Hybrid search (`DOCLOOP_SEARCH=hybrid`,
  `DOCLOOP_EMBEDDER`) scores better on the one corpus benchmarked so far.
- It does not fetch pull requests or tickets. You give it a change event file.

## Licence

Apache 2.0.
