---
name: ingest
description: Pull new material from all configured sources into inbox/, then file every inbox item onto entity pages, the timeline and knowledge/. Rebuilds index.md, appends log.md, commits. Runs daily inside the morning routine (full) and at midday on weekdays (--quick: meeting recorders + WhatsApp only), or by hand after important meetings. Use when asked to "ingest", "file the inbox", "update the brain from meetings/mail/slack".
---

# /ingest

Work in `~/brain`; every path below is relative to it.
Three phases. Phase 1 may be skipped with `--inbox-only`.

## Modes and lock

- **Full** (default): every source. Runs daily inside the morning routine (06:30 or on wake): after the quick ingest and the brief on weekdays, alone on weekends.
- **`--quick`**: phase 1 for the fast, high-signal sources only: every **active meeting-notes source** in `config/sources.md`, the WhatsApp allowlist, the WhatsApp self-chat. Update only those `last_run` keys; leave the others for the full run. Phase 2 files everything in `inbox/` as usual. In `index.md` update only the lines of pages you touched. Commit message `ingest (quick): …`. Runs at midday on weekdays, at the start of the weekday morning routine before the brief (no task sync; run record `ingest early`), and from `/prep` / `/ask` when those sources are more than 2 hours stale.

**Lock.** Only one ingest at a time. Take it with `scripts/lock.sh`, never by checking for `.ingest.lock` and then writing it yourself: two runs that wake together both see "no lock". Before phase 1:
1. `id=$(scripts/lock.sh acquire ingest <full|quick>)`. Exit 1 means another ingest holds it (the holder is printed): stop, write nothing, and say so (a caller like `/prep` then carries on with the brain as it is). A lock older than 2 hours is stale and the script takes it over.
2. Keep the printed run id for the whole run.
3. Before committing, `scripts/lock.sh owns ingest $id`. If that fails, another run took over: don't commit, don't release, report what you captured and stop.
4. Finish with `scripts/lock.sh release ingest $id`, including when you stop early on an error. Never `rm` the lock by hand: release only deletes your own.

**Already done.** A scheduled full run first checks `log.md`: if a full `ingest` line dated today exists and `config/state.json` `last_run.email` is less than 3 hours old, append `ingest · skipped, already ran today` to `log.md`, log a `skipped` run record (see below) and stop. Lock held by another run → log `skipped` with `--sources "lock: held by another run"` but don't render or commit.

**Run record.** Per *Run records* in `CLAUDE.md`: `status.py log ingest <full|quick> …` with `--counts captured=,filed=,created=,conflicts=` and every source problem in `--sources` (`partial` if there is any), then `status.py render`, both before the `owns` check and the commit.

## Phase 1 — capture

Read `config/sources.md` and `config/state.json`. For each source, fetch what's new since `last_run` (empty or first run: last 7 days) and write one file per item into `inbox/` following `inbox/README.md`. Respect every allowlist and rule in `config/*.md`. Update `last_run` per source as you finish it.

- **Meeting-notes sources**: every *active* recorder in the table in `config/sources.md`, via its connector: list meetings since last run, fetch each, store summary, decisions, action items, participants. A recorder item whose title or first line starts with **"note for the brain"** is the owner dictating a capture, not a meeting: store it verbatim as `source: manual`.
- **Notes app**: pages edited in the last 24h; fetch each. Only capture if it touches a known entity or knowledge topic.
- **WhatsApp**: for each chat in `config/whatsapp.md`, `list_messages` since last run. Capture only per the rules there.
- **WhatsApp note-to-self**: the self-chat in `config/whatsapp.md`. Every message since `last_run.whatsapp_self` that does not start with 🧠 is a manual capture (`source: manual`, verbatim, the owner's language). Prefix rules (`personal:`, `learn:`, `todo:`, `weekly:`) are in that file.
- **Email**: list accounts, then per account the threads since last run; keep only threads with a known-entity participant (`config/email.md`). Record thread ids in `seen_email_threads`.
- **Slack**: every workspace in `config/slack.md` (channels under *Routing* go to their page unfiltered); search messages since `last_run`, paging until results are older than `last_run`; drop messages from excluded channels and bots, then filter per `config/slack.md`. Read a single channel's history for thread context. If a call fails or times out, retry once; if it still fails, write `slack <workspace>: partial (<call> timed out)` in the `log.md` line and keep that workspace's `last_run` unchanged, so the next run covers the gap.
- **CRM**: notes since last run → inbox items for the matching people.
- **Calendar**: the calendars in `config/calendar.md` only: dedupe mirror copies, skip what any meeting-notes source already covers, write `source: calendar` items for known-entity meetings without notes, tally unknown attendees in `state.json → seen_attendees`.

Known entity = any page in `entities/` or `personal/`, or any CRM contact.

## Phase 2 — file

For each file in `inbox/` (not `_done/`, not `README.md`):

0. Group captures of the same meeting first (several recorders, see *One meeting, one filing* in `config/sources.md`), also against meetings already in `inbox/_done/` and the timeline from the last 3 days. File each group as one meeting from its **primary** capture: the best-ranked recorder in the `config/sources.md` table, per *Primary and corroborating captures* there. The primary's wording, names, numbers and owners go on the page; the other captures only add what it missed and flag a differing number, date or owner (`⚠ conflict`, primary's version first); the primary is cited first in every `(src: …)`. Hand the primary role to the next rank only when the primary capture is partial (under half the meeting) or has no summary, and say so in the History line.
1. Identify entities. Match to existing pages first (name, company, CRM id). Create a new page **only** if the source is a meeting, the CRM, or the owner (per `CLAUDE.md`). Use `entities/_templates/`.
2. Update each entity page: rewrite *Status* (short, current), add/close *Open items* (format and owner rule in `config/tasks.md`: `- [ ] Owner: text · due YYYY-MM-DD (src: …)`, owner always first, `<You>:` only for the owner's own next actions; close by ticking `- [x]`, never by deleting), append a *History* line. Every fact gets `(src: inbox/<file>)`.
3. Add timeline lines to `timeline/YYYY/YYYY-Wnn.md` for events and **every decision or commitment**.
4. Deal stage changes → update frontmatter `stage`, `next_step`, `next_step_due`. `next_step` = the next milestone (an event, not the owner's action; those are tasks), per `config/tasks.md`.
5. Reusable non-entity knowledge → `knowledge/<area>/<topic>.md`.
6. Contradiction with an existing page → keep both, tag `⚠ conflict`.
7. Personal content → `personal/` only, following its README.
8. Write back to the CRM (if connected): for people with a `crm:` id, create a note with a one-paragraph summary of the interaction (meetings and substantive WhatsApp/email only).
9. Move the inbox file to `inbox/_done/`.

Source-specific rules:
- `source: calendar` — one History line on the page and one timeline line `met [[X]] (calendar only, no notes)`. Infer no decisions from a calendar event.
- Self-chat `weekly:` answers (or a reply to the 🧠 weekly message) — rewrite `telos/now.md` as `/weekly` step 3 would (new week header, `Updated:` today), changing only what the answers cover and carrying the rest. Then apply the task answers per `config/tasks.md`: tasks serving the new top 3 → p1 (≤ ~5), last week's p1s that don't → p2, and the do / date / drop answers (never delete). Log `weekly-answers` in `log.md`. This is the one case where ingest edits TELOS.
- Self-chat `personal:` → `personal/` only. `learn:` → follow `/learn`. `todo:` (or "todo" at the start of a voice note) → a `<You>:` line on the page it's about (task Inbox if no page fits); phase 3 creates the task.

## Phase 3 — task sync (full and quick)

Per `config/tasks.md` (projects, ids, task format). Only **the owner's own next actions** become tasks; lines for other owners stay on the page. Skip this phase until a task manager is connected.
1. Open tasks per project and sub-project in the `config/tasks.md` map (all pages). Completed since the last run.
2. **Done in the task manager** → tick the page line with that `todoist:<id>`: `- [x] … (done YYYY-MM-DD in Todoist)`.
3. **Added in the task manager** (no page line has its id) → if the project + text point to one page, add `- [ ] <You>: <title> · due … · todoist:<id> (src: todoist, YYYY-MM-DD)` under its *Open items*; else leave it there (not lost) and mention it in the summary.
4. **New `<You>:` lines** written in phase 2 (or any `<You>:` line with no `todoist:` id) → create the task in the project that covers the page: verb-first title, description `Brain: <page path>` + facts + `src`, a due date only for a real date, priority p3 unless the source says urgent, labels per `config/tasks.md`. Write `· todoist:<id>` on the line.
5. Due date changed in the task manager → update the line's `due`.
6. Snapshot `config/todoist-tasks.json` as `config/tasks.md` describes (every open task, full project names); set `last_run.tasks`. Task manager unreachable → keep the old snapshot, `tasks: unreachable` in `--sources`, and leave new lines without ids (next run creates them).
Counts for the run record: `tasks_ticked=,tasks_created=,tasks_filed=`.

Then rebuild `index.md` (every page, one-line status, updated date), append one line to `log.md` (counts: captured, filed, created, conflicts, tasks ticked/filed), write the run record and render (above), and:

```
git add -A && git commit -q -m "ingest: <n> items, <m> pages updated" && git push -q
```

Finish with a short summary: what came in, pages created/updated, decisions logged, conflicts, meetings filed from more than one recorder and any where the top-ranked recorder was not the primary, **money** (received / still expected), **propose a page** (attendees seen twice, with meeting titles), anything that needs the owner.
