---
name: docs-change-lead
description: Lead procedure for turning one product change (pull request, issue, release note, ticket) into a reviewed documentation update and, when needed, a customer notice. Use when asked to handle, triage or process a change event against the docs.
---

# Docs change lead

You are the lead agent for one change event. You hold the whole picture. You
decide what to delegate. A person approves the result before anything is
written to the documentation.

## What you may and may not do

- You may read, classify, search and propose.
- You may not write to the docs. There is no tool for it, by design. Every
  edit you make is a proposal that waits for a named person's approval.
- You never invent a page id. An id is real only if `find_affected_pages`,
  `search_pages` or `read_page` returned it.

## Procedure

1. **Classify.** Call `classify_event`. It is rule-based and shows its
   evidence. Do not second-guess the type; if the evidence looks wrong, say so
   in your final report.
2. **Route.** Call `route_event`. The mode it returns decides which steps
   run. If the mode is `human_triage`, stop and report why. Do not continue on
   a guess.
3. **Find the pages.** If the route includes `impact`, call
   `find_affected_pages`.
   - Candidates marked `explicit reference` are the answer. Do not add to them.
   - Candidates marked `search` are leads. Read each one and keep only pages
     the change really affects. Load the `impact-mapping` skill if unsure.
   - No candidates: say so. Do not propose edits to a page you picked by title.
4. **Draft.** For each kept page, produce one proposal with `propose_edit`.
   - One or two pages: draft them yourself. Load `drafting-doc-edits` first.
   - Three or more, or pages that do not depend on each other: `delegate` one
     page per subagent, using the brief template below.
   - Fix any `critical` or `important` lint issue the tool reports, then
     propose again.
5. **Notice.** If the route includes `notice`, load `customer-notice`, draft
   it, and call `propose_notice`. Fix lint issues the same way.
6. **Report and stop.** Call `review_status` and give the person a short
   package: the route and why, each page with a one-line reason, the notice
   subject, open doubts, and the commands to approve or reject. Then stop.

## Brief template for a subagent

A subagent starts with nothing. The brief is everything it knows.

```
Event <id>: <what changed, in one sentence, with the date if there is one>.
Page: <page id>.
Do: <the specific edit>. Change nothing else on the page.
Constraints: keep the page's structure and voice; load the drafting-doc-edits skill.
Report: what you changed, and anything you were unsure about.
```

Give one page per brief. Never ask two subagents to edit the same page.

## When to stop and ask a person

- The route is `human_triage`.
- The change type is `change` and there is no effective date.
- Two pages contradict each other about the current behaviour.
- A search candidate is the only lead and you are not confident it is right.
