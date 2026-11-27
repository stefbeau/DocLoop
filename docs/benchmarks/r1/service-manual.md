# R1: GOV.UK service manual

Corpus at `4efa105e`, folders: service-manual. At most 8 candidates per event.

## Overall

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All scored events | 260 | 56% | 53% | 0.38 | 260 | 8% |

## By period (tune on the older half, report on the newer half)

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| older half | 130 | 43% | 40% | 0.29 | 130 | 7% |
| newer half | 130 | 69% | 66% | 0.46 | 130 | 9% |

## By how the pages were found

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 260 | 56% | 53% | 0.38 | 260 | 8% |

## By number of pages the commit modified

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 page | 221 | 56% | 56% | 0.37 | 221 | 7% |
| 2-3 pages | 25 | 64% | 49% | 0.43 | 25 | 14% |
| 4+ pages | 14 | 50% | 15% | 0.30 | 14 | 13% |

## By length of the commit message

| Group | Events | Hit rate | Mean recall | MRR | Answered | Precision when answered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8-30 words | 109 | 63% | 60% | 0.38 | 109 | 9% |
| under 8 words | 123 | 46% | 45% | 0.33 | 123 | 6% |
| over 30 words | 28 | 71% | 61% | 0.54 | 28 | 11% |

## Commits left out

- 4 × more than 10 pages modified (bulk edit, not one change)
- 26 × no existing page modified (new pages, assets or config only)
- 10 × message shorter than 3 words

## Reading step (openai/gpt-oss-120b:fastest)

2014 model calls, 0 unparsed replies (kept by default).

### If the reader deletes what it does not keep

| Group | Events | Hit rate before | after | Recall before | after | Precision before | after | Pages before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 260 | 56% | 46% | 53% | 44% | 8% | 30% | 8.0 | 2.588 |
| older half | 130 | 43% | 38% | 40% | 34% | 7% | 27% | 8.0 | 2.662 |
| newer half | 130 | 69% | 55% | 66% | 53% | 9% | 34% | 8.0 | 2.515 |

### How well the reader tells right from wrong, and the same-size baseline

| Group | Right pages kept | Wrong pages dropped | Reader: hit rate | recall | Top-k of search: hit rate | recall | k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 80% | 72% | 46% | 44% | 46% | 43% | 3 |
| older half | 82% | 70% | 38% | 34% | 38% | 34% | 3 |
| newer half | 79% | 73% | 55% | 53% | 55% | 52% | 3 |

### If the reader reorders the list instead of deleting

| Group | Right page in top 3, before | after | Recall in top 3, before | after | MRR before | after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 46% | 50% | 43% | 47% | 0.38 | 0.44 |
| older half | 38% | 39% | 34% | 35% | 0.29 | 0.36 |
| newer half | 55% | 61% | 52% | 58% | 0.46 | 0.52 |

## Reading as sorting: likely first, nothing deleted (R1)

Targets, on the newer half: hit rate 90%, recall 80%, precision of the likely list 60%, right pages in likely 95%, wrong pages in also check 85%.

| Group | Events | Hit rate | Recall | Precision, likely | Precision, full list | Right in likely | Wrong in also check | Empty likely |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All judged events | 260 | 56% | 53% | 30% | 8% | 80% | 72% | 38 |
| older half | 130 | 43% | 40% | 27% | 7% | 82% | 70% | 21 |
| newer half | 130 | 69% | 66% | 34% | 9% | 79% | 73% | 17 |

| Group | Right page in top 3, search order | likely first | MRR, search order | likely first |
| --- | ---: | ---: | ---: | ---: |
| All judged events | 46% | 50% | 0.38 | 0.44 |
| older half | 38% | 39% | 0.29 | 0.36 |
| newer half | 55% | 61% | 0.46 | 0.52 |

## Every scored event

| Date | Commit | Message | Truth | Found | Recall |
| --- | --- | --- | ---: | ---: | ---: |
| 2016-10-24 | `b3b7bc43` | Fixed link to the coded example on the prototype kit. | 1 | 8 | 100% |
| 2016-08-28 | `f96d5053` | Use numerals | 1 | 8 | 0% |
| 2016-08-28 | `b1708ea0` | Disambiguate single response question | 1 | 8 | 100% |
| 2016-08-16 | `5eb23d03` | Change to gender question | 1 | 8 | 100% |
| 2016-08-15 | `dc07ad93` | Remove from search content migrated prior to 2016-08-15 | 9 | 8 | 11% |
| 2016-08-08 | `b3c83856` | Fix contact link to the support app | 1 | 8 | 0% |
| 2016-07-22 | `85cd5d0f` | Fix email confirmation link | 1 | 8 | 100% |
| 2016-05-16 | `865b02df` | Remove example, which is an out-of-date survey | 1 | 8 | 100% |
| 2016-04-22 | `6dd3f05d` | Update link to agile business case guidance | 1 | 8 | 100% |
| 2016-04-22 | `b4bca3ad` | Link to Verify onboard process | 1 | 8 | 100% |
| 2016-03-03 | `60a8cede` | Fix formatting | 1 | 8 | 0% |
| 2016-03-03 | `405647d7` | Replacing broken hackpad link | 1 | 8 | 0% |
| 2016-02-24 | `a6fbd31e` | Update service.gov.uk rules with CTS email blueprint | 1 | 8 | 100% |
| 2016-02-24 | `c697baef` | Replace separate SPF and DKIM references with DMARC | 1 | 8 | 100% |
| 2016-02-23 | `f38c4cc4` | Refer to beta services as services, not prototypes | 1 | 8 | 100% |
| 2016-02-21 | `b79daa05` | Add missing apostrophe | 1 | 8 | 0% |
| 2016-02-11 | `e1487ab3` | Fixed a few typos and some grammar | 1 | 8 | 0% |
| 2016-02-07 | `3653fe94` | Map CESG URLs to new paths following website upgrade | 2 | 8 | 50% |
| 2016-02-04 | `39e2e465` | Revert "Remove link to non-working video" | 1 | 8 | 0% |
| 2016-02-01 | `df4c1a0c` | Remove link to non-working video | 1 | 8 | 100% |
| 2016-01-14 | `e6c7fc67` | Define what ‘compliant’ and ‘functional’ means re browsers | 1 | 8 | 100% |
| 2016-01-14 | `58278c21` | Update supported browsers | 1 | 8 | 100% |
| 2016-01-12 | `957e09f2` | Add a missing word: "asked enter" => "asked to enter" | 1 | 8 | 100% |
| 2015-12-16 | `df863adf` | Update “tax disc” start page example | 1 | 8 | 100% |
| 2015-12-16 | `885782a4` | Change “tax disc” to “vehicle tax” in example | 1 | 8 | 100% |
| 2015-12-16 | `88ac0640` | Clarify process for obtaining a service domain | 1 | 8 | 100% |
| 2015-12-16 | `91791592` | Clarify point about start pages (revised) | 1 | 8 | 100% |
| 2015-12-14 | `0c92fc53` | Clarify - most (not all) services get start pages | 1 | 8 | 100% |
| 2015-12-11 | `5bbad117` | Update action-plan.md | 1 | 8 | 0% |
| 2015-12-07 | `3d64480c` | Fix broken link | 1 | 8 | 0% |
| 2015-12-03 | `52242b25` | Update GOV.UK Verify contact details | 1 | 8 | 100% |
| 2015-11-30 | `a5c57f5c` | Use typographic quote marks in infosec content | 1 | 8 | 0% |
| 2015-11-25 | `ac5bd62d` | Turn dashes into em dashes | 1 | 8 | 0% |
| 2015-11-24 | `f6d6a3e2` | Update guidance based on feedback from Hackpad | 1 | 8 | 100% |
| 2015-11-24 | `529d2dc2` | Update infosec guidance to remove outdated concepts | 1 | 8 | 0% |
| 2015-11-23 | `51d95237` | Update foundation-day.md | 1 | 8 | 100% |
| 2015-11-19 | `5669f665` | Update research questions | 1 | 8 | 100% |
| 2015-11-19 | `26b77710` | Update guidance with research questions | 1 | 8 | 0% |
| 2015-11-19 | `d24c91a5` | Minor copy update | 1 | 8 | 0% |
| 2015-11-19 | `229dd084` | Change name of pattern from summary page to check your answers page | 1 | 8 | 0% |
| 2015-11-19 | `a0239872` | Content update - intergrate advice from the previous version of this p | 1 | 8 | 100% |
| 2015-11-17 | `fe4bb0a9` | Add missing link | 1 | 8 | 100% |
| 2015-11-17 | `85720f1d` | Move guidance about next steps into 'research required' section | 1 | 8 | 100% |
| 2015-11-17 | `59762195` | Update index.md | 1 | 8 | 100% |
| 2015-11-17 | `6fccc6c3` | Make image link to example from prototype kit | 1 | 8 | 100% |
| 2015-11-17 | `3b9acf79` | Make image link to example from prototype kit | 1 | 8 | 100% |
| 2015-11-16 | `ac2abcfd` | Update confirmation page pattern | 1 | 8 | 100% |
| 2015-11-16 | `c455fb41` | Add start page example image | 1 | 8 | 100% |
| 2015-11-02 | `917b068f` | Really fix the displaying of bullet points in action_plan.md | 1 | 8 | 0% |
| 2015-10-22 | `4c1ae4a3` | Update action-plan.md | 1 | 8 | 0% |
| 2015-10-20 | `91ed604b` | Correctly render bulleted lists | 1 | 8 | 0% |
| 2015-09-11 | `ba55ca42` | Add missing image, small capitalisation tweaks | 2 | 8 | 0% |
| 2015-10-07 | `e8ca0965` | Update guidance on the progress indicator pattern | 1 | 8 | 100% |
| 2015-10-09 | `683c2808` | Update action-plan.md | 1 | 8 | 0% |
| 2015-10-09 | `58837b03` | Update index.md | 1 | 8 | 0% |
| 2015-10-02 | `7bb1c684` | Update mobile Safari entries in verified browsers | 1 | 8 | 100% |
| 2015-10-02 | `36ddbca2` | Add reference to edds' blog post | 1 | 8 | 0% |
| 2015-10-02 | `31abb2f3` | Update details of emerging platforms/devices | 1 | 8 | 100% |
| 2015-10-02 | `f5ff095e` | Update advice on older IE versions | 1 | 8 | 100% |
| 2015-10-01 | `85cb6ef9` | Update stats on mobile usage | 1 | 8 | 100% |
| 2015-10-01 | `bc1075c1` | Update assisted-digital-user-research.md | 1 | 8 | 100% |
| 2015-09-29 | `488075d4` | Reword SSL certificate validation instructions | 1 | 8 | 100% |
| 2015-09-29 | `2f2546e2` | Update GDS Infrastructure Team to GOV.UK | 1 | 8 | 0% |
| 2015-09-21 | `17304d0d` | Changes to Development environments | 1 | 8 | 100% |
| 2015-09-10 | `278084f1` | Update user satisfaction guidance following comments from content edit | 1 | 8 | 100% |
| 2015-08-13 | `ea840d4e` | Rename 'Done pages' to 'Feedback pages' | 2 | 8 | 100% |
| 2015-08-12 | `87778d5f` | Update guidance on user satisfaction | 1 | 8 | 100% |
| 2015-08-12 | `3dbb3b92` | Update guidance on completion rate | 1 | 8 | 100% |
| 2015-08-12 | `45199bdf` | Clarify the role of the 4 KPIs | 2 | 8 | 100% |
| 2015-09-03 | `f7ad9f67` | Link to CESG guidance on TLS | 1 | 8 | 0% |
| 2015-08-26 | `f421eb4e` | Update procurement session description | 1 | 8 | 100% |
| 2015-08-21 | `dc87e31c` | Fix some line wrapping and add some full stops to foundation-day.md | 1 | 8 | 100% |
| 2015-08-20 | `300a2cf3` | Fix a few lacking full stops, a typo, and table syntax | 1 | 8 | 0% |
| 2015-08-20 | `593378ba` | Properly capitalise DevOps | 3 | 8 | 67% |
| 2015-08-20 | `4a011979` | Fix spacing and table syntax | 1 | 8 | 0% |
| 2015-08-20 | `9f953961` | Update foundation-day.md | 1 | 8 | 100% |
| 2015-08-20 | `ad31f4ac` | Update service-manager-induction.md | 1 | 8 | 100% |
| 2015-08-20 | `5f47451f` | Update open-programme.md | 1 | 8 | 100% |
| 2015-08-03 | `735f1f0c` | Update accessibility.md | 1 | 8 | 100% |
| 2015-08-03 | `1bb2e60c` | Fixed link to exemplar services | 1 | 8 | 0% |
| 2015-08-03 | `d9ed9b7b` | Fix bullet formatting | 1 | 8 | 0% |
| 2015-08-03 | `3bd15578` | Add prompts and evidence and service standard poster | 1 | 8 | 100% |
| 2015-07-31 | `59c07af8` | Don't automatically tab between fields | 1 | 8 | 100% |
| 2015-07-16 | `46578e65` | Update accessibility-testing.md | 1 | 8 | 100% |
| 2015-07-10 | `e77dc1f8` | Update open-programme.md | 1 | 8 | 100% |
| 2015-07-10 | `641fc9d5` | Update open-programme.md | 1 | 8 | 100% |
| 2015-07-08 | `08469ecd` | Update code-of-practice.md | 1 | 8 | 0% |
| 2015-07-07 | `42d47be9` | Update code-of-practice.md | 1 | 8 | 0% |
| 2015-07-07 | `cf937456` | Update code-of-practice.md | 1 | 8 | 100% |
| 2015-07-03 | `bb765f0a` | Fix two typos on form structure design pattern page | 1 | 8 | 100% |
| 2015-07-02 | `ea4af94a` | Fix on-page links | 1 | 8 | 0% |
| 2015-07-02 | `9cd7c1b1` | Add link to Joe's blog post | 1 | 8 | 100% |
| 2015-07-02 | `da66abe4` | Add link to Joe's blog post | 1 | 8 | 0% |
| 2015-06-26 | `7381e97b` | Revise content based on internal feedback | 1 | 8 | 0% |
| 2015-06-26 | `c5c31b1f` | Change wording about DKIM/SPF | 2 | 8 | 100% |
| 2015-06-26 | `2b75e66b` | Add mailto to link | 1 | 8 | 0% |
| 2015-06-04 | `a3d2f596` | Remove reference to 'remember' - we don't recommend this | 1 | 8 | 100% |
| 2015-06-03 | `1e0ea6a9` | Update service manager programme contact details | 1 | 8 | 100% |
| 2015-06-02 | `cce2b4fb` | Make title unique for 26 point Digital by Default Service Standard | 1 | 8 | 100% |
| 2015-05-20 | `5e3355d1` | Revise assessment criteria to 18 points | 1 | 8 | 100% |
| 2015-05-20 | `ae1e32fc` | Move Digital By Default Service Standard with 26 points | 1 | 8 | 100% |
| 2015-05-19 | `3604f93f` | added crown hosting link to page | 1 | 8 | 100% |
| 2015-05-19 | `f4fa5f8d` | Update browser guidance based on latest numbers | 1 | 8 | 100% |
| 2015-05-14 | `ef46e12a` | Fix dashes | 1 | 8 | 0% |
| 2015-05-13 | `97f0c2db` | Clarify guidance on using the word 'sex' instead of 'gender' | 1 | 8 | 100% |
| 2015-05-13 | `e319573a` | Fix broken link in usernames design pattern | 1 | 8 | 100% |
| 2015-05-13 | `29a01add` | Fix section numbering on usernames design pattern | 1 | 8 | 100% |
| 2015-05-06 | `856882be` | Minor style guide list usage change | 2 | 8 | 0% |
| 2015-05-06 | `a5a14054` | Prefer links without .html | 9 | 8 | 11% |
| 2015-05-06 | `e6a2325f` | Style guide dashes | 6 | 8 | 17% |
| 2015-05-06 | `5a3a8378` | Update link text in design pattern | 1 | 8 | 0% |
| 2015-05-06 | `ce6d049a` | Update intro of design patterns index | 1 | 8 | 100% |
| 2015-05-06 | `b8e52089` | Update service-manager-induction.md | 1 | 8 | 100% |
| 2015-05-06 | `93562f37` | Promote hackpad on the design patterns index page | 1 | 8 | 100% |
| 2015-05-06 | `e92e7535` | Fix typos and add references to gender design pattern | 1 | 8 | 100% |
| 2015-05-05 | `0fdbebc6` | Update open-programme.md | 1 | 8 | 100% |
| 2015-05-05 | `129752a3` | Add example image to create username design pattern | 1 | 8 | 100% |
| 2015-05-05 | `61aaddca` | Add examples to create password design pattern | 1 | 8 | 100% |
| 2015-05-05 | `e0d49c2c` | Add example image and update guidance for email address pattern | 1 | 8 | 100% |
| 2015-05-05 | `2b0376f3` | Update email address advice | 1 | 8 | 100% |
| 2015-05-01 | `1e774780` | Add new patterns to index page and restructure links | 1 | 8 | 100% |
| 2015-05-01 | `1ecb07e2` | Update intro on design patterns index page | 1 | 8 | 100% |
| 2015-04-29 | `8072fce0` | Add new description and pre-learning | 1 | 8 | 0% |
| 2015-04-29 | `f140ca51` | Add section to usernames design pattern | 1 | 8 | 100% |
| 2015-04-28 | `f1a0240c` | Grammar tweaks - adding 'to' | 3 | 8 | 33% |
| 2015-04-28 | `2841ff8b` | 1st draft of username and password design patterns | 1 | 8 | 100% |
| 2015-04-15 | `26c79905` | Update spending-controls.md | 1 | 8 | 100% |
| 2015-03-25 | `257aa349` | Added @andyjmk's changes - defect fixes to technology code of practice | 1 | 8 | 100% |
| 2015-03-23 | `9a34ab90` | Style guide usage and accessibility | 1 | 8 | 0% |
| 2015-03-23 | `8a095cf5` | Update to code-of-practice page | 1 | 8 | 0% |
| 2015-03-19 | `c8d7ef20` | Update with forthcoming dates for training | 1 | 8 | 0% |
| 2015-03-06 | `583c7f94` | Details of who AD support needs to be provided for | 1 | 8 | 100% |
| 2015-03-06 | `40b5fb72` | Explain why AD is not always required | 1 | 8 | 100% |
| 2015-03-17 | `24b56dc6` | Moved 'Download' prefix out of link name | 1 | 8 | 100% |
| 2015-03-17 | `6145e39c` | Updated links to persona documents | 1 | 8 | 0% |
| 2015-03-11 | `f3e284f6` | Remove salary guidance page and links to it | 2 | 8 | 50% |
| 2015-03-09 | `8ae4bfc8` | Add link to Hackpad | 1 | 8 | 100% |
| 2015-03-05 | `9cf37c9e` | Fix spacing issue | 1 | 8 | 0% |
| 2015-03-05 | `da3731be` | Update spend control email address | 1 | 8 | 100% |
| 2015-02-18 | `c8a2068e` | Fix spelling mistake | 1 | 8 | 0% |
| 2015-02-18 | `952cc784` | Follow redirected links | 6 | 8 | 0% |
| 2015-02-18 | `5ae6955b` | Fix broken link to FT webapp | 1 | 8 | 0% |
| 2015-02-18 | `60d759bf` | Add missing .html extension | 1 | 8 | 100% |
| 2015-02-18 | `a98e8554` | Add line break to fix markdown links | 1 | 8 | 0% |
| 2015-02-17 | `77184e7a` | Move form structure back to process patterns | 1 | 8 | 100% |
| 2015-02-09 | `f0336f4b` | Update description of detail and process patterns | 1 | 8 | 100% |
| 2015-02-02 | `420ba13b` | Fixed double 'the' in text | 1 | 8 | 0% |
| 2015-02-02 | `f58d5894` | Change order of design patterns to show typical use | 1 | 8 | 100% |
| 2015-02-11 | `457c0008` | Update service-manager-induction.md | 1 | 8 | 100% |
| 2015-01-21 | `2ab15544` | Add hackpad link to NINO pattern | 2 | 8 | 100% |
| 2015-01-16 | `cd2c770c` | Change of request details | 1 | 8 | 100% |
| 2015-01-09 | `ffaae12f` | Governance — Funding a digital service updates | 1 | 8 | 100% |
| 2015-01-06 | `da342846` | Removed 'from private beta'. | 1 | 8 | 100% |
| 2015-01-05 | `b7ba63f6` | typo — added ‘on’ to GOV.UK | 1 | 8 | 0% |
| 2014-12-17 | `848810fa` | Assurance for digital services — governance | 7 | 8 | 14% |
| 2015-01-05 | `f50ff4d2` | Stephen Kelly is no longer COO | 1 | 8 | 0% |
| 2014-12-27 | `600ab465` | Fix broken links | 6 | 8 | 0% |
| 2014-12-24 | `0c62b19b` | Whitespace removal, href fixes, add MPA link | 1 | 8 | 100% |
| 2014-12-20 | `4306ac58` | Lint — replace en dash | 1 | 8 | 0% |
| 2014-12-20 | `5f27c500` | Lint — replace literal em dashes | 6 | 8 | 0% |
| 2014-12-17 | `44b90796` | Add 2015 dates, update sessions and booking link | 1 | 8 | 100% |
| 2014-12-16 | `b36c7bea` | Link to hackpad page was broken | 1 | 8 | 0% |
| 2014-12-14 | `8ce20d5a` | Fix link in technology code of practice | 1 | 8 | 100% |
| 2014-12-09 | `6cc656c1` | Remove comment about May 2013 update | 1 | 8 | 100% |
| 2014-12-09 | `cd815fb1` | Update comment about Digital Procurement Framework | 1 | 8 | 0% |
| 2014-12-08 | `26239f2c` | correct spelling of the word 'approach' | 1 | 8 | 0% |
| 2014-12-05 | `6a48ba1f` | typo fix | 1 | 8 | 0% |
| 2014-12-05 | `8f060707` | Link correction, link added, typo fix | 3 | 8 | 33% |
| 2014-12-03 | `50887cfa` | Minor style changes | 3 | 8 | 0% |
| 2014-12-01 | `d840b497` | Header table fixed | 1 | 8 | 0% |
| 2014-12-01 | `6a512a7d` | Update quality to include exploratory testing | 2 | 8 | 100% |
| 2014-11-26 | `7101d4a8` | typo — missed 'in governance' from end of title | 1 | 8 | 100% |
| 2014-11-26 | `0649b38a` | Copy changes for clarity | 2 | 8 | 0% |
| 2014-11-26 | `5f8d14b5` | typo — missing apostrophe in heading | 1 | 8 | 0% |
| 2014-11-25 | `e65491af` | Clarify cookie link guidance | 1 | 8 | 100% |
| 2014-11-25 | `a5973f33` | Governance — Seeing Progress | 1 | 8 | 0% |
| 2014-11-24 | `fd69b4af` | Update for 2015 cohorts | 1 | 8 | 100% |
| 2014-11-24 | `1cec6c72` | fix minor typo | 1 | 8 | 0% |
| 2014-11-20 | `15b3d1b8` | remove -being fixed- banner or architecture page | 1 | 8 | 0% |
| 2014-11-20 | `63be4b1e` | follow suggestions on update removing banners and cleaning some text | 2 | 8 | 0% |
| 2014-11-19 | `24d8d56b` | typo in arch doc | 2 | 8 | 0% |
| 2014-11-19 | `715f1558` | typo in arch doc | 1 | 8 | 0% |
| 2014-11-19 | `04a8490d` | holding pages for platform architecture | 2 | 8 | 100% |
| 2014-11-18 | `cedba214` | Introduce guidance for 'confirmation' pages | 1 | 8 | 0% |
| 2014-11-18 | `cff75103` | Update the hackpad link for 'done' pages | 1 | 8 | 100% |
| 2014-11-18 | `45a2aa65` | Replace reference to Zendesk with GOV.UK support form. | 1 | 8 | 100% |
| 2014-11-18 | `bc8f2e7b` | Replace reference to Zendesk with GOV.UK support form. | 1 | 8 | 100% |
| 2014-11-18 | `d7780b9b` | Rename 'End pages' to 'Done pages' | 2 | 8 | 50% |
| 2014-11-13 | `b44c4e51` | Remove a redundant line | 1 | 8 | 100% |
| 2014-11-11 | `a13c0493` | Update links to the GOV.UK style guide | 5 | 8 | 40% |
| 2014-11-11 | `627a2f3b` | Update sass-repositories.md | 1 | 8 | 100% |
| 2014-11-10 | `0b98e8d6` | Fix broken link | 1 | 8 | 0% |
| 2014-11-08 | `117c66f0` | Fixed a broken link. | 1 | 8 | 0% |
| 2014-11-05 | `1c7e1dd2` | typo fix on link | 1 | 8 | 0% |
| 2014-11-05 | `5e3dc4c1` | changed index page of governance section to a table contents and made  | 1 | 8 | 0% |
| 2014-11-04 | `f0187cbb` | Fix links to not use .html versions | 1 | 8 | 0% |
| 2014-11-04 | `318c816e` | Add private and public beta descriptions | 1 | 8 | 0% |
| 2014-10-30 | `b0f581d9` | new-assisted-digital-info-added-re-focs-framework | 1 | 8 | 0% |
| 2014-10-27 | `5424d513` | assisted digital fixes | 1 | 8 | 0% |
| 2014-10-28 | `d737513f` | Remove trailing whitespace | 1 | 8 | 0% |
| 2014-10-28 | `687ac585` | Add newline so bullets will render correctly | 1 | 8 | 0% |
| 2014-10-27 | `66e698fb` | update typo | 1 | 8 | 0% |
| 2014-10-27 | `c713132d` | end-user-device | 1 | 8 | 100% |
| 2014-10-24 | `00bb5860` | Style, syntax, render changes | 2 | 8 | 0% |
| 2014-10-20 | `8af8bfdc` | Assisted digital content update | 3 | 8 | 100% |
| 2014-10-17 | `8d4228cb` | Name change 'Governing a service after scaling up' | 3 | 8 | 100% |
| 2014-10-16 | `3cf15df4` | Updates | 1 | 8 | 0% |
| 2014-10-16 | `eac0e9bd` | Link in brackets was missing final bracket | 1 | 8 | 0% |
| 2014-10-16 | `e2e322db` | white space fix | 2 | 8 | 0% |
| 2014-10-16 | `50175304` | second removal of the word empowered | 1 | 8 | 0% |
| 2014-10-16 | `d1add60e` | removal of the word 'empowered' | 1 | 8 | 100% |
| 2014-10-16 | `d7835069` | Revisions to published governance guidance | 4 | 8 | 0% |
| 2014-10-15 | `6448720a` | revisions to governance guidance based on feedback | 7 | 8 | 71% |
| 2014-10-14 | `d54cd27b` | Update guidance | 1 | 8 | 0% |
| 2014-10-08 | `1a4ac044` | Added a link to our free eBook with Retrospective Exercises | 1 | 8 | 100% |
| 2014-10-08 | `3d1fffac` | Add future browsers | 1 | 8 | 100% |
| 2014-10-07 | `b9042ffc` | Update service-manager.md | 1 | 8 | 100% |
| 2014-10-07 | `76811a88` | Update service-manager.md | 1 | 8 | 100% |
| 2014-10-05 | `b6e8ab2c` | Prefer simpler phrase | 1 | 8 | 0% |
| 2014-10-03 | `8e340858` | Upate to sections | 4 | 8 | 0% |
| 2014-10-02 | `d705260b` | ID assurance text changes | 8 | 8 | 50% |
| 2014-09-28 | `5b190530` | Fix typo in agile doc | 1 | 8 | 0% |
| 2014-09-26 | `8c14a2b1` | Fix broken link highlighted by new linkcheck tool | 1 | 8 | 100% |
| 2014-09-25 | `41e1fe64` | - Remove old dates - Add update information | 1 | 8 | 0% |
| 2014-09-24 | `e6f87b24` | Reflect recent rebranding | 1 | 8 | 0% |
| 2014-09-23 | `dd94c4c6` | Fixed the link to Governing the life of a service | 1 | 8 | 100% |
| 2014-09-22 | `79140ebd` | Fix link to governance of live phase | 1 | 8 | 100% |
| 2014-09-22 | `af763913` | recruitment-hub | 1 | 8 | 100% |
| 2014-09-19 | `34cad938` | Fix lint | 1 | 8 | 0% |
| 2014-09-19 | `5a00d761` | Changes to induction pages | 2 | 8 | 0% |
| 2014-09-17 | `88bbbbfb` | Revert "Merge pull request #435 from alphagov/feature/technical-archit | 1 | 8 | 0% |
| 2014-09-17 | `d3589918` | Two links made consistent | 1 | 8 | 100% |
| 2014-09-17 | `bfcd7793` | Prefer links without .html | 1 | 8 | 0% |
| 2014-09-17 | `cef72818` | Remove Nayeema’s email address | 1 | 8 | 100% |
| 2014-09-17 | `cf58ca44` | Typo and link fixes, gemfile.lock put back | 3 | 8 | 33% |
| 2014-08-18 | `4f32ae49` | Initial draft of technical architect role | 1 | 8 | 0% |
| 2014-09-16 | `09d4b387` | Typo, removed unintended extra space after assure | 1 | 8 | 100% |
| 2014-09-16 | `089f55b3` | Governance guidance URLs fixed to be root relative | 8 | 8 | 0% |
| 2014-09-16 | `d863958e` | Governance Guidance | 1 | 8 | 0% |
| 2014-08-28 | `263396b8` | Change start and end pages | 2 | 8 | 100% |
| 2014-08-26 | `b8a9d69a` | Fix typo/gramatical error | 1 | 8 | 0% |
| 2014-08-22 | `7f2fce87` | Change href text | 1 | 8 | 0% |
| 2014-08-21 | `3b221858` | get rid of white space | 1 | 8 | 0% |
| 2014-08-21 | `7d4e4fea` | beta and alpha banner guidance, plus link to index | 1 | 8 | 0% |
| 2014-08-21 | `71cba51c` | sever typo | 1 | 8 | 0% |
| 2014-08-18 | `b89be8a7` | Reflect the name of open document format standard | 7 | 8 | 0% |
| 2014-08-18 | `4085237c` | Remove .html from links | 1 | 8 | 0% |
| 2014-08-15 | `2569d2b7` | Replace h3 with bold | 1 | 8 | 0% |
| 2014-08-15 | `c50364ba` | Revert "Merge pull request #433 from alphagov/feature/simpler-nav" | 1 | 8 | 0% |
| 2014-08-15 | `638213ea` | Assisted digital personas | 1 | 8 | 100% |
| 2014-08-15 | `a9a473ca` | Remove h2 elements | 1 | 8 | 0% |
| 2014-08-13 | `123c0516` | Simplify and apply style guide for lists | 1 | 8 | 0% |
| 2014-08-13 | `f32d2902` | Remove FAQ format | 1 | 8 | 0% |
| 2014-08-13 | `782092ad` | Fix typo highlighted by @waynemoir | 1 | 8 | 100% |
| 2014-08-11 | `c05acee7` | Added full stop | 1 | 8 | 0% |
| 2014-08-11 | `73b332ab` | Added sentence | 1 | 8 | 0% |
| 2014-08-11 | `e5890475` | style guide sweep | 1 | 8 | 0% |
| 2014-08-07 | `a0301055` | Break up long sentence | 1 | 8 | 0% |
| 2014-08-05 | `3084a9c9` | Update Digital by Default introductory text | 1 | 8 | 100% |
| 2014-08-06 | `4a351f19` | Correct DbD wording | 1 | 8 | 100% |
