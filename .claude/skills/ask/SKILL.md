---
name: ask
description: Answer a question from the brain with citations. Use for "what do we know about X", "what did we agree with Y", "status of Z", "who do I know at W". Saves useful answers back into the brain.
---

# /ask <question>

Work in `~/brain`; every path below is relative to it.

0. Freshness, only for questions about current state ("status of", "latest", "what did we agree", "where are we with", anything about today or this week): if, in `config/state.json`, the `last_run` of any active meeting-notes source (table in `config/sources.md`) or of `whatsapp` is more than 2 hours old, run `/ingest --quick` first. Skip it for background questions ("who do I know at", frameworks, history). If it reports another ingest running, answer anyway and say so.
1. Read `index.md`. Pick the pages that could answer the question. Open only those (plus the relevant `timeline/` weeks for "when / what did we agree" questions).
2. If the question is personal, also read `personal/`. Otherwise don't. Questions about your tasks ("what's on my plate for X", "what's overdue", "what did I commit to") → the task manager via its connector (per `config/tasks.md`) plus the pages' *Open items*; what others owe you → `Waiting.md`.
3. If the brain can't answer, say so, and check the CRM (if connected) and recent meetings in the active meeting recorders (`config/sources.md`) before giving up. Don't guess.
4. Answer concisely. Status first, then detail. Every claim cites its source: `(src: entities/companies/x.md → inbox/…)` or the original URL.
5. Flag anything stale (page `updated` > 30 days for an active deal) or marked `⚠ conflict`.
6. If the answer is reusable (a synthesis, a comparison, a how-to), save it under the right `knowledge/<area>/` folder using `knowledge/_template.md`, with sources, and link it from the entity pages. If it corrected a page, fix the page.
