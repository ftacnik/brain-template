---
name: capture
description: Drop a quick note, decision or fact into inbox/ for later filing. Use when the owner says "note that…", "remember…", "capture…", "log this", or shares a fact in passing that belongs in the brain.
---

# /capture <text>

Work in `~/brain`; every path below is relative to it.
The WhatsApp self-chat does the same job from the phone (`config/whatsapp.md`); the next ingest files it.

1. Write `inbox/YYYY-MM-DD-manual-<slug>.md` with frontmatter `source: manual`, `captured: <now ISO>`, `entities: [best guesses]`, and the text verbatim (the owner's words, their language).
2. If it is clearly a **decision or commitment** about an existing entity, also append the timeline line now — don't wait for `/ingest`.
3. If it is a **task for you** ("todo", "remind me", "by Friday"), file it now per `config/tasks.md`: a task in the right project (Inbox if unclear) + the `<You>: … · todoist:<id>` line on the page, instead of leaving it for `/ingest`.
4. If it updates `telos/now.md` (a new priority, something no longer relevant), ask before editing TELOS.
5. `python3 -I scripts/status.py render`, then commit: `capture: <slug>`. Reply with one line confirming where it went.
