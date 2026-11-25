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

What this says:

- **Hybrid search helps.** Matching on meaning as well as words finds a right
  page for 14 more events out of 80, and it answers every event.
- **The reading step, as first written, is too strict.** It nearly triples
  precision and cuts the list from 8 pages to 3, but it also discards about a
  quarter of the correct pages the search had found. For 9 events it kept
  nothing at all. The judge made 621 calls with no unparsed reply, so this is
  its judgement, not a parsing fault.
- **Why:** the judge sees a commit title and one page, and is told to keep the
  page only if it can point to text the change makes false. Given "V5 docs",
  it cannot, so it drops pages a person did edit.
- **For a human-gated system this is the wrong default.** A missed page costs
  more than an extra candidate the reviewer dismisses. The next version of
  the reading step should keep what it is unsure about and drop only what is
  clearly unrelated.

With 80 events, treat differences of a few points as noise. The gap between
lexical and hybrid search is large enough to take seriously.

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
