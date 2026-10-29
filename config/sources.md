# Capture sources

Each source has its own file in this folder with the allowlist/rules. `/ingest` reads them before every run. Add rules as dated decisions.

| Source | How | Scope | Creates entities? | `state.json` key |
|---|---|---|---|---|
| Meeting recorder(s) | the recorder's connector, items since last run (see the table below) | all meetings | yes | `meetings` |
| Notes app | pages edited in the last 24h | whole workspace | no — updates existing | `notes` |
| WhatsApp | `list_messages` for chats in `whatsapp.md` | allowlist only | no | `whatsapp` |
| WhatsApp note-to-self | `list_messages` on your self-chat (`whatsapp.md`) | every message not starting with 🧠 | no — manual captures, like `/capture` | `whatsapp_self` |
| Email | mail connector, threads since last run | threads involving a known entity (page or CRM contact) | no | `email` |
| Slack | workspace connector, member channels | messages mentioning known entities or containing decisions/commitments | no | `slack` |
| CRM | contact connector | people pages link via `crm:` id; interaction notes written back | yes (people) | `crm` |
| Calendar | `list_events` on the calendars in `calendar.md` | known-entity meetings without notes; unknown attendees tallied | no — proposes a page after 2 sightings | `calendar` |
| Task manager | see `tasks.md` | your own next actions, both ways | no | `tasks` |

Delete the rows you don't use. Start with whatever records your meetings; add one source a week.

## Meeting notes (one group, several recorders)

You may record the same meeting with more than one tool. Every recorder is a **meeting-notes source**: read by the full *and* the `--quick` ingest, checked by the `/prep` / `/ask` freshness rule, and able to create entities. They are **not equal**: the *Rank* column says whose version wins when several cover the same meeting.

| Rank | Recorder | Status | Best at | How | `state.json` key |
|---|---|---|---|---|---|
| 1 | <recorder A> | active | <calls / in person> | <connector tools> | `meetings` |
| 2 | <recorder B> | active | <…> | <…> | `meetings_b` |

When a recorder is connected, retired or re-ranked, change its row here; the skills read this table and need no edit.

**One meeting, one filing.** Two captures are the same meeting when their times overlap (±30 min) and they share a calendar event, or a title or participants. Keep every inbox file (raw sources are never edited), but file the meeting **once**: one History line per page, one timeline line, one CRM note. A capture of a meeting already filed in an earlier run only adds what is new, never a second History line. A calendar item is skipped when any recorder covers the meeting.

**Primary and corroborating captures.** In a group of captures of one meeting, the one from the best-ranked active recorder is the **primary**; the others **corroborate**.

- *Any* capture may be used to identify the meeting: title, participants, calendar event, attendee list.
- The **primary** supplies the content: the summary and the History line wording, the decisions and commitments as it states them, names, owners, numbers and dates, and the CRM note.
- A **corroborating** capture adds what the primary missed (a decision, an action item, a number), cited to that capture alone. It never rewrites what the primary said.
- **Disagreement.** On a number, amount, date or who owns a commitment: the page says the primary's version, the variant follows inline, e.g. `$300k (recorder B heard $350k)`, tagged `⚠ conflict` so `/lint` surfaces it. On wording, name spelling, emphasis or what the meeting was "about": the primary wins silently; record nothing.
- **Override.** The primary drops to corroborating and the next rank takes over when its capture covers less than half the meeting (against the calendar event or the longest capture) or has no summary. Say so in the History line: `(primary: B; A partial)`.
- **Citation order.** The primary capture is listed first in every source list: `(src: inbox/…-a-….md, inbox/…-b-….md)`. That is how a page shows which recorder it trusted.
- **Reading.** `/prep`, `/ask` and `/morning`, when they read captures or the recorder connectors directly, apply the same rank.

## Capture file naming

`inbox/YYYY-MM-DD-<source>-<slug>.md` with frontmatter `source`, `captured`, `ref` (URL or id), `entities: []` (best guess, refined by `/ingest`).

## State

`config/state.json` holds the last-run timestamp per source (ISO 8601 with offset). Routines update it. An empty value means the source has never run: the first run reads the last 7 days.
