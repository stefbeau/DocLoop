---
name: corpus-census
description: How to audit whether an AI search index matches the documentation it is supposed to serve, using corpus_census. Use when asked whether the assistant can find the docs, why it cites deleted pages, or for a docs health check.
---

# Corpus census

The documentation system knows which pages exist. The search index knows
which pages an assistant can serve. The census compares the two.

## Run it

Call `corpus_census` with the path of an index listing:
`{"entries": [{"id": "...", "visibility": "public"}]}`. Export that listing
from your vector store or search service.

## Read the findings

| Finding | Meaning | Usual cause |
| --- | --- | --- |
| Blind spots | Public pages the index does not hold | No ingestion on publish |
| Ghosts | Deleted pages the index still serves | No delete event reaches the index |
| Wrongly suppressed | Public pages indexed as internal | Visibility flag out of sync |
| Leaked internal | Internal pages indexed as public | Same, in the dangerous direction |

Report leaked internal pages first. They are an exposure, not a quality issue.

## Before you report a number

A first pass always overcounts. For each finding type:

1. Confirm both listings were taken on the same day. Never compare a fresh
   index with an old export.
2. Check three pages by hand in the live system.
3. Rule out aliases: the same page under two ids.

State the date of each listing in the report, and say which findings you
verified by hand and which you did not.
