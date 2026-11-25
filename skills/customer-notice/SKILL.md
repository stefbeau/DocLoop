---
name: customer-notice
description: How to draft a customer-facing notice about a product change and submit it with propose_notice. Use when the route includes a notice step.
---

# Customer notice

A notice tells customers what changes, when, and what they must do. A person
reviews and sends it. You only draft.

## Shape

- **Subject:** `<Product>: <what changes> <date>`. Full product name. For a
  change or retirement, the date is in the subject.
- **First sentence:** the change and the date.
- **Second sentence:** what the customer should do, or that no action is needed.
- **Last sentence:** where to get help.

## Rules

- Dates as DD-MON-YYYY. Add a time and time zone only if the event gives one.
- Second person, active voice, present or future tense.
- No contractions, no apology, no marketing adjectives.
- Under 180 words. Most notices need fewer than 80.
- Say only what the change event supports. If the date or the replacement is
  missing, stop and ask; do not write around the gap.

## Timing, for your report

- Retirements and behaviour changes: recommend sending at least two weeks
  before the date.
- Enhancements: on or after release.

Call `propose_notice`, fix the lint issues it reports, and include the
recommended send timing in your final report.
