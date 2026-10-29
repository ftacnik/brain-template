# WhatsApp allowlist

Only chats listed here are read. Edit freely; `/ingest` re-reads this file every run. Match loosely on the WhatsApp display name; record the chat id (jid) on first run so later runs don't have to search. Format: `- Display name (jid <id>) · [[Page]] — note`.

## Business — people
<!-- one line per contact whose chat the brain may read -->
- 

## Business — groups
<!-- one line per group; name the page the group's messages route to -->
- 

## Friends & family → `personal/` only
- 

## Capture — note to self
- **<your name> (self-chat)** (jid `<your own jid>`) · WhatsApp "message yourself". Zero-friction capture from the phone, by typing or dictating.
  - Every message here is a **manual capture**: file it verbatim as `inbox/YYYY-MM-DD-manual-<slug>.md` with `source: manual`, `ref: whatsapp-self <message id>`, your language kept. Then treat it exactly like `/capture`: decisions go to the timeline at once, entity guesses in frontmatter.
  - Prefixes: `personal:` → `personal/` only · `learn:` → treat as `/learn` input · `todo:` → a task for you (page line + task manager, per `config/tasks.md`) · `weekly:` or a reply to the brain's weekly message → the weekly interview answers; `/ingest` applies them to `telos/now.md` per `/weekly` step 3, changing only what the answer covers, and logs it.
  - Messages that start with **🧠** are the brain's own posts (morning plan, weekly questions, confirmations). Never capture those.
  - This is the only chat the brain **writes to**, and only if you enable it here: `/morning` posts the Suggested plan, `/weekly` posts the interview questions, each prefixed `🧠 Brain ·`. Never post anything here that is not already in the brain, and never post to any other chat.
  - **Posting enabled:** no   <!-- set to "yes" once you have tested the brain by hand for a week -->

## Explicitly NOT read
<!-- groups the brain must skip even if a rule above would match them: deal-flow groups, event groups, status broadcasts -->
- 

## Rules
- **Backfill.** A chat marked `backfill from YYYY-MM-DD` is new: on its first run, read it from that date instead of `last_run.whatsapp`, then delete the marker from this file in the same commit.
- Capture: decisions, commitments, dates, money, anything about a known entity.
- Skip: small talk, media-only messages, forwards.
- Never quote personal/family messages in work entity pages.
