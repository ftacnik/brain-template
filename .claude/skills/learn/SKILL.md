---
name: learn
description: Add long-term knowledge to the wiki on purpose — from a URL, PDF, file, pasted text, a book or course, or something the owner explains. Use when the owner says "learn this", "add to the wiki", "save this article", "remember this framework", or shares a link/document to keep. Not for meeting notes (that's /ingest).
---

# /learn <url | file | text | topic>

Work in `~/brain`; every path below is relative to it.

1. **Get the source.** URL → WebFetch; PDF/file → Read; pasted text → as is; "topic X" with nothing attached → interview the owner briefly, or research with WebSearch if asked. Save a copy of raw material to `inbox/_done/YYYY-MM-DD-learn-<slug>.md` (or the file itself) so every claim can cite it.
2. **Decide where it lives.** One page per topic under `knowledge/<area>/`: `markets/`, `frameworks/` (how to think: negotiation, M&A process, culture), `playbooks/` (how we do things: DD checklist, fundraising process), `industries/`, `people-insights/` (what we learned about how a type of counterpart behaves), `reading/` (books, courses). If a page on the topic exists, **update it** rather than creating a sibling.
3. **Write for your future self**, using `knowledge/_template.md`: what it is in 3 lines, the key points, how it applies to your situation (link entities and deals), open questions, sources. Don't paste the source; distil it. Keep the owner's own reactions and disagreements as quotes.
4. **Link both ways.** Add `[[links]]` from relevant entity/deal pages ("see [[…]]") and add the page to `index.md` under Knowledge with a one-line summary.
5. `python3 -I scripts/status.py render`, then commit: `learn: <slug>`. Reply with the page path and one line on what it adds.

Rules: cite every non-obvious claim; mark figures known / believed / guess; never store credentials or paywalled full text, only notes.
