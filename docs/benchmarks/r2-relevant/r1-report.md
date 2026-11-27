# R1 accuracy: results

Registered in [r1-preregistration.md](../r1-preregistration.md) before any R1 measurement. Each corpus is judged on its own, on the newer half by date. Nothing is combined across corpora.

## Verdict

Release R1 acceptance test: **undecided**.

Corpora not yet run: hub, openbb, prometheus, service-manual.

| Corpus | Kind | Events scored | Commit | Search | Reader | Model calls |
| --- | --- | ---: | --- | --- | --- | ---: |

## What each pass added (newer half)

| Corpus | Pass | Right page in top 3 | Reciprocal rank | Gain | Kept |
| --- | --- | ---: | ---: | --- | --- |

## Limits

- The replay scores commit messages against the pages they edited. It is a floor for the first passes and a proxy for real change events.
- The Hub and OpenBB newer halves were seen in earlier reports; the Prometheus and service manual halves were not.
- The GOV.UK corpus is archived (2016) and many of its commit messages name the file they edit.
- One reader model, on one date. Precision of the likely list is the registered reading; the literal full-list figure is shown beside it.

