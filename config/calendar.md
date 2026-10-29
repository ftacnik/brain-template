# Calendar

Only the calendars listed here are read by `/ingest`:

| Calendar | id | Why |
|---|---|---|
| <Personal> | `<calendar id>` | <most meetings land here> |
| <Work> | `<calendar id>` | <work meetings> |

Not read by `/ingest`: <shared, family, holiday and location calendars>. `/morning` may still read everything for the day's plan.

## Mirror copies
If a tool copies meetings between your calendars, the same meeting appears in both at the same time. **Two events with the same start and end across two calendars are one event.** Keep the copy that has attendees or a description (the original); if both or neither, keep the work copy. Never log a meeting twice. Scheduling tools' own blocks (titles like "Focus time", "Lunch", "Travel", habits, "Busy") are not meetings: skip them.

## What /ingest does with the events since last run
Tool: `list_events` per calendar id, `startTime` = `config/state.json → last_run.calendar`, `endTime` = now, ordered by start time.

1. Dedupe per the mirror rule. Skip all-day events, declined events, scheduling blocks, and events with no attendee other than you unless the title names a known entity.
2. **Already covered**: if a meeting note captured in the same run matches the event (overlap within 15 minutes, or same title / attendees), the calendar adds nothing. Skip.
3. **Known entity, no notes**: an attendee or the title matches a page in `entities/` or `personal/`, or a CRM contact → one inbox item `source: calendar` with title, time, attendees. `/ingest` files it as one History line on the page and one timeline line: `met [[X]] (calendar only, no notes)`. No decisions are inferred from a calendar event.
4. **Unknown attendees**: for every attendee email that matches no page and no CRM contact, bump `seen_attendees[email] = {name, count, last, titles}` in `config/state.json`. When `count` reaches 2, list the person in the ingest summary under "Propose a page" with the meeting titles. Do not create the page; you say "make a page for X" (or add them in the CRM) and the next ingest creates it.
5. Personal-calendar events with no work entity (doctor, family, friends) are not captured, except as `personal/` timeline lines when they are a commitment you made (travel, family dates).

Update `last_run.calendar` when done.
