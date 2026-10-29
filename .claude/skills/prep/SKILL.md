---
name: prep
description: Everything known before a meeting or conversation with a person or company — status, history, open items, last messages, what to ask. Use for "prep me for X", "what should I know before meeting Y", "brief me on Z". For negotiations (price, terms, equity, a dispute, anything with money or a counterpart's "no"), adds a negotiation block built on the circle chart (problem, diagnosis, strategy, tactics).
---

# /prep <person | company | meeting title> [--negotiation]

Work in `~/brain`; every path below is relative to it.

0. Freshness: if, in `config/state.json`, the `last_run` of any active meeting-notes source (table in `config/sources.md`) or of `whatsapp` is more than 2 hours old, run `/ingest --quick` first so today's meetings and messages are on the pages. If it reports another ingest running, carry on and say the brief may miss the last few hours.
1. Resolve the target: entity page(s) via `index.md`; CRM contact (if connected); if a meeting title, the calendar event and its attendees.
2. Gather: Status + Open items + last 5 History lines from each page; your open tasks for them (the page's `<You>: … · todoist:` lines, plus a task-manager search for ones added on the phone) and what they owe you (`Owner: …` lines); put both in the brief as "Your open items" and "They owe you"; timeline mentions in the last 90 days; last recorded meeting with them in any active recorder (`config/sources.md`); recent email thread and WhatsApp/Slack messages with them (last 30 days, respecting `config/` rules).
3. Decide the mode. **Negotiation mode** when `--negotiation` is given, or when the meeting is about price, terms, equity, a payment, a dispute, or the deal page is in stage `negotiating`. Otherwise standard mode.
4. Write the brief. You lead meetings and want an agenda you can read and move through fast, so keep it tight: standard ≤ 40 lines, negotiation ≤ 70.

## Standard brief

```
# Prep · <name> · <date>
**Who/what:** 1–2 lines
**Where we are:** status, last decision, money/dates if any
**They owe us / we owe them:**
**Since last time:** new messages, changes
**Suggested agenda / questions:** 3–5 bullets
**Watch out:** conflicts, stale info, sensitivities
**About them (if a person):** what they need (to be liked / status / to achieve / control), recent successes, how they see the world — from `knowledge/people-insights/` if you keep notes there
```

Add your own special cases here as they come up: a recurring counterpart with a playbook page, a coach whose sessions live in `personal/`. Name the page the brief must read for each.

## Negotiation brief

Standard brief first, then this block. It follows the circle chart (problem → diagnosis → strategy → tactics) from the Harvard PON method; keep your notes on it in `knowledge/frameworks/negotiation.md` (write it with `/learn`) and read that page before writing. Cite the deal page for every number. Mark numbers **known / believed / guess**.

```
## Negotiation
**1. Problem** — the gap between where the deal is and where you want it, in one line.
**2. Diagnosis**
- Parties: people, not companies; each person's individual incentive.
- Their interests (behind their positions) · Our interests.
- Their BATNA (analysed as carefully as ours) · Our BATNA, and is it visible to them?
- ZOPA: what a good deal looks like; is it sustainable; is any of it about identity?
- Core concerns in play (appreciation / autonomy / affiliation / status / role) — theirs and yours.
- Which base they operate from: rights / power / interests.
**3. Strategy**
- Target (internal goal) · Anchor and its justification · Walk-away.
- Value to create: differences to trade (timing, risk, earn-out, scope, people).
- Process move: what to agree about *how* before *what*; coalition or third party if multiparty.
- Away from the table: anything to set up before the meeting (allies, sequence, information).
**4. Tactics for this meeting**
- Opening line and frame.
- Three questions to ask (why? what else? what is that based on?).
- Anchors to expect from them and how to defuse each.
- Concession path and the signal for "end of the road".
- Your trap to watch (name it in `telos/principles.md`): the pre-decided line you do not cross today.
- Close: the last thing you say, so the last emotion is a good one.
**After:** 3 questions to answer in /capture (what worked, what I'd do differently, what I learned about them).
```

5. Save to `journal/prep-YYYY-MM-DD-<slug>.md`. If you found facts not yet on the entity page, add them (with sources), run `python3 -I scripts/status.py render` (Home lists recent preps) and commit. When the owner captures the post-meeting review afterwards, `/ingest` files it to the deal page's History and, if it is reusable, to the negotiation page under "My take".
