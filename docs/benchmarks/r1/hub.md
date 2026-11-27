# R1: Hugging Face Hub docs

Corpus at `2c3f84c8`, folders: docs/hub, docs/inference-providers. At most 8 candidates per event.

## Overall

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All scored events | 186 | 89% | 81% | 0.70 | 186 | 17% |

## By period (tune on the older half, report on the newer half)

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| older half | 93 | 86% | 78% | 0.67 | 93 | 16% |
| newer half | 93 | 91% | 85% | 0.73 | 93 | 18% |

## By how the pages were found

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| explicit reference | 20 | 100% | 88% | 0.70 | 20 | 24% |
| hybrid | 166 | 87% | 81% | 0.69 | 166 | 16% |

## By number of pages the commit modified

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 page | 110 | 86% | 86% | 0.68 | 110 | 11% |
| 2-3 pages | 59 | 93% | 80% | 0.70 | 59 | 23% |
| 4+ pages | 17 | 94% | 61% | 0.75 | 17 | 38% |

## By length of the commit message

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8-30 words | 67 | 84% | 77% | 0.66 | 67 | 13% |
| over 30 words | 87 | 95% | 86% | 0.75 | 87 | 22% |
| under 8 words | 32 | 81% | 78% | 0.62 | 32 | 11% |

## Commits left out

- 4 × more than 10 pages modified (bulk edit, not one change)
- 3 × no existing page modified (new pages, assets or config only)
- 107 × message matches --skip-message (\(automated\))

## Reading step (openai/gpt-oss-120b:fastest)

1488 model calls, 0 unparsed replies (kept by default).

### If the reader deletes what it does not keep

| Group | Events | Hit rate before | after | Recall before | after | Precision before | after | Pages before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 186 | 89% | 77% | 81% | 68% | 17% | 56% | 8.0 | 2.387 |
| older half | 93 | 86% | 71% | 78% | 63% | 16% | 54% | 8.0 | 2.505 |
| newer half | 93 | 91% | 83% | 85% | 72% | 18% | 59% | 8.0 | 2.269 |

### How well the reader tells right from wrong, and the same-size baseline

| Group | Right pages kept | Wrong pages dropped | Reader: hit rate | recall | Top-k of search: hit rate | recall | k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 83% | 81% | 77% | 68% | 76% | 62% | 2 |
| older half | 84% | 79% | 71% | 63% | 77% | 66% | 3 |
| newer half | 83% | 84% | 83% | 72% | 78% | 64% | 2 |

### If the reader reorders the list instead of deleting

| Group | Right page in top 3, before | after | Recall in top 3, before | after | MRR before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 79% | 86% | 67% | 74% | 0.70 | 0.77 |
| older half | 77% | 82% | 66% | 70% | 0.67 | 0.72 |
| newer half | 81% | 90% | 69% | 79% | 0.73 | 0.81 |

## Reading as sorting: likely first, nothing deleted (R1)

Targets, on the newer half: hit rate 90%, recall 80%, precision of the likely list 60%, right pages in likely 95%, wrong pages in also check 85%.

| Group | Events | Hit rate | Recall | Precision, likely | Precision, full list | Right in likely | Wrong in also check | Empty likely |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 186 | 89% | 81% | 56% | 17% | 83% | 81% | 16 |
| older half | 93 | 86% | 78% | 54% | 16% | 84% | 79% | 8 |
| newer half | 93 | 91% | 85% | 59% | 18% | 83% | 84% | 8 |

| Group | Right page in top 3, search order | likely first | MRR, search order | likely first |
| --- | ---: | ---: | ---: | ---: |
| All judged events | 79% | 86% | 0.70 | 0.77 |
| older half | 77% | 82% | 0.67 | 0.72 |
| newer half | 81% | 90% | 0.73 | 0.81 |

## Every scored event

| Date | Commit | Message | Truth | Found | Recall |
| --- | --- | --- | ---: | ---: | ---: |
| 2026-11-25 | `2c3f84c8` | [Buckets] Document hf://buckets as iceberg storage | 1 | 8 | 100% |
| 2026-11-25 | `e3687a9b` | Use nvidia/HelpSteer2 in the SQL Console regex example | 1 | 8 | 100% |
| 2026-11-25 | `08d6e01f` | Spaces OAuth: deprecate client secret in favor of PKCE + SPACE_SIGNING | 2 | 8 | 50% |
| 2026-11-25 | `432d4a32` | Document the Require repository-scoped tokens policy | 5 | 8 | 60% |
| 2026-11-25 | `ebde65a3` | Document blog analytics CSV export in Publisher Analytics | 2 | 8 | 100% |
| 2026-11-24 | `725af5b3` | document .sog gaussian splat previews in the 3d file viewer | 1 | 8 | 100% |
| 2026-11-24 | `35326521` | Add a Nightwatch alert example for a dataset made public | 1 | 8 | 100% |
| 2026-11-24 | `c394f623` | Label the data sources in the Nightwatch diagram | 1 | 8 | 100% |
| 2026-11-24 | `8828cef3` | Document Nightwatch for Enterprise customers | 1 | 8 | 0% |
| 2026-11-24 | `61f23e0d` | Replace deleted example Spaces in Spaces docs | 3 | 8 | 33% |
| 2026-11-24 | `6261bb53` | Fix dead torchcodec and vetiver links in Hub docs | 2 | 8 | 0% |
| 2026-11-23 | `58f8f5b9` | list Enterprise pricing as custom | 1 | 8 | 100% |
| 2026-11-23 | `197dda8a` | Fix broken ZenML documentation links in Spaces guide | 1 | 8 | 100% |
| 2026-11-23 | `7ea1f55d` | docs(publisher-analytics): drop empty-case parenthetical from path row | 1 | 8 | 100% |
| 2026-11-20 | `22e95b7b` | Fix ACCELERATOR and MEMORY descriptions for Jobs env vars | 1 | 8 | 100% |
| 2026-11-20 | `d475cc23` | Resource Groups: org admins can invite external collaborators without  | 3 | 8 | 100% |
| 2026-11-19 | `37ae8ca8` | Download Analytics: egress total is over the last 30 days | 1 | 8 | 100% |
| 2026-11-18 | `6057ca72` | document openrouter broadcast traces in the agent traces and bucket in | 2 | 8 | 100% |
| 2026-11-18 | `4c72f815` | Docs: pre-release model pages | 2 | 8 | 100% |
| 2026-11-17 | `444be2a2` | [Inference Providers] Align two guides with the new routing | 2 | 8 | 100% |
| 2026-11-17 | `d28c0ba5` | Buckets S3: add a restic/kopia backup example | 1 | 8 | 100% |
| 2026-11-17 | `3893e111` | docs(publisher-analytics): add path column to advanced export schema | 1 | 8 | 100% |
| 2026-11-16 | `45393883` | Update section title for clarity on analytics | 1 | 8 | 100% |
| 2026-11-16 | `cad2ce70` | Inference Providers docs update | 10 | 8 | 30% |
| 2026-11-16 | `6fa0289f` | Update SCIM-managed Resource Groups docs: role overrides, no service a | 2 | 8 | 50% |
| 2026-11-16 | `3212a1dc` | Document automatic expiration of access tokens unused for a year | 2 | 8 | 100% |
| 2026-11-16 | `819a5a83` | Document credit expiry dates and reminders in billing FAQ | 1 | 8 | 100% |
| 2026-11-13 | `1ae50230` | Update Pi with llama cpp setup | 1 | 8 | 100% |
| 2026-11-13 | `4754ccb6` | Add Rapid-MLX to Hub local cache applications | 1 | 8 | 100% |
| 2026-11-12 | `89c2517a` | [Inference Providers] Document that org provider settings apply to org | 1 | 8 | 100% |
| 2026-11-12 | `df23f0d9` | Document request-gated-repos OAuth scope and gated repo permissions | 4 | 8 | 100% |
| 2026-11-10 | `79469522` | Add "Removing Sensitive Data" page | 2 | 8 | 50% |
| 2026-11-09 | `2702d861` | Buckets: recommend <namespace>.s3.hf.co as the S3 endpoint | 2 | 8 | 100% |
| 2026-11-09 | `610ed94d` | Clarify how cards link to papers and show the sidebar papers list | 5 | 8 | 100% |
| 2026-11-09 | `28e313ac` | [3d datasets docs]: restructure the page with format examples and view | 1 | 8 | 100% |
| 2026-11-09 | `94381314` | Add Zephon to Datasets Libraries documentation | 1 | 8 | 0% |
| 2026-11-09 | `5be3d969` | docs: Container Images access control and resource groups | 1 | 8 | 100% |
| 2026-11-06 | `24e8aa5b` | Remove Nscale text-to-image support from providers table | 1 | 8 | 100% |
| 2026-11-06 | `6e8b9068` | Update hardware reference from H100s to H200s | 1 | 8 | 100% |
| 2026-11-06 | `729817fc` | [3d datasets docs]: document 3d previews, mesh columns and the simread | 1 | 8 | 100% |
| 2026-11-06 | `38d38591` | document service account tokens skip token approval | 1 | 8 | 100% |
| 2026-11-06 | `5924f534` | Update repo counts | 1 | 8 | 0% |
| 2026-11-05 | `2f7e5865` | managed org doc edit | 1 | 8 | 0% |
| 2026-11-05 | `1fd5a44a` | Document SSO authorization for access tokens and SSH keys | 3 | 8 | 33% |
| 2026-11-04 | `cb4181e0` | docs(xet): update hf_xet settings and telemetry for 1.8.0 | 1 | 8 | 100% |
| 2026-11-04 | `0eb8d434` | docs(xet): update HF_XET_CLIENT_READ_TIMEOUT default to 300s | 1 | 8 | 100% |
| 2026-11-04 | `eac949a2` | docs(xet): document direct-to-S3 uploads and the S3 hostnames to allow | 4 | 8 | 100% |
| 2026-11-04 | `a60b4ecd` | Buckets: list libraries with built-in bucket support | 3 | 8 | 67% |
| 2026-11-04 | `d98de708` | Update TRL support status and add LeRobot | 1 | 8 | 0% |
| 2026-11-03 | `170e64cb` | [Docs] Clarify hf_xet download chunk cache behavior | 1 | 8 | 100% |
| 2026-11-03 | `7ef6935c` | Buckets: add a Migration Guide | 3 | 8 | 100% |
| 2026-11-03 | `963dbe23` | Update dataset libraries table | 1 | 8 | 100% |
| 2026-11-03 | `92d1e147` | [Hub/Eval] Document leaderboard.base_models_only option in eval.yaml s | 1 | 8 | 100% |
| 2026-10-30 | `7b31ef10` | Document read-only repo trusted publishers | 2 | 8 | 100% |
| 2026-10-29 | `c88d9c79` | Document transferring a personal OAuth app to an organization | 2 | 8 | 100% |
| 2026-10-29 | `59dd2c17` | drop models from the 3d file preview docs. | 1 | 8 | 100% |
| 2026-10-29 | `7e4b0bb6` | update llama.cpp guide to unified commands | 1 | 8 | 100% |
| 2026-10-29 | `84fa8b0d` | Document organization-owned OAuth apps, their audit log events and the | 2 | 8 | 100% |
| 2026-10-28 | `ac26a585` | Update local apps docs | 1 | 8 | 100% |
| 2026-10-28 | `6649d53c` | docs: update relative links from ./datasets-viewer to ./data-studio | 3 | 8 | 0% |
| 2026-10-28 | `765a965a` | Datasets libraries: fix upload section errors | 1 | 8 | 100% |
| 2026-10-28 | `424d8363` | Buckets: DuckDB writes to buckets with the hf extension | 1 | 8 | 100% |
| 2026-10-28 | `494cad61` | Align LLM dataset upload guide limits with storage-limits | 1 | 8 | 100% |
| 2026-10-27 | `e07d7c97` | Docs: Write to buckets or datasets with DuckDB | 4 | 8 | 50% |
| 2026-10-27 | `fdd66295` | Buckets: point Python users to HfFileSystem live_follow | 1 | 8 | 100% |
| 2026-10-27 | `5b7163b7` | Remove the Register as an Inference Provider guide | 1 | 8 | 100% |
| 2026-10-27 | `f2ea15fe` | Update network security IP Ranges docs for the new range list UI | 1 | 8 | 100% |
| 2026-10-27 | `516efc7c` | Document hiding models from benchmark leaderboards | 1 | 8 | 100% |
| 2026-10-26 | `d821c32b` | Add Migrating to Managed SSO guide | 1 | 8 | 100% |
| 2026-10-26 | `0cf1b3c3` | Document per-brand hardware pages on the Hub | 1 | 8 | 100% |
| 2026-10-23 | `faaeaa06` | Jobs: document hf jobs stats -f | 1 | 8 | 100% |
| 2026-10-23 | `adadb1b8` | docs: delete container tags from the Hub, and garbage collection | 1 | 8 | 100% |
| 2026-10-23 | `1ce2794c` | Document S3 credentials for service account tokens | 3 | 8 | 100% |
| 2026-10-23 | `83a805d0` | Document option to skip collecting requester username/email on gated r | 3 | 8 | 100% |
| 2026-10-22 | `4ec6139c` | document editing a paper's media for authors and daily papers submitte | 1 | 8 | 100% |
| 2026-10-22 | `cf3c1b14` | Fix docs drift: Skills install command, Space pause/restart, org blog  | 6 | 8 | 33% |
| 2026-10-22 | `443cc31f` | Document native hf://buckets/ support in DuckDB (2.0+) | 4 | 8 | 100% |
| 2026-10-22 | `c21d994f` | Local cache: document the shared blob store | 1 | 8 | 100% |
| 2026-10-22 | `3a3fd2a9` | Passkeys and unified two-factor authentication docs | 2 | 8 | 100% |
| 2026-10-22 | `78a3e235` | doc: external collaborator on repo settings | 5 | 8 | 80% |
| 2026-10-21 | `b7dc0905` | Update external collaborators section for clarity | 1 | 8 | 100% |
| 2026-10-21 | `c2b74f31` | Document when cloud marketplace billing takes effect after approval | 1 | 8 | 100% |
| 2026-10-21 | `0b94dd1d` | Document that deleting a payment method cancels the subscription and h | 1 | 8 | 100% |
| 2026-10-20 | `6619ee05` | Document Nvidia RTX PRO 6000 hardware for Spaces | 3 | 8 | 100% |
| 2026-10-20 | `58f53072` | update agent traces docs for hermes and droid | 2 | 8 | 100% |
| 2026-10-15 | `5493982a` | Mention org plan requirement badges in the OpenAPI reference | 1 | 8 | 0% |
| 2026-10-15 | `8b59e8ca` | Document when org blog articles are featured on /blog | 1 | 8 | 100% |
| 2026-10-13 | `db72268a` | replace managed org step with sso prerequisite note in scim guides | 2 | 8 | 100% |
| 2026-10-13 | `bde5a40f` | use okta user id as saml name id and stop scim lockouts | 2 | 8 | 100% |
| 2026-10-13 | `ef42b8f9` | Add the agentenv RL environment framework tag | 1 | 8 | 100% |
| 2026-10-09 | `aab9d7b5` | Add Service Accounts row to Enterprise plans comparison | 1 | 8 | 100% |
| 2026-10-07 | `c708a9e9` | docs(inference-providers): free users no longer get included monthly c | 6 | 8 | 50% |
| 2026-10-06 | `612e0ffb` | docs(xet): add hf_xet telemetry page | 2 | 8 | 50% |
| 2026-10-06 | `3c615a74` | docs(xet): document memory-based download buffer defaults in hf_xet 1. | 2 | 8 | 100% |
| 2026-10-06 | `be20ce24` | state 2GB limitation on malware scan | 1 | 8 | 100% |
| 2026-10-06 | `a6850828` | Local cache: LlamaBarn was renamed to Llama-macOS | 1 | 8 | 100% |
| 2026-10-06 | `5fbaa491` | [Inference Providers] Document the organization usage API endpoint | 1 | 8 | 100% |
| 2026-10-03 | `009b6244` | Update Fal inference provider description | 1 | 8 | 100% |
| 2026-10-02 | `35dea5dd` | Add a Diffusers section to Train Models on Jobs | 1 | 8 | 100% |
| 2026-10-01 | `43e614de` | Jobs: document retries, rerun and reschedule | 3 | 8 | 67% |
| 2026-10-01 | `40146396` | Jobs webhooks: document secrets for Job-triggered webhooks | 1 | 8 | 100% |
| 2026-10-01 | `f5cdf351` | Jobs: document public ports and changing ports on a running Job | 2 | 8 | 100% |
| 2026-10-01 | `b1143ffb` | Fix two moved links | 2 | 8 | 0% |
| 2026-10-01 | `b6c0e7d2` | Add a webhook guide for processing new bucket files with Jobs | 3 | 8 | 100% |
| 2026-10-01 | `74596850` | Clarify SSO resource group mapping sync behavior | 1 | 8 | 100% |
| 2026-09-30 | `eba41100` | Recommend upload_folder / hf upload for large uploads | 2 | 8 | 50% |
| 2026-09-30 | `1143bdeb` | Document the built-in SPACE_SIGNING_SECRET Spaces environment variable | 1 | 8 | 100% |
| 2026-09-30 | `23f6f6fd` | Say "train or fine-tune" where the Jobs docs link to Train Models | 3 | 8 | 33% |
| 2026-09-30 | `37480fe2` | Bucket live follow: clarify resuming, drop xetHash access caveat | 1 | 8 | 100% |
| 2026-09-28 | `761bb84c` | Link Axolotl's Hugging Face Jobs guide from Train Models | 1 | 8 | 100% |
| 2026-09-28 | `a14593bd` | Update outdated tool instructions | 3 | 8 | 67% |
| 2026-09-28 | `3477a59f` | Fix tip rendering | 1 | 8 | 0% |
| 2026-09-28 | `bb8e7c53` | docs: fix wording in Spaces dev mode guide | 1 | 8 | 100% |
| 2026-09-28 | `59ee10b7` | docs: fix wording in models uploading guide | 1 | 8 | 100% |
| 2026-09-28 | `d2afcf09` | Fix four in-page anchors that no longer match their headings | 4 | 8 | 0% |
| 2026-09-28 | `3730d59e` | Add quotes so that it works on fish shell too | 1 | 8 | 0% |
| 2026-09-28 | `8dfa2030` | Drop --claude flag from hf skills add instructions | 1 | 8 | 100% |
| 2026-09-28 | `f78ae550` | Update hub-sync action to v0.3.0 in the GitHub Actions docs | 2 | 8 | 100% |
| 2026-09-28 | `710c629e` | Fix image links in model cards user studies | 1 | 8 | 100% |
| 2026-09-25 | `b3a8d175` | Add a Train Models page to the Jobs docs | 5 | 8 | 60% |
| 2026-09-24 | `5bb6683d` | Add hfdask to Jobs community projects | 1 | 8 | 100% |
| 2026-09-24 | `f17f0b0b` | Document Google Cloud Marketplace as a billing option | 1 | 8 | 100% |
| 2026-09-23 | `33ce0739` | docs: document the reset status for gated repo access requests | 2 | 8 | 100% |
| 2026-09-21 | `0249c808` | Dask: show streaming read/write in bucket integrations | 1 | 8 | 100% |
| 2026-09-21 | `0478904f` | Rework the Jobs images page: ready-made images vs your own Docker Spac | 5 | 8 | 20% |
| 2026-09-17 | `8dc2b054` | Fix dead coding-agent skill link on the Jobs examples page | 1 | 8 | 100% |
| 2026-09-17 | `f88183be` | Document the bucket live-follow (server-sent events) endpoint | 3 | 8 | 67% |
| 2026-09-17 | `6b1976f7` | Document the [tool.hf-jobs] launch config in UV scripts | 1 | 8 | 100% |
| 2026-09-17 | `6b4955a8` | fix: correct environment tag | 1 | 8 | 0% |
| 2026-09-17 | `a71ccba2` | docs: document environment dataset tags | 1 | 8 | 0% |
| 2026-09-16 | `f189d075` | Improve Jobs docs onboarding and Quickstart | 3 | 8 | 100% |
| 2026-09-15 | `ffbbd5ca` | Fix tokens management doc: token-id revoke API + 50 admin notification | 1 | 8 | 100% |
| 2026-09-15 | `66e6b6a8` | Document the audit log export API endpoint | 1 | 8 | 100% |
| 2026-09-16 | `41972b8a` | Document that webhook handlers must answer with a 2xx status | 1 | 8 | 100% |
| 2026-09-15 | `bea532be` | Clarify Jobs costs and link to spending controls | 1 | 8 | 100% |
| 2026-09-15 | `40cb2a42` | [Jobs] Document network groups | 1 | 8 | 0% |
| 2026-09-15 | `65ee22df` | Update Resource Groups docs for the redesigned UI | 2 | 8 | 100% |
| 2026-09-15 | `a2e6245b` | Update Pi links to the renamed repo and npm package | 3 | 8 | 33% |
| 2026-09-14 | `ce2eaa9a` | docs: fix 'allows to load' grammar in Asteroid Hub guide | 1 | 8 | 100% |
| 2026-09-07 | `d035e18f` | [ZeroGPU] Update PyTorch versions | 1 | 8 | 100% |
| 2026-09-04 | `41cf54a5` | Clarify Jobs argument forwarding | 1 | 8 | 100% |
| 2026-09-04 | `8ee62b1b` | Clarify Python package reuse with Jobs framework images | 2 | 8 | 100% |
| 2026-09-03 | `8d9df7fd` | [Inference Providers] drop the conversational tag requirement | 2 | 8 | 100% |
| 2026-09-03 | `26ed3807` | Document the Webhook-Id delivery header | 2 | 8 | 100% |
| 2026-09-02 | `2263fcd8` | Fix resource-group Jobs billing instructions | 1 | 8 | 100% |
| 2026-08-29 | `fc93a745` | Document Network Security exemption for service account tokens | 2 | 8 | 100% |
| 2026-08-28 | `b76e80aa` | doc(webhook): Add bucket webhook | 1 | 8 | 100% |
| 2026-08-28 | `d9283a9a` | Jobs: document auto-generated names and fix the labels example | 1 | 8 | 100% |
| 2026-08-27 | `5eef6295` | Buckets: document changing visibility after creation | 1 | 8 | 100% |
| 2026-08-27 | `8f7e93ee` | Jobs: update the Filter Jobs section for --status / --label / --name | 1 | 8 | 100% |
| 2026-08-25 | `a0eeda80` | Document optional Inference Providers access for user trusted publishe | 1 | 8 | 100% |
| 2026-08-24 | `b8f5fa52` | Reference /.well-known/meta.json in proxy and firewall allowlists | 2 | 8 | 100% |
| 2026-08-22 | `242f4a1e` | Clarify "Higher Hub rate limits" | 2 | 8 | 100% |
| 2026-08-21 | `a9fef576` | included sub credits are now compute credits | 6 | 8 | 83% |
| 2026-08-19 | `efd21b8f` | Update academia-hub.md with new logo Dartmouth College | 1 | 8 | 100% |
| 2026-08-18 | `72e35afe` | Document monthly spend limits per resource group | 3 | 8 | 67% |
| 2026-08-18 | `e6812941` | Add DataTrove to Jobs examples | 1 | 8 | 100% |
| 2026-08-18 | `19d2f1d4` | Document the read-memberships OAuth scope | 2 | 8 | 100% |
| 2026-08-13 | `dbf81083` | agents-cli: reflect the hf-cli skill auto-install (huggingface_hub v1. | 2 | 8 | 100% |
| 2026-08-12 | `741d7725` | Cross-link restrictable-feature docs to Feature access section | 3 | 8 | 67% |
| 2026-08-12 | `688fba08` | Document per-resource-group feature access for organizations | 3 | 8 | 100% |
| 2026-08-12 | `3cd2b170` | Add tip for retrieving short-lived HF token via CLI | 1 | 8 | 100% |
| 2026-08-11 | `bdaaeeb2` | Rename SCIM Step 0 heading and add it to Entra ID doc | 2 | 8 | 100% |
| 2026-08-12 | `115fff4a` | Document read-endpoints / write-endpoints OAuth scopes | 2 | 8 | 100% |
| 2026-08-10 | `0a5d1e69` | Update Together provider support status | 1 | 8 | 100% |
| 2026-08-07 | `a63fdc38` | update scim doc for accuracy | 1 | 8 | 0% |
| 2026-08-07 | `c74dc583` | Document public token revocation endpoint | 3 | 8 | 67% |
| 2026-08-06 | `12c57214` | Count modular_model_index.json downloads for diffusers repos | 1 | 8 | 100% |
| 2026-08-06 | `77973ff7` | Add Baseten inference provider docs | 4 | 8 | 50% |
| 2026-08-05 | `f16d9eb4` | Document redirect URI matching rules and the loopback port exception | 1 | 8 | 100% |
| 2026-08-05 | `95f022d4` | Address julien-c's review comments on hardware API docs | 1 | 8 | 100% |
| 2026-08-04 | `606330bd` | Document API access to user hardware items | 1 | 8 | 0% |
| 2026-07-31 | `bb345afc` | docs(xet): document shard/chunk cache and other Xet environment variab | 1 | 8 | 100% |
| 2026-07-29 | `059eb9f4` | fix and add download analytics page | 1 | 8 | 0% |
| 2026-07-24 | `8cd5e456` | Document 'Keep repository metadata visible' Content Access Policy opti | 1 | 8 | 100% |
| 2026-07-24 | `c62a35f9` | add per repo consideration to docs | 1 | 8 | 0% |
| 2026-07-24 | `a7735fa2` | Update model-page Deploy to Spaces flow to reflect AI agent build prom | 1 | 8 | 0% |
| 2026-07-22 | `663405ca` | Refresh docs. The Hub Search and Details tool is omitted | 1 | 8 | 100% |
| 2026-07-21 | `86be61b3` | Document publisher gating download blocking and blocked regions | 1 | 8 | 100% |
| 2026-07-21 | `34ee0f00` | Update Spaces docs: paid plan required for compute Spaces, ZeroGPU fre | 6 | 8 | 50% |
| 2026-07-21 | `5873e81f` | Add SkyPilot to storage bucket integrations | 2 | 8 | 100% |
| 2026-07-21 | `049a2816` | Mention hf datasets sql in the datasets DuckDB and Data Studio docs | 4 | 8 | 75% |
| 2026-07-20 | `63e84c74` | Jobs: document names and label updates (huggingface_hub v1.24.0) | 2 | 8 | 50% |
| 2026-07-20 | `b45fb365` | Add Jobs guide: Process Large Datasets | 1 | 8 | 100% |
| 2026-07-17 | `ba3f0460` | Jobs: add "Persist your results" section | 2 | 8 | 0% |
| 2026-07-16 | `cf313025` | Document proxy/firewall hostnames for dataset downloads | 2 | 8 | 100% |
