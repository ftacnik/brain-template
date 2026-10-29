---
name: weekly
description: Sunday review — summarise the week from the timeline and journal, run /lint, then interview the owner to refresh telos/now.md and goals.md. Use for "weekly review", "plan the week", "refresh my priorities".
---

# /weekly

Work in `~/brain`; every path below is relative to it.

## 1. Look back (no input needed)
- Read this week's `timeline/` file, the week's `journal/` entries, `log.md` lines from the week.
- Run `/lint`.
- Read the task manager (per `config/tasks.md`): overdue, the Inbox, p1/p2 without a date, tasks older than 30 days; and `Waiting.md` (who owes you what).
- Write `journal/weekly-YYYY-Wnn.md`: decisions made, deals that moved, new entities, open loops (including the task items above, each with a proposal: do / date / drop / move project, and the chase list from `Waiting.md`), what slipped vs `now.md`'s top 3, lint items needing a decision.

## 2. Interview (in chat, one question at a time, short)
Ask only what's needed to rewrite `telos/now.md`:
1. Of last week's top 3, what's done / carried / dropped?
2. Top 3 for the coming week?
3. Anything new in deals/engagements? Anything to pause?
4. Who do you wait on? Who waits on you?
5. Tasks: overdue and Inbox items, do / date / drop each? Who from *Waiting* to chase? (Apply through the task connector; never delete.)
6. Anything to say no to this week?
7. (Monthly, first Sunday) Anything to change in `goals.md` or `me.md`?

Pre-fill proposed answers from the look-back so the owner mostly confirms or corrects.

## 3. Write
- Rewrite `telos/now.md` (new week header, `Updated:` today). Keep it short.
- Task priorities follow the new top 3 (`config/tasks.md`): tasks that serve the top 3 → p1 (≤ ~5); last week's p1s that don't → p2. Go through the **Stale** filter with the owner (date / p4 / drop).
- Edit `goals.md` / `me.md` only if the owner asked.
- Create next week's `timeline/` file with the header (`timeline/README.md`).
- Keep the `now.md` section headings `## This week's top 3` and `## Waiting on` exactly: `Home.md` embeds them. *Waiting on* lists only what others owe you; what you owe others goes to the task manager (answers to question 4 → tasks), never a list in `now.md`.
- Append `log.md`, write the run records (`status.py log lint check …` for the lint pass, `status.py log weekly review …` for the review; see *Run records* in `CLAUDE.md`), `status.py render`, commit, push.

If run by routine (owner not present): do step 1 and 3's timeline file only. Put the interview questions with pre-filled proposals at the top of `journal/weekly-YYYY-Wnn.md`. If posting is enabled in `config/whatsapp.md`, also post the same questions to the owner's WhatsApp self-chat, prefixed `🧠 Brain · weekly YYYY-Wnn`, plain text, under 1,500 characters, ending with: "Reply here, voice is fine. The next ingest applies your answers to now.md." If sending is not permitted or fails, note it in `log.md`. The owner can also answer in the app by saying "weekly"; `/ingest` applies self-chat answers (see `config/whatsapp.md`).
