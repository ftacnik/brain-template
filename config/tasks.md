# Tasks

The template assumes **Todoist** as the task manager (it has a Claude connector and labels, projects, comments and deadlines). Any tool with the same shape works: replace the names below and the `todoist:` marker.

## Architecture

| Tool | Holds | Who writes |
|---|---|---|
| **Todoist** | Your own next actions, and only those. The one place you look at your tasks. | The brain (`/ingest`, `/capture`, on request) and you (phone, quick add) |
| **Calendar scheduler** (optional, e.g. Reclaim) | Calendar time for tasks labelled `reclaim`. Nothing else is scheduled. | The scheduler's Todoist sync |
| **Brain pages** | *Open items*: the context, and what others owe you (`Name: …`). Your lines carry `todoist:<id>`. | The brain |
| **`Waiting.md`** | Generated chase list: open items owned by others, plus any `<You>:` line not yet in Todoist (safety net). | `scripts/status.py render` |
| **CRM** | People follow-ups and keep-in-touch only. Not tasks. | You + the brain |

Three rules keep it clean:
1. **Only your own next actions become Todoist tasks.** What others owe you stays on the page as `Owner: …` and shows in `Waiting.md`, `/morning` and `/weekly`.
2. **Calendar time is opt-in.** Label `reclaim` only on tasks that need a block: dated, or p1/p2. Undated backlog stays unlabelled.
3. **Capture doesn't change.** "todo: …" in the WhatsApp self-chat, or an action in a meeting → the brain files it in the right project. Unclear where → Todoist Inbox; `/weekly` empties it with you.

## Todoist structure

One project per area of your life (your roles in `telos/me.md`, plus Personal and Inbox); sub-projects only where an area has several tasks. A new sub-project only when ~5+ tasks share a page; otherwise file at the area root. The page → project map below is what `/ingest` uses. Fill in the ids from the Todoist connector (`find-projects`).

| Project | id | Brain pages filed here |
|---|---|---|
| **<Area 1>** (root) | `<project id>` | <company, deal and person pages that belong to it> |
| ↳ <Sub-project> | `<project id>` | <pages> |
| **<Area 2>** | `<project id>` | <pages> |
| **Personal** | `<project id>` | `personal/` (generic titles, no private detail) |
| Inbox | `<project id>` | unclear; emptied in `/weekly` |

A page not in the map → its area's root (deal/company by topic); add it to the map in the same commit.

**Deal `next_step`:** one short line naming the deal's next *milestone* (an event, not an action: `indicative offer ~23–30 Oct`), with `next_step_due` its date. Your actions never go there; they are Todoist tasks. `/ingest` refreshes it when the deal moves.

## Task format in Todoist

- **Title**: verb first, short (`Send X the redline`). No owner prefix, no project prefix.
- **Description**: `Brain: <page path>` on the first line, then the facts that don't fit the title, then `src: …`.
- **Due**: only a real date. **Deadline** field for hard external deadlines (tax, capital call).
- **Priority**: p1 = this week and it matters; p2 = soon; p3 = default for brain-created tasks; p4 = someday.
- **Duration**: estimate when known (the scheduler uses it), else 30m for labelled tasks.
- **Labels**, the brain sets them when it creates a task:
  - `reclaim` (work time) / `reclaim_personal`: the scheduler books time; only dated or p1/p2.
  - `call`: doable by phone or while driving (ask, chase, reply, discuss).
  - `deep`: needs focus (review, draft, write, decide on a structure).
  - `<City>`: only doable in that city (meet in person, sign, pick something up). Add a location reminder for the city, trigger on arrival.
- **Recurring admin** lives as recurring tasks in the finance/admin project: VAT, payroll, monthly bookkeeping. When a new statutory or repeating payment appears, add it as a recurring task.
- **Sections** (optional, by kind of work, not by company): add them when a project passes ~6 top-level tasks; the brain then files new tasks into the matching section.
- **Parent tasks** group related work (one call, one payment run, one outreach): the subtasks keep their own page lines; a parent created only to group them needs no page line. Merged tasks are completed in Todoist and ticked on the page `(merged YYYY-MM-DD into todoist:<id>)`.
- **p1 = this week's top 3 only** (set in `/weekly` from `now.md`, at most ~5 tasks); everything urgent but outside the top 3 is p2.

## Page line format

```
- [ ] Owner: what · due YYYY-MM-DD · todoist:<task id> (src: …)
```

Owner first, always (`<You>:` or a name; a topic is not an owner; `<You>` is the `OWNER` constant in `scripts/status.py`). One task per line. Done: `- [x] … (done YYYY-MM-DD, src: …)`; dropped: `(dropped YYYY-MM-DD, src: <you>)`. Never delete a line.

## Sync (`/ingest` phase 3)

1. `find-tasks` for every project (all pages) and `find-completed-tasks` since the last run.
2. Completed in Todoist → tick the page line with that `todoist:` id.
3. Task added in Todoist with no page line (you, on the phone) → if its project and text point to one page, add the line `<You>: … · todoist:<id> (src: todoist, YYYY-MM-DD)`; else leave it (Todoist holds it; it's not lost).
4. New `<You>:` line from this run's filing (or one without `todoist:`) → create the task (format above), write the id on the line.
5. Due date moved in Todoist → update the line's `due`.
6. Write `config/todoist-tasks.json` (`{"synced": <now ISO>, "tasks": [{id, project, content, due, priority, labels, parent, page}]}`, every open task, `project` as the full name from the table above, `page` = the `Brain: <path>` from the description) for `/morning` fallback and `Waiting.md`; set `last_run.tasks`.

## Views (saved filters)

Focus `(today | overdue) & (p1 | p2)` · Calls `@call` · Deep work `@deep` · Stale `no date & created before: -30 days`.

## Reading

- **You**: the Todoist app (Today, Upcoming, per project); the calendar for scheduled blocks; the morning brief.
- `/morning`: Todoist `today | overdue` (live) grouped by project, plus `Waiting.md` items due ≤ today.
- `/weekly`: overdue, Inbox, p1/p2 without a date, the chase list from `Waiting.md`, tasks older than 30 days → do / date / drop.
- `/prep`, `/ask`: the page's *Open items*.

## Never

Complete, move or drop a task on a guess. A tick needs evidence (a source) or your word. Never delete in Todoist: complete instead.
