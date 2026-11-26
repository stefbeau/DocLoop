# Evaluation: historical replay

The first version of this system measured whether runs completed. It never
measured whether the pages it picked were the right ones. `docloop replay`
closes that gap with data that already exists in every docs repository: its
own history.

## Method

For each past commit that changed documentation:

1. Take the commit message as the change event.
2. Rebuild the docs as they were just before that commit.
3. Ask `find_pages` which pages the change affects (at most 8).
4. Compare with the pages the commit really modified.

Left out: commits that only add new pages (there is nothing to find yet),
bulk edits touching more than 10 pages, and messages shorter than three words.

No model is involved. The replay scores the deterministic first pass that the
lead agent starts from. It is a floor.

```
docloop replay --repo path/to/docs-repo --roots content --report report.md
```

## First result: OpenBB documentation

Run on the public OpenBB docs repository (185 current pages, 179 commits of
history) at commit `692a7bce`. Full table: [benchmarks/openbb-docs-replay.md](benchmarks/openbb-docs-replay.md).

| Measure | Result |
| --- | ---: |
| Commits scored | 80 |
| At least one right page among the candidates | 51% |
| Mean recall of the pages really edited | 40% |
| Right page ranked first | 20 of 80 |
| Every edited page found | 25 of 80 |
| Share of candidates that were right | 15% |

By message length:

| Commit message | Events | Hit rate | Mean recall |
| --- | ---: | ---: | ---: |
| Under 8 words | 47 | 47% | 36% |
| 8 to 30 words | 26 | 65% | 52% |
| Over 30 words | 7 | 29% | 21% |

## Reading the result

- **This is not good enough to act on unreviewed,** and the design never
  assumed it would be. Search candidates are leads. The lead agent reads each
  one and keeps only pages where it can point to the sentence the change makes
  false. One candidate in seven being right means that reading step is doing
  real work.
- **The input is the limit.** Many of these commit messages say "V5 docs",
  "Docs Improvement" or "updating docs". No method can find the page from
  that. Messages of 8 to 30 words score clearly better. Very long messages
  score worst here: they are squash merges that list many unrelated
  sub-commits. Seven events is too few to conclude much from that row.
- **A commit message is a weaker event than the real thing.** In production
  the event is a pull request or ticket with a description and comments. This
  benchmark understates what richer events would give, and it cannot say by
  how much.
- **No event named its pages,** so the explicit-reference rule, which is the
  most reliable path, was never exercised on this corpus.

## Going beyond the first pass

Two options change what is measured. Both need a model, so they need a key.

```
pip install -e ".[agent,vector]"
set HF_TOKEN=hf_...                      (Windows)   export HF_TOKEN=hf_...   (macOS, Linux)

docloop replay --repo ../openbb-docs --roots content content-odp ^
    --search hybrid --embedder hf:BAAI/bge-small-en-v1.5 ^
    --judge-model openai/gpt-oss-120b:fastest --judge-max 20 ^
    --report replay.md --out replay.json
```

- `--search vector` or `hybrid` replaces the word-matching search with an
  embeddings index, or fuses the two rankings. Embedders: `hf:<model>`,
  `openai:<model>`, or `local:<model>` (sentence-transformers, no key).
- `--judge-model` adds the reading step. For each candidate, the model reads
  the page and answers keep or drop, with the sentence it relies on. The
  report then shows hit rate, recall and precision before and after reading.
- `--judge-max N` judges only the newest N events, to try it cheaply first.

Embeddings and verdicts are cached under `.docloop/`, so a rerun costs nothing
for work already done. A reply the judge cannot parse keeps the page and is
counted as unparsed: an unreadable answer must never drop a page silently.

Every report splits the events into an older and a newer half by date. Tune
on the older half. Report the newer half.

### Result on the OpenBB history (25 November 2026)

Same 80 commits, same corpus commit `692a7bce`. Embedder
`BAAI/bge-small-en-v1.5`, judge `openai/gpt-oss-120b`, both through Hugging
Face Inference Providers. Nothing was tuned on these events.

| Setup | Found a right page | Mean recall | Precision | Candidates per event |
| --- | ---: | ---: | ---: | ---: |
| Lexical search | 51% | 40% | 15% | 5.4 |
| Hybrid search | 69% | 51% | 12% | 8.0 |
| Hybrid search, then the reading step | 54% | 37% | 33% | 2.9 |

Newer half only (40 events), the figures to quote:

| Setup | Found a right page | Mean recall | Precision |
| --- | ---: | ---: | ---: |
| Lexical search | 43% | 34% | 17% |
| Hybrid search | 73% | 51% | 14% |
| Hybrid search, then the reading step | 60% | 39% | 38% |

What this says, after looking at every event
([table](benchmarks/openbb-hybrid-reading.md), [data](benchmarks/openbb-hybrid-reading.json)):

- **Hybrid search helps.** Matching on meaning as well as words finds a right
  page for 14 more events out of 80, and it answers every event.
- **The reader carries real signal, and it is noisy.** It keeps 72% of the
  right pages it is shown and discards 69% of the wrong ones. It also makes
  calls that are hard to defend: for "Add missing screenshots" it kept all
  eight candidates, and for "Update excel docs" it dropped the Excel
  installation page and kept a command-line quickstart.
- **Deleting is the wrong use of it.** Letting the reader delete cuts the list
  from 8 pages to 3 and nearly triples precision, at the cost of a quarter of
  the right pages. Against the fair baseline, the top 3 of the search
  ranking, it is ahead overall (54% against 48% hit rate) but behind on the
  older half and ahead on the newer half. On 40 events each, that is not a
  result to lean on.
- **Reordering loses nothing.** Using the same verdicts to put kept pages
  first and the others after them keeps the full list's 69% hit rate and
  moves a right page into the top 3 for 56% of events, up from 48%. That gain
  also comes entirely from the newer half.
- **Message length does not explain the reader's misses.** It keeps about the
  same share of right pages for messages under 8 words (68%) as for longer ones (74%).
- **The ceiling is the search, and the events.** For 25 of the 80 events the
  right page is not among the eight candidates at all. No reading step
  recovers those.

The design consequence: the reading step sorts candidates into "likely" and
"also check", and never removes a page from what the reviewer sees. The
`docs-change-lead` skill now says so.

An earlier version of this page said the reader was simply too strict and
blamed short commit messages. The per-event data does not support either
claim, and both have been removed.

With 80 events, treat differences of a few points as noise. The gap between
lexical and hybrid search is large enough to take seriously. The effect of
the reading step is not yet.

## Second corpus: Hugging Face Hub documentation

The public `huggingface/hub-docs` repository, folders `docs/hub` and
`docs/inference-providers`: 334 pages, the 300 most recent docs commits.
This measures DocLoop's search. It says nothing about the quality of the
documentation itself.

### Automated commits have to be left out

Of 284 scorable commits, 98 are titled "Update Inference Providers
documentation (automated)" and touch five pages each on average. The title
names nothing, so no search can map it: the hit rate on those 98 is 0%. They
are not change descriptions, and including them measures the commit bot, not
the search. `--skip-message` leaves them out.

| Lexical search, corpus at `2c3f84c8` | Events | Found a right page | Mean recall | Precision |
| --- | ---: | ---: | ---: | ---: |
| Every commit | 284 | 49% | 41% | 22% |
| Human-written commits only | 186 | 75% | 65% | 32% |

Full table for the second row: [benchmarks/hub-docs-replay.md](benchmarks/hub-docs-replay.md).

When a person describes the change in a sentence, plain word matching finds a
right page three times out of four. The OpenBB figure of 51% reflects its
commit messages more than the method.

### Pages named in the message are not the whole answer

20 of the 186 messages name a page. A named page was among the edited ones in
90% of cases, but the named pages covered only 52% of what was edited. The
first version of this tool stopped at the named pages, a rule inherited from
the pipeline it replaces, where it guarded against invented page ids. The
tools now refuse invented ids on their own, so the rule was costing recall
for nothing. Named pages now come first and search fills the remaining
places: on those 20 events, hit rate goes from 90% to 95% and recall from 52%
to 68%.

### Hybrid search and the reading step (maintainer's run, 25 November 2026)

Run on all 284 commits, automated ones included, so the hybrid figure is not
comparable with the 75% above. A rerun on human-written commits is the next
measurement.

| All 284 commits | Found a right page | Mean recall |
| --- | ---: | ---: |
| Lexical search | 49% | 41% |
| Hybrid search | 57% | 51% |

Reading step on the 60 newest of those commits, judge `openai/gpt-oss-120b`,
380 calls, no unparsed reply:

| | Found a right page | Mean recall | Precision | Pages |
| --- | ---: | ---: | ---: | ---: |
| Hybrid search, all candidates | 70% | 63% | 15% | 7.7 |
| Top 2 of the search ranking | 63% | 50% | 38% | 2 |
| Reader deletes what it does not keep | 60% | 52% | 40% | 2.4 |
| Reader reorders, top 3 | 70% | 58% | 31% | 3 |
| Search ranking, top 3 | 65% | 54% | 29% | 3 |

The reader separates right from wrong better here than on OpenBB (it keeps
80% of right pages and drops 77% of wrong ones), and the conclusion is the
same on both corpora:

- Used to delete, it is no better than cutting the search ranking to the
  same length.
- Used to reorder, it gains a few points in the top 3, and on both corpora
  that gain appears in the newer half of the events and not in the older half.

A model reading one page at a time against a one-line description adds little
to the ranking. Where the model earns its place is elsewhere: drafting the
edit, and reading with the freedom to search again.

## What this benchmark is for

It gives a number to move. Changes worth testing against it, in order:

1. A vector index behind `impact.search`, to match on meaning and not only on
   shared words.
2. The agent's reading step, scored the same way: of the candidates, which
   does the model keep, and is recall preserved while precision rises?
3. Richer events: pull request descriptions in place of commit titles.

Report every change against the same commit of the same corpus. Do not tune
on the events you report on: split the history by date, tune on the older
part, and report on the newer part.

## Origin

The replay idea and the page registry come from `docdrift`, an earlier
prototype of this project that planned the same evaluation on the same corpus.


## Release R1: accuracy targets (in progress)

The targets, the four corpora and the rules were written down before any R1
measurement: [r1-preregistration.md](r1-preregistration.md). Hybrid search is now
the default, and the reading step sorts candidates into "likely" and "also
check" instead of deleting any.

What is measured so far, with no model (word search, pass 1):

| Corpus | Events | Hit rate, newer half | Recall, newer half | Report |
| --- | ---: | ---: | ---: | --- |
| Prometheus docs | 273 | 83% | 81% | [table](benchmarks/prometheus-docs-replay.md) |
| GOV.UK service manual (2016) | 260 | 49% | 47% | [table](benchmarks/service-manual-replay.md) |

The saved OpenBB run, rescored with the registered measures and no new model
calls, misses every R1 target on its newer half (hit rate 73%, recall 51%,
precision of the likely list 38%). The reading pass does help there: the share
of events with a right page in the top 3 rises from 43% to 60%.

Hybrid search and reading on all four corpora run in the `r1-benchmark`
workflow, which needs the repository secret `HF_TOKEN`. Its results are written
to a new branch and then reviewed; a missed target is published as a miss.

To run one corpus yourself: `python -m docloop.r1 run --corpus prometheus --workdir work --out out`
(needs `HF_TOKEN`), then `python -m docloop.r1 summarize --in out --out docs/benchmarks/r1`.
