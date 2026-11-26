# Replay on the Prometheus documentation history (word search, pass 1)

Corpus at `a8a02474`, folders: docs. At most 8 candidates per event.

## Overall

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All scored events | 273 | 78% | 76% | 0.56 | 267 | 22% |

## By period (tune on the older half, report on the newer half)

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| older half | 136 | 72% | 71% | 0.49 | 133 | 20% |
| newer half | 137 | 83% | 81% | 0.62 | 134 | 24% |

## By how the pages were found

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| explicit reference | 22 | 100% | 100% | 0.96 | 22 | 22% |
| nothing returned | 6 | 0% | 0% | 0.00 | 0 | n/a |
| search | 245 | 78% | 76% | 0.53 | 245 | 22% |

## By number of pages the commit modified

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 page | 259 | 79% | 79% | 0.57 | 254 | 22% |
| 2-3 pages | 11 | 64% | 35% | 0.41 | 11 | 17% |
| 4+ pages | 3 | 33% | 8% | 0.11 | 2 | 8% |

## By length of the commit message

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| under 8 words | 109 | 66% | 65% | 0.43 | 105 | 21% |
| 8-30 words | 114 | 86% | 85% | 0.61 | 112 | 23% |
| over 30 words | 50 | 84% | 80% | 0.71 | 50 | 24% |

## Commits left out

- 5 × no existing page modified (new pages, assets or config only)
- 4 × message shorter than 3 words
- 2 × more than 10 pages modified (bulk edit, not one change)

## Every scored event

| Date | Commit | Message | Truth | Found | Recall |
| --- | --- | --- | ---: | ---: | ---: |
| 2026-11-25 | `a8a02474` | fix: Fix prose and screenshot in intrumentation tutorial | 1 | 0 | 0% |
| 2026-11-17 | `2dd00ee1` | docs: fix the dead GitLab Alertmanager integration link | 1 | 2 | 100% |
| 2026-11-14 | `69834613` | Correct 'procol' to 'protocol' in documentation | 1 | 5 | 100% |
| 2026-11-12 | `37d616f6` | docs: fix dead matrix-hookshot link | 1 | 3 | 100% |
| 2026-11-09 | `5e1fd26e` | docs: document review rules for AI bot pull requests in contributing g | 1 | 2 | 100% |
| 2026-11-09 | `28c2aae6` | docs: add Nightingale to integrations | 1 | 8 | 100% |
| 2026-11-08 | `14696405` | Add Akmatori to Alertmanager webhook receivers | 1 | 4 | 100% |
| 2026-10-30 | `38cd0646` | docs: fix dead OpenZiti, Pomerium, Mezmo and GreptimeDB links | 3 | 1 | 0% |
| 2026-10-30 | `a295741b` | docs: fix dead client_java, Perses and Micrometer links | 3 | 2 | 33% |
| 2026-10-29 | `1faf8a9b` | Move LibreDB Studio entry into alphabetical order | 1 | 1 | 100% |
| 2026-10-28 | `828e69aa` | docs: fix typo in OpenMetrics 2.0 migration guide | 1 | 8 | 100% |
| 2026-10-28 | `50dc4126` | om2/summary: allow negative Sum and Quantile values | 1 | 8 | 100% |
| 2026-10-02 | `68a2f511` | docs: Remove unmaintained exporters | 1 | 1 | 100% |
| 2026-10-26 | `90a30fc4` | docs: use default listener port in TLS examples | 1 | 8 | 0% |
| 2026-10-26 | `22906ce2` | docs: fix certificate directory in TLS guide | 1 | 3 | 100% |
| 2026-10-24 | `3576591a` | docs: add Kepler to hardware exporters | 1 | 8 | 100% |
| 2026-10-22 | `46a54fb3` | rw2: add stateless and stateless-st modes (rc.6) | 1 | 6 | 100% |
| 2026-10-13 | `98d58021` | docs(first-steps): checksum verification and macOS first-run fixes | 1 | 2 | 100% |
| 2026-10-20 | `c10695ab` | om2/gaugehistogram: prohibit negative count and bucket values | 1 | 3 | 100% |
| 2026-10-19 | `02db958f` | docs: fix broken GitHub anchor link in contributor guide | 1 | 5 | 100% |
| 2026-10-18 | `8d6c4a61` | Add TEMPer USB thermal sensor exporter link | 1 | 5 | 100% |
| 2026-10-16 | `6d11cea2` | Remove code block from zen acknowledgements | 1 | 4 | 0% |
| 2026-10-16 | `bb753d29` | om2/version: bump rc version in preparation of changes | 1 | 8 | 0% |
| 2026-10-12 | `84e0a926` | docs: fix two more broken anchor links | 2 | 7 | 50% |
| 2026-10-09 | `6b4cce62` | docs: fix broken in-page anchor links | 4 | 6 | 25% |
| 2026-10-06 | `19854d28` | Add LibreDB Studio to other integrations | 1 | 7 | 100% |
| 2026-09-29 | `d5552697` | rw2: rc.5 version | 1 | 4 | 100% |
| 2026-09-26 | `8a42b398` | Add CallHeim to Alertmanager webhook receiver integrations | 1 | 4 | 100% |
| 2026-09-23 | `9422f695` | docs(security): stop presenting CORS as an XSS defence | 1 | 1 | 100% |
| 2026-08-02 | `2d2be504` | Add Dagster exporter to list of miscellaneous exporters | 1 | 8 | 100% |
| 2026-09-11 | `6bc84f20` | Generate LTS documentation and downloads from support dates | 1 | 3 | 100% |
| 2026-09-10 | `d1543859` | Add Oodle remote storage integration | 1 | 3 | 100% |
| 2026-09-10 | `3cbe8340` | docs: move Node.js client library to official list | 1 | 8 | 100% |
| 2026-09-08 | `52df6f8b` | fix: correct grafana dashboard URL in documentation | 1 | 8 | 100% |
| 2026-09-08 | `4b25078a` | Add BetterDB Monitor to Databases exporters list | 1 | 8 | 100% |
| 2026-09-07 | `6716ef12` | Mark Prometheus 3.5 as end of life | 1 | 3 | 100% |
| 2026-09-02 | `7a12bfa0` | Update docs/introduction/release-cycle.md | 1 | 3 | 100% |
| 2026-09-02 | `7410a164` | clarify LTS commitment | 1 | 0 | 0% |
| 2026-09-01 | `c9cdfcf0` | Add AlertINT to Alertmanager webhook receiver integrations | 1 | 4 | 100% |
| 2026-08-28 | `6ca00d63` | docs: close unclosed code fence hiding developer summit section | 1 | 4 | 100% |
| 2026-08-26 | `ac340e7f` | docs: unify getting started content into first steps | 1 | 2 | 0% |
| 2026-08-26 | `a0d29881` | Add hint to regarding CORS headers of Alertmanager | 1 | 3 | 100% |
| 2026-08-13 | `487cd80b` | docs(instrumenting): list ClickHouse among software exposing Prometheu | 1 | 3 | 0% |
| 2026-08-13 | `218274e2` | docs(practices): fix three typos in histograms and summaries | 1 | 4 | 100% |
| 2026-08-13 | `90afeb43` | docs: use https for external links in faq | 1 | 5 | 100% |
| 2026-08-12 | `1edbe32a` | fix: link governance document in the overview | 1 | 5 | 100% |
| 2026-08-12 | `d870e482` | remove direct classification from Apache APISIX | 1 | 1 | 100% |
| 2026-08-12 | `f264ca28` | docs: add Apache APISIX to software exposing Prometheus metrics | 1 | 8 | 100% |
| 2026-08-11 | `cd94bdb0` | docs: fix typo in Histograms and summaries | 1 | 8 | 100% |
| 2026-08-05 | `fe6f3c94` | apply typo fix to spec 2 of document | 1 | 8 | 100% |
| 2026-08-04 | `157bea87` | docs: update TSDB storage comparison | 1 | 5 | 100% |
| 2026-07-30 | `b4254f0c` | Fix subtitle notation in open_metrics_spec.md | 1 | 8 | 0% |
| 2026-07-26 | `d4a19f96` | Add meinberg_ltos_exporter to exporters list | 1 | 8 | 0% |
| 2026-07-21 | `90d91e44` | Add OpenObserve remote storage integration | 1 | 8 | 100% |
| 2026-07-20 | `d43edc1a` | Updated integrations.md with SMSEagle support for voice and SMS | 1 | 1 | 100% |
| 2026-07-18 | `16f567c7` | Add Slurm exporter | 1 | 8 | 0% |
| 2026-07-08 | `30a990b5` | fix: change to new governance doc | 1 | 1 | 0% |
| 2026-07-07 | `1127f4b6` | Clarify wording around DoS reporting | 1 | 1 | 0% |
| 2026-07-01 | `3f332291` | Change links to GitHub repo | 1 | 3 | 0% |
| 2026-07-01 | `703050b6` | Revert to single level list | 1 | 8 | 0% |
| 2026-07-01 | `b07a46e8` | chore: document 3.13 LTS release | 1 | 4 | 100% |
| 2026-06-28 | `c479f5b5` | Fix duplicated words in docs | 2 | 4 | 50% |
| 2026-06-27 | `33df5eb2` | Fix grammar in overview section | 1 | 1 | 0% |
| 2026-06-25 | `1f86e83a` | Add alternative Haskell client library | 1 | 8 | 100% |
| 2026-06-24 | `4c004dad` | Add Rust to native histogram instrumentation libraries | 1 | 8 | 100% |
| 2026-06-16 | `797cb37d` | Add Prometheus 3.13 as an LTS release | 1 | 3 | 0% |
| 2026-06-12 | `e43b4c3d` | Add Last9 remote storage to integration doc | 1 | 7 | 100% |
| 2026-05-21 | `2f0ba506` | Fix typos in native_histograms.md (evalute/signifcantly/abitrary) | 1 | 1 | 100% |
| 2026-05-21 | `25fba80a` | add Garmin Connect exporter | 1 | 8 | 100% |
| 2026-05-16 | `ececf3c2` | Add Runframe integration to documentation | 1 | 1 | 100% |
| 2026-05-12 | `18588e5c` | docs: add ITOC360 Alertmanager webhook integration | 1 | 4 | 100% |
| 2026-02-04 | `c82a04fe` | Histogram spec: Rework and amend operators section | 1 | 5 | 100% |
| 2026-04-17 | `a92a2c03` | Update created timestamp references to start timestamp in histogram do | 1 | 8 | 100% |
| 2026-04-14 | `d3e2d63e` | docs(integrations): fix incorrect path for http_sd_config link | 1 | 1 | 0% |
| 2026-04-08 | `57e718ca` | Add FairCom Edge exporter to IoT section | 1 | 4 | 100% |
| 2026-04-08 | `1d5f492c` | om2: remove typo in migration guide | 1 | 6 | 100% |
| 2026-04-08 | `300bcc39` | Address reviews, editorial changes | 1 | 5 | 100% |
| 2026-04-01 | `855dffc0` | OM2: Enable in docs menu; mark it as experimental | 1 | 7 | 100% |
| 2026-04-01 | `3f0428d6` | fix(om2): move mermaid diagram outside the spec | 1 | 2 | 0% |
| 2026-04-01 | `d3a9435c` | Fix inline code formatting in docs/guides/opentelemetry.md | 1 | 5 | 100% |
| 2026-03-30 | `d28f55ea` | add exception for Exemplar | 1 | 7 | 100% |
| 2026-03-30 | `8f08ed6f` | Apply suggestions from code review | 1 | 3 | 100% |
| 2026-03-30 | `c97e6290` | OM2: Metric/MetricFamily.Name escaping consistency | 1 | 5 | 100% |
| 2026-03-30 | `7ca12855` | OM2: Add unknown metadata example | 1 | 8 | 100% |
| 2026-03-30 | `f140aaac` | feat(om2): expand Extensions and Improvements section | 1 | 4 | 100% |
| 2026-03-30 | `15ec08da` | fix(om2): clarify empty UNIT/HELP value wording | 1 | 5 | 100% |
| 2026-03-30 | `c1631301` | feat(om2): clarify Timestamp and Start Timestamp semantics | 1 | 4 | 100% |
| 2026-03-30 | `3d727c50` | feat(om2): recommend TLS 1.3 while keeping TLS 1.2 as minimum | 1 | 7 | 100% |
| 2026-03-30 | `58d16942` | OM2: Outline failure mode | 1 | 2 | 0% |
| 2026-03-30 | `c9cde747` | fix(om2): clarify which Classic Buckets may be dropped | 1 | 5 | 100% |
| 2026-03-30 | `d4b8455c` | feat(om2): expand Number description with float64 and NaN details | 1 | 6 | 100% |
| 2026-03-30 | `61a91078` | feat(om2): add link from Unit metadata to Units and Base Units section | 1 | 7 | 100% |
| 2026-03-30 | `b5812039` | fix(om2): consistent capitalization of Gcount | 1 | 2 | 100% |
| 2026-03-25 | `2859ef2d` | feat(om2): switch ABNF from RFC 5234 to RFC 7405 | 1 | 4 | 100% |
| 2026-03-25 | `c05614ca` | fix(om2): small corrections to ABNF | 1 | 3 | 100% |
| 2026-03-25 | `142f6de0` | Apply suggestion from @dashpole | 1 | 1 | 100% |
| 2026-03-25 | `1daba88f` | Apply suggestion from @dashpole | 1 | 1 | 100% |
| 2026-03-25 | `f7889483` | fix(om2): introduce SampleValue abstract class to model exclusive Numb | 1 | 2 | 100% |
| 2026-03-25 | `011cfd03` | fix(om2): reorder Sample relationships in diagram to match wire format | 1 | 6 | 100% |
| 2026-03-25 | `19123245` | fix(om2): replace MetricFamily subclasses with MetricFamilyType enum i | 1 | 4 | 100% |
| 2026-03-25 | `dd81b711` | feat(om2): add Mermaid class diagram of the data model | 1 | 6 | 100% |
| 2026-03-25 | `b565e05e` | fix(om2): apply content changes from PR #2851 | 1 | 5 | 100% |
| 2026-03-25 | `8f285577` | feat(om2): clarify that timestamps MAY be floating point for sub-secon | 1 | 4 | 100% |
| 2026-03-25 | `2474abde` | fix(om2): exemplar common rules | 1 | 5 | 100% |
| 2026-03-25 | `cb4a90c2` | feat(om2): add Normative Language section defining RFC 2119/8174 keywo | 1 | 4 | 100% |
| 2026-03-23 | `cb1a9956` | fix(om2): be specific when it comes to leading underscores rule | 1 | 8 | 100% |
| 2026-03-20 | `0ae66d19` | fix(om2.0) : do we really need escaping for escaping? | 1 | 8 | 100% |
| 2026-03-20 | `33fb2eb1` | feat(om2.0): the extensions and improvements section | 1 | 4 | 100% |
| 2026-03-20 | `974c4ed0` | fix(om2.0): fixes in type text format | 1 | 6 | 100% |
| 2026-03-20 | `32aba1e7` | refact(om2.0): reorder ABFN and enhance comments | 1 | 4 | 100% |
| 2026-03-20 | `c9ed9a0e` | fix(om2.0): metadata text format updates | 1 | 5 | 100% |
| 2026-03-20 | `f279b4cc` | refact(om2.0): some wording improvements to the text format around utf | 1 | 8 | 100% |
| 2026-03-19 | `d2f18e7c` | Fix minor grammar issues in FAQ documentation | 1 | 5 | 100% |
| 2026-03-10 | `4933d057` | Update metric_types.md for native histograms | 2 | 8 | 50% |
| 2026-02-18 | `469f1f04` | Revamp histogram and summaries best practices | 1 | 8 | 100% |
| 2026-03-18 | `7f943610` | fix(om2.0): abnf consistent with model | 1 | 5 | 100% |
| 2026-03-18 | `47219cdb` | Remove title header from the Zen of Prometheus | 1 | 4 | 100% |
| 2026-03-18 | `cb6e9bfe` | om2: pre rc.0 changes from WG | 1 | 7 | 100% |
| 2026-03-17 | `e728fa3f` | Update docs/practices/the_zen.md | 1 | 5 | 100% |
| 2026-03-17 | `abeed267` | Apply suggestions from code review | 1 | 2 | 0% |
| 2026-03-13 | `880b0011` | add example with multiple samples per metric | 1 | 8 | 100% |
| 2026-03-13 | `f247196e` | move sample ordering into metric | 1 | 5 | 100% |
| 2026-03-13 | `5c968722` | Apply suggestions from code review | 1 | 2 | 0% |
| 2026-03-13 | `5413af6c` | update StateSet to use new terminology | 1 | 5 | 100% |
| 2026-03-13 | `38984ad1` | change MetricPoint to Sample and define sample. Exclude stateset | 1 | 3 | 100% |
| 2026-03-12 | `025f7346` | Fix typo in dockerswarm guide | 1 | 2 | 100% |
| 2026-03-13 | `a92f82c4` | om2: Setup mdox formatter for openmetrics spec 2.0 | 1 | 4 | 100% |
| 2026-03-13 | `57c335ed` | fix(om2): consistency between model and exposition | 1 | 7 | 100% |
| 2026-03-13 | `e3585af5` | fix(om2.0): consistency between text and abnf on Summary fields | 1 | 6 | 100% |
| 2026-03-13 | `a3e73fff` | OM 2.0: Add requirements to exemplar timestamps, and clarify exemplar  | 1 | 7 | 100% |
| 2026-03-13 | `bf72edc4` | feat(om2.0): have one line for classic-native histogram | 1 | 8 | 100% |
| 2026-03-12 | `d6947bf1` | feat(om2.0): update the version to rc0 | 1 | 8 | 100% |
| 2026-03-11 | `94f23273` | docs: Add HTTP Service Discovery section to Integrations | 1 | 8 | 100% |
| 2026-03-11 | `611089c1` | clarify first steps | 1 | 0 | 0% |
| 2026-03-09 | `c7ddb800` | cleanup left-over text from when MetricPoints could have multiple valu | 1 | 6 | 100% |
| 2026-03-11 | `4edf6d2b` | OM 2.0: MetricFamily name is the same as Metric Name for target_info | 1 | 8 | 100% |
| 2026-03-11 | `b92be37a` | OM 2.0: Consistently use MetricFamily Type | 1 | 5 | 100% |
| 2026-03-11 | `8f039d6d` | OM 2.0: recommend exemplar keys for trace context | 1 | 7 | 100% |
| 2026-03-09 | `8ba34e56` | remove references to additional suffixes on samples | 1 | 7 | 100% |
| 2026-03-06 | `66817ef4` | Add OpenClaw exporter to the list | 1 | 8 | 100% |
| 2026-03-05 | `c42ff584` | OM2: Discontinue OM Proto; specify PrometheusProto | 2 | 2 | 0% |
| 2026-03-05 | `1cdc632d` | docs(exporters): Add tailscale exporter | 1 | 8 | 100% |
| 2025-04-24 | `db7eb202` | [opentelemetry] fix some grammar errors | 1 | 5 | 100% |
| 2026-03-03 | `7d4e848d` | fix(om2.0): consistency, GaugeHistogram and special values | 1 | 4 | 100% |
| 2026-03-03 | `10cfd1d9` | fix(om2.0): more missing suffix | 1 | 4 | 100% |
| 2026-03-01 | `5cb8bbb7` | add postfix exporter | 1 | 8 | 0% |
| 2026-02-26 | `a6450370` | docs: use canonical Pushgateway and Go client links | 1 | 7 | 100% |
| 2024-02-19 | `fa693510` | Multiple targets and multiple modules in one Prometheus job | 1 | 8 | 100% |
| 2026-02-26 | `960207ea` | fix(om2.0): consistency of metric name is metric name | 1 | 8 | 100% |
| 2026-02-25 | `0327b4b9` | fix(om2.0): consistency of metric name is metric name | 1 | 8 | 100% |
| 2026-02-24 | `12e2edf8` | fromatting the spaces and removed comma | 1 | 0 | 0% |
| 2026-02-24 | `be82632e` | om2: MetricFamilyName is MetricName | 1 | 6 | 100% |
| 2026-02-24 | `081abf71` | Allow multiple exemplars on counters and histograms | 1 | 8 | 100% |
| 2026-02-18 | `6ba0caf6` | Update docs/specs/om/open_metrics_spec_2_0.md | 1 | 8 | 100% |
| 2026-02-18 | `66d21518` | Update docs/specs/om/open_metrics_spec_2_0.md | 1 | 8 | 100% |
| 2026-02-18 | `e9f902f4` | feat(om2.0): exemplars MUST have a timestamp | 1 | 7 | 100% |
| 2026-02-17 | `753f9a0a` | Update docs/specs/om/open_metrics_spec_2_0.md | 1 | 8 | 100% |
| 2026-02-18 | `47ae9ed3` | fixes: more spells errors with cross verifications | 1 | 1 | 0% |
| 2026-02-18 | `8bad120f` | fixes: more spells errors | 1 | 0 | 0% |
| 2026-02-17 | `f3bf8f57` | docs: add HTTP Service Discovery section to integrations page | 1 | 8 | 100% |
| 2026-02-17 | `60cc9cc6` | contribution guide: @beorn review comments | 1 | 2 | 100% |
| 2026-02-16 | `9a3d311e` | chore: address review comments | 1 | 1 | 0% |
| 2026-02-12 | `49846691` | Finish the contributors guide | 1 | 1 | 100% |
| 2022-07-29 | `aafad80c` | Update exposition_formats.md | 1 | 8 | 100% |
| 2026-02-11 | `c7e04fe2` | OM2: Remove exemplar hard limit; mention use intention | 1 | 5 | 100% |
| 2026-02-11 | `60208036` | allow using double-underscores for federation | 1 | 6 | 100% |
| 2026-02-10 | `5bec1eac` | Fix Rootly documentation link | 1 | 4 | 100% |
| 2026-02-10 | `7bd8a572` | add Triton to the list of apps exposing Prometheus metrics | 1 | 8 | 0% |
| 2022-02-18 | `04952c18` | integrations: Add ElastiCache SD | 1 | 6 | 0% |
| 2020-11-06 | `e4a91575` | Add Open OnDemand exporter | 1 | 8 | 0% |
| 2026-02-09 | `f5dd6a45` | Add Rootly to Alertmanager Webhook Receiver integrations | 1 | 2 | 100% |
| 2026-02-08 | `6271bf6f` | Add webhook integrations | 1 | 4 | 100% |
| 2026-02-06 | `28bf4190` | Fix typo in native_histograms.md | 1 | 5 | 100% |
| 2026-02-05 | `808ed38d` | feat(om2): classic histogram and summary as complex types | 1 | 6 | 100% |
| 2026-02-04 | `a2c011ad` | Fix errors in tutorial/instrumenting HTTP server | 1 | 8 | 100% |
| 2026-02-03 | `9a788335` | Add pihole-exporter | 1 | 8 | 0% |
| 2021-12-01 | `d63f0f42` | Add RTPEngine to 3rd-party software that export Prometheus metrics | 1 | 8 | 100% |
| 2026-02-02 | `dbf40507` | fix(docs): correct URL encoding in file-based service discovery link | 1 | 8 | 0% |
| 2026-01-28 | `93119d75` | feat(om2.0): allow float histograms | 1 | 8 | 100% |
| 2026-01-27 | `58c046af` | docs(practices): add native histograms guidance | 1 | 8 | 100% |
| 2026-01-27 | `0a06fd33` | docs(practices): address review comments on The Zen of Prometheus | 1 | 2 | 100% |
| 2026-01-27 | `410443d2` | naming: improve unit suggestion | 1 | 8 | 100% |
| 2026-01-26 | `d4406d23` | sAdd KafkaJS exporter to list of available exporters | 1 | 8 | 100% |
| 2022-11-07 | `292bc326` | Remove usage of global registry from Go example | 2 | 8 | 50% |
| 2026-01-18 | `689e8716` | Update .NET / C# link to maintained alternative | 1 | 8 | 0% |
| 2025-05-03 | `be103c40` | add redfish api exporter that references the comcast/fishymetrics repo | 1 | 6 | 0% |
| 2026-01-16 | `315b7175` | Add a link to ioriver-exporter | 1 | 8 | 0% |
| 2026-01-14 | `3db381f8` | docs: add ZLMediaKit exporter to the list of available exporters | 1 | 8 | 0% |
| 2026-01-13 | `9b1ba7bc` | docs: remove discontinued go-neb entry | 1 | 1 | 100% |
| 2026-01-13 | `86e7bc68` | docs: remove abandoned PowerDNS exporter link | 1 | 1 | 0% |
| 2026-01-13 | `5cc3355e` | docs: explain all placeholders in node exporter download URL | 1 | 2 | 100% |
| 2026-01-13 | `fc4ced0b` | docs: add matrix-alertmanager and clarify Matrix integration options | 1 | 1 | 100% |
| 2026-01-09 | `8afdb70c` | docs(consoles): Add Prometheus 3.0 deprecation warnings and update lin | 2 | 7 | 50% |
| 2026-01-09 | `b0175ec5` | docs: improve node exporter download instructions | 1 | 1 | 100% |
| 2026-01-09 | `bd6e71f5` | docs: replace discontinued go-neb with matrix-hookshot | 1 | 4 | 100% |
| 2026-01-09 | `f2dfa4b4` | docs: add mixin definition to glossary | 1 | 8 | 100% |
| 2026-01-08 | `ec927a21` | docs: fix broken PowerDNS exporter link | 1 | 2 | 0% |
| 2026-01-06 | `cbea98f4` | docs(instrumenting): Update exposition_formats.md to include quoting s | 1 | 8 | 100% |
| 2025-12-18 | `30643632` | remove prometheus monitoring and global object | 1 | 8 | 0% |
| 2025-12-18 | `ca99d72e` | add docker-inline-config approach | 1 | 3 | 100% |
| 2025-12-11 | `126caffa` | Replace NVIDIA exporter with nvidia's project | 1 | 8 | 100% |
| 2025-12-10 | `31951232` | feat(om2): add native histograms to OpenMetrics2.0 | 1 | 8 | 100% |
| 2025-12-04 | `467de3d4` | add swift to unofficial third-party client libraries list | 1 | 7 | 100% |
| 2025-12-03 | `532758b6` | OM2.0: Add info and examples for UTF-8 | 1 | 8 | 100% |
| 2025-12-03 | `61ce601d` | docs(exposition): clarify required Content-type header for scrapes | 1 | 8 | 0% |
| 2025-11-24 | `3a44f489` | relax stance on metrics with same name but different labels | 1 | 8 | 100% |
| 2025-11-21 | `8db7d12c` | Improve HA FAQ entry | 1 | 4 | 100% |
| 2025-11-20 | `60c24e45` | feat(om2): exemplar timestamp MAY to SHOULD | 1 | 8 | 100% |
| 2025-11-14 | `9e02fa11` | OpenTelemetry guide: document the info function's churn handling | 1 | 7 | 100% |
| 2025-11-11 | `a04d7ce0` | chore(om2.0): rename created timestamp to start timestamp | 1 | 7 | 100% |
| 2025-11-05 | `fca6b9ba` | Adds another exporter for Azure Health (replaces the FXinnovation/azur | 1 | 1 | 100% |
| 2025-11-05 | `65a6ca02` | feat(om2.0): Add UTF-8 metric names and labels | 1 | 8 | 100% |
| 2025-11-04 | `2530b2cd` | RW 2.0-rc.4 (breaking): Move CT from TimeSeries to Sample; Rename to S | 1 | 6 | 100% |
| 2025-10-31 | `ca94ec0c` | feat(om2.0): relax suffix rules for total and unit | 1 | 8 | 100% |
| 2025-10-30 | `3dbdf491` | reworiding exporter announcing documentation | 1 | 8 | 100% |
| 2025-10-29 | `db005cb7` | om2: Update authors; update intro | 1 | 7 | 100% |
| 2025-10-27 | `1934595d` | Add Oodle as a remote write receiver | 1 | 8 | 100% |
| 2025-10-25 | `09e8eccc` | Fix exporters link path in writing_exporters.md | 1 | 8 | 100% |
| 2025-10-24 | `74c5ee25` | feat(nh): remove experimental from native histograms | 3 | 5 | 100% |
| 2025-10-23 | `7fa96a00` | Add Parny integration to Prometheus integrations list | 1 | 5 | 100% |
| 2025-10-22 | `5a056203` | OTel guide: recommend using the info function for joining with target_ | 1 | 8 | 100% |
| 2025-10-22 | `99336480` | Update opentelemetry.md | 1 | 7 | 100% |
| 2025-10-16 | `f24c4e66` | spec (histograms): Clarify that the zeroth custom bucket includes -Inf | 1 | 8 | 100% |
| 2025-10-08 | `58b069ad` | spec (histograms): Clarify counter reset hints after aggregations | 1 | 6 | 100% |
| 2025-10-08 | `5b2f031e` | spec (histograms): Further clarify NHCB federation | 1 | 1 | 100% |
| 2025-10-08 | `9822c487` | spec (histograms): Add NHCB bucket layout reconciliation | 1 | 6 | 100% |
| 2025-10-08 | `2c220462` | spec (histograms): Clarify valid custom values | 1 | 6 | 100% |
| 2025-10-08 | `ad9ddde7` | docs: Fix utf8 escaping parameter in content negotiation docs | 1 | 4 | 100% |
| 2025-10-08 | `66bd52f2` | feat(om1.1): relax the requirements around unit and total suffixes | 1 | 8 | 100% |
| 2025-10-03 | `057e0e6e` | chore(om1.1) Set status of OM 1.1 as draft | 1 | 7 | 0% |
| 2025-10-02 | `5a0b8f85` | om1: Update release date | 1 | 8 | 100% |
| 2025-09-30 | `96abc128` | spec: Be explicit about invalidity of negative histograms | 1 | 8 | 100% |
| 2025-10-01 | `2dab5342` | docs: fix typo in content_negotation | 1 | 2 | 0% |
| 2025-09-25 | `2e8e4dad` | specs: Clarify federation of NHCB | 1 | 1 | 100% |
| 2025-09-29 | `09c4b47b` | Fix typo in metric name | 1 | 2 | 0% |
| 2025-09-24 | `b27dead3` | native histogram spec: More clarifications about schemas | 1 | 2 | 100% |
| 2025-09-24 | `f002a857` | Fix link for HeyOnCall integration | 1 | 2 | 100% |
| 2025-09-19 | `60c3cf09` | OM1.1: create OpenMetrics 1.1 draft and enable CI check of ABNF on it | 1 | 4 | 100% |
| 2025-09-18 | `8aad6950` | native histograms: clarify schema reduction and schemas 9-52 | 1 | 4 | 100% |
| 2025-09-11 | `b79f93dc` | rw2: Add missing space after link | 1 | 8 | 100% |
| 2025-09-03 | `8d14d8b0` | histogram spec: Fix wording around annotation about counter resets | 1 | 1 | 100% |
| 2025-08-27 | `bcce4776` | Add CCF HuaTuo exporter to the exporters list in documentation | 1 | 8 | 0% |
| 2025-08-21 | `a0dbf027` | histogram spec: Remove TODO about synthetic zero sample | 1 | 3 | 100% |
| 2025-08-13 | `41b3c64c` | Native histogram spec: Clarify counter reset handling for + and - | 1 | 8 | 100% |
| 2025-08-13 | `4c85a097` | native histogram spec: Update section about unary minus | 1 | 4 | 100% |
| 2025-08-13 | `b6a90f5c` | fix(om2): histograms and negative observed values | 1 | 7 | 100% |
| 2025-08-08 | `913328bb` | add grafana-bridge | 1 | 7 | 0% |
| 2025-08-04 | `d82d764e` | utf8: update doc for deprecated bool | 1 | 2 | 0% |
| 2025-07-27 | `b5841f3e` | Update the URL to Dovecot's metrics endpoint documentation. | 1 | 7 | 0% |
| 2025-07-24 | `4b1b80f5` | utf8: update doc for deprecated bool | 1 | 2 | 0% |
| 2025-07-21 | `9e876084` | chore(security.md): add more precisions regarding sec bugs reporting | 1 | 1 | 100% |
| 2025-07-16 | `c90124fa` | Add a more explicit note for security scanners and Go | 1 | 7 | 100% |
| 2025-07-14 | `cda26d7c` | Add Release 3.5 as LTS | 1 | 1 | 100% |
| 2025-07-11 | `1c2dc97d` | docs(opentelemtry): Add explanation of UnderscoreEscapingWithoutSuffix | 1 | 4 | 100% |
| 2025-07-01 | `e39897e4` | refactor(om2): rename, align Created Value to Created Timestamp | 1 | 8 | 100% |
| 2025-07-01 | `63e50e99` | Update OM 2.0 with proposal#43 Created Timestamp syntax | 1 | 5 | 100% |
| 2025-06-25 | `bbf3583e` | fix(nh-spec): update histogram_quantile and histogram_fraction docs | 1 | 6 | 100% |
| 2025-06-20 | `6320b3fc` | native histoggram spec: document extrapolation below zero heuristics | 1 | 6 | 100% |
| 2025-06-17 | `2e2c0a4b` | Add Webhook integration for Alertmanager to Notion Database | 1 | 2 | 100% |
| 2025-06-13 | `6893aca9` | feat: add the exporter scraparr | 1 | 8 | 0% |
| 2025-06-13 | `19b2d910` | add perses as another visualisation tool | 1 | 4 | 0% |
| 2025-06-13 | `fb6b195a` | add a short description about Grafana | 1 | 8 | 0% |
| 2025-06-11 | `37c14861` | test(om2): test that examples follow the spec and fix if not | 1 | 6 | 100% |
| 2025-06-06 | `f52f7a0c` | Add NetBird exporter to the exporters list in documentation | 1 | 8 | 0% |
| 2025-06-04 | `cbfa1f27` | Fixed a couple of small typos/phrasing issues in the Alerting based on | 1 | 3 | 0% |
| 2025-05-29 | `a629ed77` | Update exporters.md | 1 | 8 | 0% |
| 2025-05-29 | `91dacf3a` | chore(ci): add action to test abnf syntax and examples in OM2.0 spec | 1 | 4 | 100% |
| 2025-05-27 | `79a0d610` | Move some new docs from "Concepts" to "Instrumenting" | 2 | 6 | 0% |
| 2025-05-27 | `60c4d886` | Fix sort order for new Concepts pages | 2 | 5 | 0% |
| 2025-05-24 | `3a7ea2b5` | Fix wrong heading level in Security Model page | 1 | 4 | 100% |
| 2025-05-22 | `5ee01216` | Integrate latest upstream docs changes | 1 | 3 | 0% |
| 2025-05-22 | `ea065ff0` | Standardize and fix up a bunch of Markdown / frontmatter fields | 8 | 1 | 0% |
| 2025-05-21 | `a0726523` | Fix a bunch of relative links in the local docs | 8 | 0 | 0% |
