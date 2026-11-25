# Replay on the OpenBB documentation history: hybrid search and the reading step

Corpus at `692a7bce`, folders: content, content-odp. At most 8 candidates per event.

## Overall

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All scored events | 80 | 69% | 51% | 0.44 | 80 | 12% |

## By period (tune on the older half, report on the newer half)

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| older half | 40 | 65% | 50% | 0.49 | 40 | 9% |
| newer half | 40 | 72% | 51% | 0.39 | 40 | 14% |

## By how the pages were found

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 80 | 69% | 51% | 0.44 | 80 | 12% |

## By number of pages the commit modified

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 page | 41 | 63% | 63% | 0.41 | 41 | 8% |
| 2-3 pages | 23 | 65% | 41% | 0.42 | 23 | 13% |
| 4+ pages | 16 | 88% | 31% | 0.55 | 16 | 19% |

## By length of the commit message

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| over 30 words | 7 | 100% | 51% | 0.55 | 7 | 18% |
| 8-30 words | 26 | 88% | 73% | 0.59 | 26 | 17% |
| under 8 words | 47 | 53% | 38% | 0.34 | 47 | 7% |

## Commits left out

- 23 × message shorter than 3 words
- 12 × more than 10 pages modified (bulk edit, not one change)
- 8 × no existing page modified (new pages, assets or config only)

## Reading step (openai/gpt-oss-120b:fastest)

621 model calls, 0 unparsed replies (kept by default).

### If the reader deletes what it does not keep

| Group | Events | Hit rate before | after | Recall before | after | Precision before | after | Pages before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 80 | 69% | 54% | 51% | 37% | 12% | 33% | 8.0 | 2.85 |
| older half | 40 | 65% | 48% | 50% | 35% | 9% | 27% | 8.0 | 2.6 |
| newer half | 40 | 72% | 60% | 51% | 39% | 14% | 38% | 8.0 | 3.1 |

### How well the reader tells right from wrong, and the same-size baseline

| Group | Right pages kept | Wrong pages dropped | Reader: hit rate | recall | Top-k of search: hit rate | recall | k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 72% | 69% | 54% | 37% | 48% | 34% | 3 |
| older half | 67% | 71% | 48% | 35% | 52% | 39% | 3 |
| newer half | 75% | 67% | 60% | 39% | 42% | 30% | 3 |

### If the reader reorders the list instead of deleting

| Group | Right page in top 3, before | after | Recall in top 3, before | after | MRR before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 48% | 56% | 34% | 41% | 0.44 | 0.47 |
| older half | 52% | 52% | 39% | 40% | 0.49 | 0.47 |
| newer half | 42% | 60% | 30% | 42% | 0.39 | 0.48 |

## Every scored event

| Date | Commit | Message | Truth | Found | Recall |
| --- | --- | --- | ---: | ---: | ---: |
| 2026-09-29 | `692a7bce` | V5 docs | 8 | 8 | 12% |
| 2026-07-21 | `28697f6a` | Add documentation for Workspace Lite | 2 | 8 | 50% |
| 2026-07-20 | `aa6a6f12` | mcp auth | 3 | 8 | 33% |
| 2026-07-10 | `4e85fbde` | update iframe auth docs | 4 | 8 | 100% |
| 2026-07-08 | `649c584e` | Update the workspace MCP docs to feature hosted MCP vs sidecar | 4 | 8 | 100% |
| 2026-06-12 | `9698f864` | Custom agent features and user feedback docs | 3 | 8 | 100% |
| 2026-06-08 | `295ed04e` | docs for iframe / mcp | 1 | 8 | 100% |
| 2026-05-21 | `9c8225f8` | Document Workspace MCP and app builder resources | 1 | 8 | 100% |
| 2026-05-15 | `0f393b61` | Add cron job and data update support | 2 | 8 | 0% |
| 2026-05-08 | `d0963554` | vega lite docs | 1 | 8 | 0% |
| 2026-05-08 | `fc66265f` | Fix/git installation | 1 | 8 | 100% |
| 2026-04-25 | `e36e4c9e` | add docs for chartview new things | 2 | 8 | 50% |
| 2026-04-22 | `b01c1e42` | fix youtube dev video | 1 | 8 | 0% |
| 2026-04-03 | `fecb2571` | Apply security patches and clean up | 2 | 8 | 50% |
| 2026-03-24 | `af693b5e` | Docs Improvement | 4 | 8 | 25% |
| 2026-03-23 | `4f5fdcee` | allow global formatterFn | 1 | 8 | 100% |
| 2026-02-16 | `b7623b48` | Add advanced features to Widgets.json reference | 1 | 8 | 100% |
| 2026-01-29 | `149ed66c` | update name for rita | 1 | 8 | 0% |
| 2026-01-19 | `5b29ec81` | Feat/update docs for release | 3 | 8 | 33% |
| 2026-01-15 | `a3dfa0db` | Improve Developer Section of Python Docs | 8 | 8 | 38% |
| 2026-01-01 | `47ec6391` | docs: document ai flag for widget AI visibility | 1 | 8 | 0% |
| 2025-12-27 | `460f4dcb` | MCP tools added to docs | 2 | 8 | 0% |
| 2025-11-28 | `e8320193` | fix video + accordion | 1 | 8 | 0% |
| 2025-11-26 | `53517883` | Multi file viewer PDF with only POST examples | 1 | 8 | 100% |
| 2025-11-25 | `62b98f71` | Improve newsfeed style docs + improve docs ordering | 6 | 8 | 17% |
| 2025-11-16 | `cdd9be94` | Update Docs Style | 1 | 8 | 0% |
| 2025-11-13 | `d55981a8` | Update apps-json-reference.md | 1 | 8 | 100% |
| 2025-11-13 | `bdc5685c` | new groupby docs | 3 | 8 | 100% |
| 2025-10-22 | `4a72fd50` | Update ODP Screenshots | 4 | 8 | 50% |
| 2025-10-21 | `02f70a8c` | Add missing screenshots | 1 | 8 | 0% |
| 2025-09-30 | `4e6b985b` | Matching widget to mcp tool | 1 | 8 | 0% |
| 2025-09-18 | `7bb63dfe` | AI agents revamp docs | 1 | 8 | 100% |
| 2025-09-16 | `82da48b6` | MCP docs + Enterprise theme settings + orchestrator + genui | 3 | 8 | 0% |
| 2025-08-18 | `515595ff` | Add documentation for sparkline configuration in table widgets | 2 | 8 | 100% |
| 2025-08-06 | `6ca03621` | add plotly raw data to docs | 2 | 8 | 100% |
| 2025-07-30 | `4c35a6d2` | Update obb-widget.md | 1 | 8 | 100% |
| 2025-07-29 | `5741a37e` | Updates for Platform V4.4.5 | 4 | 8 | 25% |
| 2025-07-24 | `35ce2f93` | Improve significantly AI agent docs | 4 | 8 | 25% |
| 2025-06-18 | `10f4e80b` | Add widget parameter positioning documentation and enhance widgets.jso | 4 | 8 | 25% |
| 2025-06-17 | `1e0d3029` | warning on platform installer for workspace | 1 | 8 | 100% |
| 2025-06-12 | `557ea864` | Update multi file section | 1 | 8 | 100% |
| 2025-05-23 | `cc28994a` | update to show what the structure is of app | 1 | 8 | 0% |
| 2025-05-21 | `aafa7479` | Fix some broken URLs and get rid of useless loading bar | 2 | 8 | 0% |
| 2025-05-16 | `4d401ea4` | Update excel installation docs | 1 | 8 | 100% |
| 2025-05-16 | `677f7420` | Update excel docs | 1 | 8 | 100% |
| 2025-05-06 | `2d247afb` | updates some links and enterprise | 3 | 8 | 33% |
| 2025-05-02 | `64c9a3ea` | i like long branch names | 10 | 8 | 0% |
| 2025-05-01 | `dafd8213` | Remove registry file req for decorator, add to boilerplate code | 1 | 8 | 100% |
| 2025-04-30 | `7aa576eb` | Refactor overall docs | 7 | 8 | 0% |
| 2025-04-07 | `05842d75` | Update Platform Architecture Overview & Markdown Generator | 7 | 8 | 29% |
| 2025-01-22 | `44254be6` | Update copilot docs for widgets 2.0 | 1 | 8 | 100% |
| 2024-12-23 | `c11c5047` | WiP - first pass at rewrite for custom backend | 2 | 8 | 100% |
| 2024-12-09 | `637b2151` | Platform Install Page - Fix/Clarify Extras Install | 1 | 8 | 100% |
| 2024-12-06 | `735419c2` | Copilot docs overhaul | 1 | 8 | 100% |
| 2024-12-02 | `0be248ae` | Updates To Settings & Environment Variables Page + Installer Patch Ins | 3 | 8 | 67% |
| 2024-11-25 | `95c6cf36` | csp settings for docs | 2 | 8 | 0% |
| 2024-11-25 | `d338e500` | update custom-backend for endpoint param and type | 1 | 8 | 100% |
| 2024-11-19 | `857c7bfc` | [Platform] Remove GitHub Container Registry Reference From Install | 1 | 8 | 100% |
| 2024-11-19 | `e4920844` | Update COT Page | 1 | 8 | 0% |
| 2024-11-08 | `b6972cdd` | fix TOC on terminal tutorials | 1 | 8 | 100% |
| 2024-11-08 | `680cb01f` | Add Error Section To Platform FAQ & Update Extensions Page. | 3 | 8 | 67% |
| 2024-10-29 | `c088c0bd` | Add instructions on running ngrok to connect open source platform | 1 | 8 | 100% |
| 2024-10-24 | `30b9b64b` | Update docs + S3 bucket pictures | 1 | 8 | 0% |
| 2024-10-10 | `0b21d8bd` | adding instructions for users on safari/brave to do https | 2 | 8 | 0% |
| 2024-10-06 | `7e041c8a` | Update docs & create new tutorials | 6 | 8 | 17% |
| 2024-10-06 | `393db879` | Docs for Platform Installer API - Widget filtering | 5 | 8 | 20% |
| 2024-10-02 | `4fad9bdb` | docs: fix naming and links | 1 | 8 | 0% |
| 2024-10-02 | `5dd33098` | docs: fix typo | 1 | 8 | 0% |
| 2024-09-24 | `41bcab5f` | fix youtube video and broken link | 2 | 8 | 0% |
| 2024-09-16 | `a3a71dbc` | Update Copilot docs (#15) | 2 | 8 | 0% |
| 2024-09-11 | `d86c06ed` | add api endpoints | 3 | 8 | 33% |
| 2024-09-09 | `0b315040` | Update Copilot docs | 1 | 8 | 100% |
| 2024-09-09 | `9fa8b8bf` | [BugFix] Platform Markdown Script - Ensure Reference & Data Model Tabl | 1 | 8 | 100% |
| 2024-09-05 | `8c872cfb` | Overhaul Terminal Pro docs - WIP | 5 | 8 | 20% |
| 2024-08-28 | `36c55617` | Max Python version as 3.12 | 1 | 8 | 100% |
| 2024-08-26 | `0c4ed420` | [BugFix] Fix URL to Data Extensions in CLI Quick Start | 1 | 8 | 100% |
| 2024-07-15 | `7721df5c` | Remove Dev Container from Install Instructions | 1 | 8 | 100% |
| 2024-07-04 | `772bc0b1` | Fix Broken URL | 1 | 8 | 0% |
| 2024-06-24 | `b6d6169e` | fix: format code snippet | 1 | 8 | 0% |
| 2024-06-24 | `1e3cb774` | Update from OpenBBTerminal 'main' c0d0989 | 3 | 8 | 33% |
