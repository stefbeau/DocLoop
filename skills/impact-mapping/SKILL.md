---
name: impact-mapping
description: How to decide which documentation pages a product change really affects, starting from search candidates. Use when find_affected_pages returns search results rather than explicit references, or returns nothing.
---

# Impact mapping

The goal is a short, correct list. A confident wrong page costs the reviewer
more than a missing one.

## Order of evidence

1. **Pages the event names.** Final. Do not add to them.
2. **Pages that state the old behaviour.** Read each search candidate and look
   for the sentence the change makes false. If you can quote that sentence,
   the page is affected.
3. **Pages that list or link the feature.** Tables of formats, option lists,
   "see also" sections. Affected only if the listed item changes.

## Checks before you keep a page

- You read it with `read_page`. A title match is not enough.
- You can point to the exact lines that must change.
- It is the canonical place for that fact. If two pages state it, keep both
  and flag the duplication in your report.

## Widening the search

If nothing fits, try `search_pages` with the user-facing name of the feature,
then with the menu path, then with the old name. Stop after three queries. If
you still have nothing, report "no affected page found" and list the queries
you tried. That is a valid result: the page may not exist yet.

## Two piles, not one

Sort what you read into **likely** and **also check**. A page you cannot
tie to a specific sentence goes to also check, not in the bin: the reviewer
sees both piles and decides.

## Never

- Never return an id you did not get from a tool.
- Never propose an edit to an also-check page.
- Never drop a candidate without listing it.
