---
name: drafting-doc-edits
description: How to draft a minimal, reviewable edit to one existing documentation page and submit it with propose_edit. Use before proposing any page edit.
---

# Drafting documentation edits

A reviewer will read your change as a diff. Make the diff small and the
reason obvious.

## Method

1. Read the page with `read_page`.
2. Find every sentence the change makes false or incomplete. Edit those and
   nothing else.
3. Keep the page's structure, heading levels, terminology and voice. If the
   page says "Select", do not write "Click".
4. For a retirement or behaviour change, state the date once, in the format
   the page already uses, or DD-MON-YYYY if it uses none.
5. Do not describe a screenshot you cannot see. Replace an outdated image with
   a clearly marked placeholder such as
   `[screenshot placeholder: Export menu, current layout]` and say so in the
   rationale.
6. Call `propose_edit` with the full new body and a one-sentence rationale
   that names the change event.

## After proposing

The tool returns lint results. Fix `critical` and `important` issues and
propose again. Mention any `suggestion` you chose to leave.

## Do not

- Do not rewrite for style. That is a separate request.
- Do not add content the change event does not support.
- Do not leave TODO, TBD or draft notes in the body.
