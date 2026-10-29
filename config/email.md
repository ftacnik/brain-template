# Email

Accounts: via your mail connector (list accounts first; query each linked account).
<!-- - <account label> — <what it is for> -->

Rule: capture a thread only if a participant matches a **known entity** — an `entities/` page or a CRM contact. Email never creates new entities.

From a kept thread, capture: the ask, any commitment/date/amount, and the current state (waiting on whom). Not the full text.

## Always skip
- newsletters, notifications, receipts, calendar auto-mails
- threads already captured (match on thread id in `config/state.json` → `seen_email_threads`)

## Always capture
- Auto-generated **meeting notes emails** (meeting-assistant summaries, call-recorder artifacts) for meetings of a known entity, even when you did not attend: file them like meeting notes (`source: email`, ref = thread + notes doc). They are not "calendar auto-mails".
