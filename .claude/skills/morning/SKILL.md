---
name: morning
description: Today's brief — calendar, meeting prep, open commitments, expected money, overnight mail and Slack, against this week's priorities. Writes journal/YYYY-MM-DD.md and, if enabled, posts the plan to the owner's WhatsApp self-chat. Runs 06:30 by routine, after a quick ingest and before the full one; run by hand with "morning", "brief me", "what's today"; "/morning refresh" or "refresh the brief" rewrites today's brief with what already happened.
---

# /morning

Work in `~/brain`; every path below is relative to it.

Read `telos/now.md`, `telos/principles.md`, `index.md`, `personal/personal goals.md` if present, yesterday's `journal/` entry, and `config/calendar.md` (the mirror rule).

Gather (parallel where possible):
- **Calendar**: today's events (all calendars). An event present in two calendars at the same time is one meeting, listed once. Scheduling tools' own blocks (focus time, lunch, travel, habits) are not meetings.
- **Meetings**: for each meeting, the matching entity pages and the last 2 timeline mentions → 2–3 lines of prep each. If no page exists, say so.
- **Open items**: per `config/tasks.md` — lead with today's p1 tasks (this week's top 3), then the task manager's `today | overdue` live, grouped by project, overdue first with days overdue (unreachable → `config/todoist-tasks.json`, and `tasks: unreachable` in `--sources`); then `Waiting.md` items due ≤ today (who to chase); `next_step_due` ≤ today across deals; *Waiting on* from `now.md`.
- **Money**: every `expected_payments` entry on a deal page with `received` empty and today inside [`promised` − 3 days, `deadline` + 3 days] (no deadline: `promised` + 14 days). If a bank connector is configured, check it once per account per run and report each as **received on <date>** or **not yet**; without one, list them as "expected, cannot verify". If received: fill `received:` on the page, add a History line and a timeline line.
- **Overnight**: unread email across accounts and Slack since yesterday evening (excluded channels per `config/slack.md` dropped) — but only the threads involving known entities or needing a reply from you. Max 8 lines.
- **Inbox**: anything in `inbox/` not yet filed → mention count.

**Before gathering: one brief at a time, brief first.** The brief and the full ingest are one routine (06:30 or on wake): on weekdays a quick `/ingest --quick` (meeting recorders, WhatsApp, self-chat) runs first so meeting prep reflects last night, then this brief, then the full `/ingest`, so the plan never waits for the slow filing. The brief reads calendar, email, Slack and the task manager live itself. Run by hand, the brief runs no ingest. Locks go through `scripts/lock.sh` (atomic; never check-then-write by hand):
1. `mid=$(scripts/lock.sh acquire morning brief)`. Exit 1 → another brief is running: stop without writing or sending anything.
2. A scheduled run (not one the owner asked for) that finds today's `journal/` file already written: release the morning lock and stop, so the plan is never posted twice.
3. `scripts/lock.sh release morning $mid` at the very end (after delivery), and also when you stop early.

Write `journal/YYYY-MM-DD.md`:

```
# YYYY-MM-DD · <weekday>

## Focus today (from now.md)
## Meetings & prep
## Due / waiting on      (money lines first: received / not yet)
## Overnight worth a look
## Suggested plan (3–5 lines)
```

If the owner is driving or travelling today (calendar), add one line: the `@call` tasks they could do on the way. Keep it under ~60 lines. Respect the rhythm in `telos/principles.md`. If `now.md`'s `Updated:` date is more than 10 days old, say so at the top. Append to `log.md`, commit, push.

**Run record** (after delivery, so it knows whether the post went out): per *Run records* in `CLAUDE.md`, `status.py log morning brief …` with `--counts meetings=N` and problems such as `email: unreachable` or `whatsapp: send failed` in `--sources`, then `status.py render`, then `git add -A && git commit -q -m "morning: run record" && git push -q`, then release the lock. A scheduled run that stops because today's brief exists logs nothing.

**Deliver.** If posting is enabled in `config/whatsapp.md`, post the *Suggested plan* plus anything urgent to the owner's WhatsApp self-chat, prefixed `🧠 Brain · morning YYYY-MM-DD`, plain text, under 1,500 characters. This and the weekly questions are the only messages the brain ever sends, and only to that chat. If sending is not permitted or fails, note it in `log.md` and carry on; the journal file is the record. Reply in chat with the same plan and anything urgent only.

## Refresh during the day (`/morning refresh`, "refresh the brief")

Rewrites today's brief from where the day stands now: what already happened, what's left. Run by hand; never scheduled.

1. **Lock and check.** `mid=$(scripts/lock.sh acquire morning refresh)`; exit 1 → a brief is running, stop. No `journal/YYYY-MM-DD.md` for today yet → write the normal brief instead (sections above), then stop.
2. **Catch up first.** Unless a quick or full ingest finished in the last 30 minutes (`runs.jsonl`), run `/ingest --quick` with its normal lock, so meetings that already happened have their recorder notes filed and today's task completions are ticked. Its lock held → skip it and say the brief may miss the last hour.
3. **Gather what changed since the brief.** Calendar for today (live, mirrors once): which meetings are over, which are left, anything added, moved or cancelled. For each meeting that is over: the outcome in one line from the filed notes (the timeline line or the page's History), else "held, no notes yet". Task manager: completed since 00:00 today, and `today | overdue` for what's left. Money: re-check only an expected payment due today that the brief listed as *not yet*, at most once per account. Email and Slack since the brief was written: only threads needing your reply, max 5 lines.
4. **Rewrite `journal/YYYY-MM-DD.md`** in place:
   - first line after the title: `*Refreshed HH:MM (brief written HH:MM).*`
   - a new `## Done so far` at the top: meetings held (time, title, one-line outcome), tasks completed, money received, items others delivered; most important first, max ~10 lines;
   - `## Meetings & prep`: only the meetings still ahead, prep kept, clashes re-checked;
   - `## Due / waiting on` and `## Overnight worth a look` updated (drop what's done; mark new items "since the brief");
   - `## Suggested plan`: 3–5 lines for the rest of the day, from the current time; keep the morning's plan below it as `### Morning plan (HH:MM)` with finished lines struck through (`~~…~~`).
5. **No WhatsApp post** unless the owner says "refresh and send"; then post the new plan prefixed `🧠 Brain · refresh HH:MM`.
6. `log.md` line `morning · refreshed HH:MM: <n> done, <m> meetings left`; run record `status.py log morning refresh ok|partial --trigger manual --started HH:MM --counts done=N,meetings_left=M`; `status.py render`; `git add -A && git commit -q -m "morning: refresh YYYY-MM-DD HH:MM" && git push -q`; release the morning lock. Reply with the new plan and the Done-so-far headline only.
