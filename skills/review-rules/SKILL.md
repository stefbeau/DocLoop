---
name: review-rules
description: House rules for reviewing a documentation page or a proposed edit, with severities. Use when asked to review a page, or to check a proposal before it goes to a person.
---

# Review rules

Rules a script can check are already checked by `propose_edit` and
`propose_notice`. This skill covers what needs judgement. Report each finding
as: severity, rule, the quoted text, and a paste-ready fix.

## Critical: fix before review

- The page states behaviour the product no longer has.
- A procedure cannot be completed as written: a step is missing or out of order.
- A warning about data loss or cost is absent or buried.

## Important

- The page does not say who it is for or what it lets the reader do, in the
  first two sentences.
- A question-style heading does not answer the question in its first sentence.
- The same thing has two names on one page.
- Internal names, ticket numbers or team jargon appear in customer-facing text.

## Suggestion

- Sentences over 30 words.
- A list of more than seven steps that could be two procedures.
- A paragraph that explains what the interface already shows.

## Writing for retrieval

Assistants answer from single chunks of a page. Check that each section makes
sense on its own: it names the product and the feature, and does not depend on
"as described above".

## How to extend

Add your organisation's rules under the same three severities. Move any rule
that can be checked mechanically into `docloop/rules.py`, so the model stops
spending attention on it.
