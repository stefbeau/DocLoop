# R1 accuracy: results

Registered in [r1-preregistration.md](../r1-preregistration.md) before any R1 measurement. Each corpus is judged on its own, on the newer half by date. Nothing is combined across corpora.

## Verdict

Release R1 acceptance test: **not met**.

| Corpus | Kind | Events scored | Commit | Search | Reader | Model calls |
| --- | --- | ---: | --- | --- | --- | ---: |
| Hugging Face Hub docs | technical | 186 | `2c3f84c8` | hybrid (hf:BAAI/bge-small-en-v1.5) | openai/gpt-oss-120b:fastest | 1488 (0 unreadable) |
| OpenBB docs | technical | 80 | `692a7bce` | hybrid (hf:BAAI/bge-small-en-v1.5) | openai/gpt-oss-120b:fastest | 640 (0 unreadable) |
| Prometheus docs | technical | 273 | `a8a02474` | hybrid (hf:BAAI/bge-small-en-v1.5) | openai/gpt-oss-120b:fastest | 2141 (2 unreadable) |
| GOV.UK service manual | non-technical | 260 | `4efa105e` | hybrid (hf:BAAI/bge-small-en-v1.5) | openai/gpt-oss-120b:fastest | 2014 (0 unreadable) |

## Hugging Face Hub docs

Result: **targets missed**.

| Measure (newer half) | Target | Result | |
| --- | ---: | ---: | --- |
| Hit rate | 90% | 91% | met |
| Mean recall | 80% | 85% | met |
| Precision of the likely list | 60% | 59% | missed |
| Right pages placed in likely | 95% | 83% | missed |
| Wrong pages placed in also check | 85% | 84% | missed |
| Precision of the full list (literal reading) | 60% | 18% | missed |

Detail: [hub.md](hub.md)


## OpenBB docs

Result: **targets missed**.

| Measure (newer half) | Target | Result | |
| --- | ---: | ---: | --- |
| Hit rate | 90% | 72% | missed |
| Mean recall | 80% | 51% | missed |
| Precision of the likely list | 60% | 36% | missed |
| Right pages placed in likely | 95% | 73% | missed |
| Wrong pages placed in also check | 85% | 71% | missed |
| Precision of the full list (literal reading) | 60% | 14% | missed |

Detail: [openbb.md](openbb.md)


## Prometheus docs

Result: **targets missed**.

| Measure (newer half) | Target | Result | |
| --- | ---: | ---: | --- |
| Hit rate | 90% | 92% | met |
| Mean recall | 80% | 90% | met |
| Precision of the likely list | 60% | 47% | missed |
| Right pages placed in likely | 95% | 69% | missed |
| Wrong pages placed in also check | 85% | 81% | missed |
| Precision of the full list (literal reading) | 60% | 12% | missed |

Detail: [prometheus.md](prometheus.md)


## GOV.UK service manual

Result: **targets missed**.

| Measure (newer half) | Target | Result | |
| --- | ---: | ---: | --- |
| Hit rate | 90% | 69% | missed |
| Mean recall | 80% | 66% | missed |
| Precision of the likely list | 60% | 34% | missed |
| Right pages placed in likely | 95% | 79% | missed |
| Wrong pages placed in also check | 85% | 73% | missed |
| Precision of the full list (literal reading) | 60% | 9% | missed |

Detail: [service-manual.md](service-manual.md)


## What each pass added (newer half)

| Corpus | Pass | Right page in top 3 | Reciprocal rank | Gain | Kept |
| --- | --- | ---: | ---: | --- | --- |
| Hugging Face Hub docs | 1 words | 72% | 0.64 |  |  |
| Hugging Face Hub docs | 2 hybrid | 81% | 0.73 | 9% / 0.09 | yes |
| Hugging Face Hub docs | 3 reading | 90% | 0.81 | 10% / 0.089 | yes |
| OpenBB docs | 1 words | 32% | 0.29 |  |  |
| OpenBB docs | 2 hybrid | 42% | 0.39 | 10% / 0.104 | yes |
| OpenBB docs | 3 reading | 52% | 0.46 | 10% / 0.062 | yes |
| Prometheus docs | 1 words | 76% | 0.62 |  |  |
| Prometheus docs | 2 hybrid | 82% | 0.73 | 6% / 0.111 | yes |
| Prometheus docs | 3 reading | 80% | 0.73 | -2% / -0.005 | no |
| GOV.UK service manual | 1 words | 43% | 0.31 |  |  |
| GOV.UK service manual | 2 hybrid | 55% | 0.46 | 12% / 0.147 | yes |
| GOV.UK service manual | 3 reading | 61% | 0.52 | 6% / 0.059 | yes |

Scope of each pass, by the registered rule (kept on at least 3 corpora, fewer, or none): pass2 hybrid: **kept**; pass3 reading: **kept**.

## Limits

- The replay scores commit messages against the pages they edited. It is a floor for the first passes and a proxy for real change events.
- The Hub and OpenBB newer halves were seen in earlier reports; the Prometheus and service manual halves were not.
- The GOV.UK corpus is archived (2016) and many of its commit messages name the file they edit.
- One reader model, on one date. Precision of the likely list is the registered reading; the literal full-list figure is shown beside it.

