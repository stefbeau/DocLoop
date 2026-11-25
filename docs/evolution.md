# From a seven-agent pipeline to one lead agent

This project is the second version of an idea. The first version ran in
production-like conditions at a large B2B data company in 2026. This page
records what the first version was, what it taught, and how each lesson shaped
the design here.

## The problem, unchanged

When an AI assistant answers from your documentation, a stale page is bad
data. Every product change opens a gap between what the product does and what
the docs say, and nothing closes that gap unless a writer notices.

## Version 1: a pipeline of seven agents

```
change request
   │
00 Orchestrator ── routes
01 Intake ──────── reads the request, extracts a change object
02 Impact ──────── finds the affected pages
03 Content prep ── drafts the edits
   ✋ writer approves
04 Notice ──────── drafts the customer notice
05 Health ──────── scans the corpus (asynchronous)
06 Governance ──── scores readiness, writes the audit record
```

Seven standing agents, each with its own prompt, wired agent to agent on an
internal agent platform. It won the company hackathon out of 485 projects and
was used by nine people.

It also taught seven lessons the hard way.

| What failed | What it cost |
| --- | --- |
| The impact agent invented page ids when it could not reach the registry | Eight pages proposed where one existed |
| Every agent forwarded its whole output to the next | 165k tokens for one run |
| Routing was done by a model reading long instructions | More than 64 orchestrator prompt versions to make it reliable |
| Prompts lived on the platform and in local files | A day lost debugging agents that were running stale prompts |
| Intake read the form and not the comments | A real request misclassified |
| Seven agents grew to 21 as cases accumulated | One builder was the only person who understood all of it |
| Completion was measured, correctness was not | No labelled set to prove page mapping was right |

By the end of the year the first version had already drifted away from its own
design: routing had become a lookup table, intake had become rule-based
detectors, and most agents had become thin wrappers around tools. The agents
were no longer where the value was.

## Version 2: one lead agent, a skill library, tools, a gate

```
change event
   │
Lead agent ── holds the whole context, follows the docs-change-lead skill
   │   ├─ classify_event ...... tool, rule-based, shows its evidence
   │   ├─ route_event ......... tool, lookup table
   │   ├─ find_affected_pages . tool, real ids only
   │   ├─ load_skill .......... instructions on demand
   │   ├─ delegate ............ subagent with a clean context, one page per brief
   │   └─ propose_edit / propose_notice ... proposals, never writes
   ✋ a named person runs: approve, then apply
```

| Version 1 | Version 2 | Why |
| --- | --- | --- |
| Seven standing agents | One lead agent; subagents created per task | Subtasks are decided at run time, so a fixed roster either over-serves or under-serves each event |
| Knowledge in seven prompts | Knowledge in six skills, loaded on demand | A skill is a document: reviewable, versioned, portable across runtimes |
| Routing by a model | `route_event`, a table | A decision with five outcomes does not need judgement |
| "Never invent a page id", as a prompt rule | `propose_edit` rejects any id the store does not hold | A rule in a prompt can be ignored. A rule in a tool cannot |
| Gate between two agents | No write tool exists; `approve` and `apply` are human commands | The gate stops depending on the agents behaving |
| Each agent forwards its output | A subagent returns a six-line report | The lead keeps the context; the detail stays in the proposal files |
| Built for one platform | One core, three runtimes | The platform is the part most likely to change |
| Built for one content system | A page store interface with two adapters | Docs live in Git for some teams and in a CMS for others |
| Health scan inside every run | `corpus_census`, a separate tool and skill | It answers a different question, on a different schedule |

## What stayed the same

- **A person approves every change.** In version 2 this is stricter, not
  looser: writes are single-threaded and refused if the page changed after
  the proposal.
- **Deterministic first.** If a script can decide it, a model does not.
- **Everything is logged.** Every tool call that changes state appends to an
  audit log.

## What version 2 does not prove yet

- **Model quality.** The test suite exercises the tools, the gate, the loop
  and the delegation with a scripted model. Draft quality depends on the
  model you connect and has not been benchmarked here.
- **Page-mapping accuracy beyond the first pass.** `docloop replay` now scores
  the deterministic search against real history ([results](evaluation.md)):
  51% hit rate and 40% recall on 80 commits of a public docs repository. The
  agent's reading step, which filters those candidates, is not scored yet.
- **Scale.** Search is a small lexical index. Beyond a few thousand pages,
  plug a vector index in behind `impact.search`.
