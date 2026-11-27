# R2 pre-registration: what the reader sees

Written on 27 November 2026, before any R2 measurement. It follows the R1 rules: a miss is recorded as a miss and a target is never moved.

## The question

In R1, the reading pass sends the model the first 6,000 characters of each candidate page. On the saved OpenBB and Prometheus analyses, the right pages that the reader pushed down were much longer than the ones it kept. That is a clue, not a proof: the service manual showed no such effect.

## The change (and only this change)

`Judge(excerpt="relevant")` sends, for a page longer than 6,000 characters, the first block plus the blocks that share the most words with the change, in page order, within the same 6,000 characters. Pages that fit are sent whole. It is deterministic and uses no model. The default stays `excerpt="head"`, so R1 is unchanged.

## Registered comparison

- Same four corpora, same pinned commits, same events, same model (`openai/gpt-oss-120b:fastest`), temperature 0, run on the same day as the R1 reference run.
- Two runs per corpus: `head` (the R1 reference) and `relevant`.
- Measures, per corpus and on the newer half only: share of events with a right page in the top 3 after reading, mean reciprocal rank, right pages placed in "likely", precision of "likely".
- **Kept for a corpus** if the top-3 share rises by at least 2 points or the mean reciprocal rank by at least 0.02, as in the R1 rule. Otherwise it is published as no gain.
- Published as "corpus-dependent" if it helps on fewer than three corpora. No averaging across corpora.
- Expected, stated in advance: a gain on corpora with long pages (Prometheus, OpenBB), none on the service manual. If it helps nowhere, the clue was wrong and that is recorded.

## Limits

- One model, one date. Each run's call count is stored with its report.
- The R1 newer halves are no longer fresh, so a gain there is weaker evidence than one on a corpus not yet looked at.
- Nothing here changes search, so the share of events with no right page among the 8 candidates (11% to 44% depending on the corpus) is untouched.
