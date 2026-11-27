# R1 pre-registration: accuracy

Written on 26 November 2026, before any R1 measurement and before the R1 code. It is committed ahead of the code and the tests that check it. A missed target is recorded as a miss. It is never moved.

## What is registered

Targets come unchanged from the product specification (section "Quality targets").

| Measure | Target | Measured on |
| --- | ---: | --- |
| Hit rate (a right page among the candidates) | 90% | full candidate list, at most 8 pages |
| Mean recall of affected pages | 80% | full candidate list |
| Precision when it answers | 60% | the "likely" list (see the choice below) |
| Right pages placed in "likely" | 95% | pass 3 |
| Wrong pages placed in "also check" | 85% | pass 3 |

Each target is judged **per corpus, on the newer half by date**. Figures are never averaged across corpora. R1 passes only if every corpus meets every target; otherwise the misses are published, corpus by corpus.

## Choice made before the data: which list precision is measured on

The baselines in the specification (32% and 15%) were measured on the full list of up to 8 pages. With about two right pages per change, a list of 8 cannot reach 60% precision. Pass 3 splits the list into "likely" and "also check", and the reviewer is sent the "likely" pages first. So the primary precision target applies to the "likely" list.

The literal reading, precision of the full list against 60%, is reported next to it in every table, with the same target. It is expected to be missed. This choice is a proposal for the editor to confirm or reverse; it is recorded here so that it was made before the numbers existed.

## Corpora

Fixed now. A corpus is not added or dropped after its figures are seen.

| Corpus | Kind | Folders | Licence of the source | Note |
| --- | --- | --- | --- | --- |
| Hugging Face Hub docs | technical | `docs/hub`, `docs/inference-providers` | Apache 2.0 | already reported (186 events) |
| OpenBB docs | technical | `content`, `content-odp` | not yet checked: recorded in the R1 report before the figures are used | already reported (80 events) |
| Prometheus docs | technical | `docs` | Apache 2.0 | new in R1 |
| GOV.UK service manual (archived 2016) | non-technical guidance | `service-manual` | Open Government Licence | new in R1; old history, labelled as such |

Only variable names, page ids and error figures are stored from these corpora, never their text.

Events are scored with the existing replay rules (message of at least 3 words, at most 10 pages modified, existing pages only, automated commits skipped). A corpus with fewer than 60 scored events has its figures reported but is not counted as meeting or missing a target: it is reported as "too few events".

## What is fixed before the first R1 run

- Search: hybrid, `hf:BAAI/bge-small-en-v1.5`, up to 8 candidates, the lexical settings unchanged (`MIN_SCORE`, BM25 constants).
- Reader (pass 3): `openai/gpt-oss-120b:fastest`, temperature 0, the instructions in `docloop/judge.py` as committed with this file. The reader sorts, it never deletes: a page it does not keep goes to "also check". An unreadable reply puts the page in "likely".
- No parameter, prompt or threshold is changed after the first R1 run on a corpus. There is no tuning step in R1. If a later release tunes, it is labelled as tuned on the older half and reported on the newer half.

## Honest limits, stated in advance

- The Hub and OpenBB newer halves were already seen in earlier reports (no tuning was done on them, but they are not fresh). The two new corpora are first-look for the newer half.
- The replay scores commit messages against edited pages. This is a floor for the deterministic first pass plus reading, and a proxy for real change events. The non-technical corpus is old (2016) and its commit style may differ from current practice.
- Reader results depend on one model on one date. The model name and call counts are stored with each report.

## Rule for keeping a pass

Each pass must show a measured gain on the replay benchmark for the content it is used on, or it is removed (specification, "Rules for the method"). Fixed now:

- A pass is **kept for a corpus** if, on the newer half, it raises the share of events with a right page in the top 3 by at least 2 points, or the mean reciprocal rank by at least 0.02.
- Pass 2 (hybrid) is compared with pass 1 (words only). Pass 3 (reading) is compared with the list in search order.
- A pass kept on fewer than three of the four corpora is published as "corpus-dependent", with the corpora where it helped and where it did not.

## Amendment 1 (26 November 2026, before any R1 model run)

Made after looking at commit subjects of the two new corpora, and at the word-search figures of none. It fixes the settings the specification left open; it changes no target.

- Every corpus is replayed at a pinned commit, with `--limit 300` (newest 300 commits touching the folders), at most 10 pages modified, existing replay filters. The pins, folders and the one skip rule (`(automated)` on the Hub corpus) are in `benchmarks/r1-corpora.json`.
- OpenBB docs are replayed from `OpenBB-finance/openbb-docs`, the repository whose head `692a7bce` the earlier report used.
- The GOV.UK service manual has many commits whose message is just "update <file>.md". Those name the page, so they are easy for the first pass. They are kept, and the corpus is labelled with this.
- Prometheus docs has only about 280 commits under `docs`, so fewer than 300 events will be scored; the 60-event floor applies.
- A hybrid run that silently fell back to word search is invalid: the benchmark stops with an error instead of reporting it.
- Real cost: the reader makes up to 8 model calls per scored event, on the account that owns the `HF_TOKEN` secret.
