# Brain — operating manual

This repo is <your name>'s second brain. Two layers:

1. **TELOS** (`telos/`) — who you are, goals, this week's priorities. Small. Loaded into every Claude Code session by a global hook. Edited only in the weekly review or when you ask.
2. **Knowledge** (`entities/`, `timeline/`, `knowledge/`, `personal/`) — what you know. Grows. Written mostly by Claude from captured sources, read on demand.

Capture flows in through `inbox/`; `/ingest` files it; `/ask` answers from it; `/lint` keeps it honest.

Replace `<your name>` and `<you>` throughout this file (and `OWNER` in `scripts/status.py`) with your first name before the first run.

## Folder map

| Folder | Holds | Who writes |
|---|---|---|
| `telos/` | `me.md`, `goals.md`, `now.md`, `principles.md` | You, via interviews |
| `entities/people/` | One page per person (work). Links to your CRM contact when one exists. | Claude |
| `entities/companies/` | One page per company: clients, partners, counterparties | Claude |
| `entities/deals/` | Engagements, prospects, pipeline items | Claude |
| `entities/projects/` | Internal projects and ventures | Claude |
| `personal/` | Family, friends, health, finances. Stricter rules, see below. | Claude |
| `timeline/YYYY/YYYY-Wnn.md` | Dated events and decisions, one file per ISO week | Claude |
| `knowledge/` | The wiki: `markets/ frameworks/ playbooks/ industries/ people-insights/ reading/`. Grows from `/ingest` by-products and from `/learn` on purpose. One page per topic, updated not duplicated. | Claude |
| `journal/` | `YYYY-MM-DD.md` morning briefs, `prep-*.md`, `weekly-*.md`, `lint-*.md` | Claude |
| `inbox/` | Raw captures waiting to be filed. Append-only. | Hooks, routines, `/capture` |
| `config/` | Allowlists and capture rules per source, `state.json` | You + Claude |
| `index.md` | Every entity page with a one-line status | Claude, on every ingest |
| `log.md` | What was ingested/changed and when | Claude, on every ingest |
| `Home.md` | Start page in Obsidian: status, today's brief, this week. Generated below its marker; your notes above it | `scripts/status.py` |
| `Status.md` | Today's runs, source freshness, inbox/conflicts/locks, last 14 runs. Fully generated | `scripts/status.py` |
| `Waiting.md` | What others owe you, plus your page tasks not yet in your task manager. Fully generated | `scripts/status.py` |
| `runs.jsonl` | One machine-readable line per routine run (ingest, morning, weekly, lint) | `scripts/status.py log` |

## Rules

**Reading.** Start from `index.md`, then open only the pages you need. Never read the whole repo.

**Writing entity pages.** Use the template in `entities/_templates/`. Keep the *Status* block at the top current and short. Append history, never rewrite it. Every fact gets a source: `(src: inbox/2026-10-08-whatsapp-xyz.md)` or a URL, or `(src: <your name>, 2026-10-08)`.

**Timeline.** One line per event: `- 2026-10-08 · [[company]] · what happened / what was decided · next: … (src: …)`. Decisions are the most important thing in this repo. If in doubt, log it.

**Linking.** `[[wikilinks]]` by page name. People pages carry `crm: <id>` in frontmatter when a CRM contact exists.

**Inbox.** Never edit or delete inbox files. `/ingest` moves processed files to `inbox/_done/`.

**Conflicts.** When a new fact contradicts a page, don't overwrite. Add both with sources and a `⚠ conflict` tag; `/lint` surfaces these.

**Entities vs noise.** Create a new entity page only from a meeting, a CRM contact, or when you ask. Email and Slack update *existing* entities; they don't create new ones.

**Personal.** `personal/` never contains account numbers, IBANs, balances, medical identifiers or anything you'd not want in a private GitHub repo. Summaries and decisions only. Raw financial data stays in its source systems, never copied here. `/ask` reads `personal/` only when the question is personal; nothing else does.

**Language.** English for structure and Claude-written text. Quote the owner in whatever language they used.

**Other memories.** Durable facts go here, not into any other AI memory store. Claude Code's own memory holds only working-style feedback.

**Run records.** Every ingest, morning, weekly and lint run ends with one line in `runs.jsonl`, then a render, both just before the commit so they land in it:
```
python3 -I scripts/status.py log <skill> <mode> <ok|partial|failed|skipped> --trigger <scheduled|manual> --started HH:MM --counts k=N,… --sources "<source>: <problem>; …"
python3 -I scripts/status.py render
```
`partial` = the run finished but a source was unavailable, timed out or stale, or it ran 3h+ late; name each problem in `--sources` (the same ones the `log.md` line names). `failed` = stopped on an error: still log, render and commit. `skipped` = already ran / lock held. `--trigger scheduled` only when a routine started the run. Every other skill that commits (`/capture`, `/learn`, `/prep`, edits) runs just `render` before committing, so `Home.md` stays dated today. Never edit `Status.md`, or `Home.md` below its marker, by hand. An optional launchd job (`scripts/com.example.brain-status.plist`) also renders hourly so the date rolls over when no run happens; it skips while a lock is held and never commits. `/weekly` keeps the `now.md` headings "This week's top 3" and "Waiting on": `Home.md` embeds them.

**Tasks.** Your own next actions live in your **task manager** (the template assumes Todoist; map in `config/tasks.md`). Pages keep *Open items* as context and what others owe you, with `todoist:<id>` on your lines. `/ingest` syncs both ways; `status.py render` builds `Waiting.md` (chase list + safety net). The CRM is for people, not tasks. Full rules in `config/tasks.md`.

**Git.** Commit after every ingest, brief, or edit with a one-line message. Push if a remote exists. Never force-push.

**Messages.** The brain never sends messages or emails. The one permitted exception, if you enable it in `config/whatsapp.md`: `/morning` and `/weekly` may post to your own WhatsApp self-chat. Nothing is ever posted anywhere else.

## Skills

Every skill is also installed globally as a thin wrapper (`scripts/install-skills.sh` → `~/.claude/skills/`), so `/ask`, `/capture`, `/prep` and `/learn` work from any Claude Code session and always operate on `~/brain`. Re-run the script after changing a skill's description.

| Skill | When |
|---|---|
| `/ingest` | File everything in `inbox/`. Full run daily inside the morning routine; `--quick` (meeting recorders + WhatsApp) at midday on weekdays and from `/prep`/`/ask` when stale. One run at a time (`.ingest.lock`, taken atomically via `scripts/lock.sh`; `/morning` likewise holds `.morning.lock`). Run by hand after a big meeting. |
| `/ask <question>` | Answer from the brain with citations. Save useful answers to `knowledge/` or the entity. |
| `/lint` | Stale pages, orphans, conflicts, missing sources. Weekly. |
| `/morning` | Today's brief → `journal/`. Runs at 06:30. |
| `/prep <meeting or person> [--negotiation]` | Everything known before a meeting. Negotiation mode adds a circle-chart block (problem, diagnosis, strategy, tactics). |
| `/capture <text>` | Drop a note into `inbox/` quickly. |
| `/learn <url, file, text, topic>` | Add long-term knowledge to `knowledge/` deliberately: distil, place, link, cite. |
| `/weekly` | Week summary + interview to refresh `telos/now.md` and `goals.md`. Sundays. |

## Sources (see `config/`)

One file per source in `config/`, each with its allowlist and rules; `config/sources.md` is the overview and the ranking of meeting recorders. Typical set: meeting recorders (one or more; the same meeting from two recorders is filed once) · WhatsApp allowlist (`config/whatsapp.md`) · WhatsApp note-to-self chat (zero-friction capture from the phone; the only chat the brain may post to) · email threads with known entities (`config/email.md`) · Slack channels filtered to known entities and decisions (`config/slack.md`) · CRM (people link, interaction notes both ways) · calendar (`config/calendar.md`) · task manager (`config/tasks.md`).

Add rules as dated decisions, with the why: `(decided YYYY-MM-DD)`. When a run does something wrong, the fix is a sentence here or in the skill, not a new tool.
