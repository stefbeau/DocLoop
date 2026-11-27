# R1 accuracy: results

Registered in [r1-preregistration.md](../r1-preregistration.md) before any R1 measurement. Each corpus is judged on its own, on the newer half by date. Nothing is combined across corpora.

## Verdict

Release R1 acceptance test: **not met**.

Corpora not yet run: hub, prometheus, service-manual.

| Corpus | Kind | Events scored | Commit | Search | Reader | Model calls |
| --- | --- | ---: | --- | --- | --- | ---: |
| OpenBB docs | technical | 80 | `692a7bce` | hybrid (hf:BAAI/bge-small-en-v1.5) | openai/gpt-oss-120b:fastest | 640 (0 unreadable) |

## OpenBB docs

Result: **targets missed**.

| Measure (newer half) | Target | Result | |
| --- | ---: | ---: | --- |
| Hit rate | 90% | 72% | missed |
| Mean recall | 80% | 51% | missed |
| Precision of the likely list | 60% | 37% | missed |
| Right pages placed in likely | 95% | 75% | missed |
| Wrong pages placed in also check | 85% | 70% | missed |
| Precision of the full list (literal reading) | 60% | 14% | missed |

Detail: [openbb.md](openbb.md)


## What each pass added (newer half)

| Corpus | Pass | Right page in top 3 | Reciprocal rank | Gain | Kept |
| --- | --- | ---: | ---: | --- | --- |
| OpenBB docs | 1 words | 32% | 0.29 |  |  |
| OpenBB docs | 2 hybrid | 42% | 0.39 | 10% / 0.104 | yes |
| OpenBB docs | 3 reading | 55% | 0.46 | 12% / 0.063 | yes |

## Limits

- The replay scores commit messages against the pages they edited. It is a floor for the first passes and a proxy for real change events.
- The Hub and OpenBB newer halves were seen in earlier reports; the Prometheus and service manual halves were not.
- The GOV.UK corpus is archived (2016) and many of its commit messages name the file they edit.
- One reader model, on one date. Precision of the likely list is the registered reading; the literal full-list figure is shown beside it.

