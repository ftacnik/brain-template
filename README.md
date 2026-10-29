# Second brain — template

A personal knowledge base that Claude Code keeps for you: plain markdown in a git repo, filled from your meeting notes, messages, mail and calendar by scheduled routines, and queried from any Claude Code session. This repo is the scaffold only: the rulebook, the templates, eight skills, four scripts, and one config file per source. No data.

Two layers:

1. **TELOS** (`telos/`): who you are, your goals, this week's priorities. Small. Printed into every Claude Code session by a hook. You write it; a weekly review refreshes it.
2. **Knowledge** (`entities/`, `timeline/`, `knowledge/`, `personal/`): what you know. Grows. Claude writes it from captured sources; you read and correct.

Capture flows in through `inbox/`; `/ingest` files it; `/ask` answers from it; `/lint` keeps it honest. `CLAUDE.md` is the operating manual Claude reads at the start of every session in this folder; everything below points into it.

## Setup in five steps

### 1. The folder and the rulebook

```bash
cp -R brain-template ~/brain && cd ~/brain && rm -rf .git && git init && git add -A && git commit -q -m "brain: scaffold"
```

Keep it at `~/brain`: the hook, the skill wrappers and the scripts assume that path (or set `BRAIN=/other/path` in your shell profile). Add a **private** remote if you want a backup; the brain will contain things you would not put in a public repo.

Then make it yours:

- `CLAUDE.md`: replace `<your name>` and `<you>`; delete the sources you will not use; read the rules once. They are short, and every one of them exists because a run once did the wrong thing.
- `scripts/status.py`: set `OWNER` to your first name. Pages mark your own tasks as `- [ ] <Name>: …`; this is how the status page tells your tasks from what others owe you.
- `entities/_templates/`: one template per entity type (person, company, deal, project). Replace `<your company>` in the `owner` field. The ingest fills them; you only correct.

### 2. TELOS and the hook

Write three short files in `telos/` (the placeholders show the headings the skills rely on):

- `me.md`: roles, how you work, what Claude should always factor in.
- `now.md`: this week's top three, who you wait on, what to say no to. Keep the headings `## This week's top 3` and `## Waiting on` and the `**Updated:** YYYY-MM-DD` line exactly: `Home.md` embeds the first two and the hook warns when the date is more than ten days old.
- `principles.md`: how you like things done, what Claude must never do.

`goals.md` can wait until the first quarterly review.

Then add the hook to `~/.claude/settings.json` (create the file if it does not exist; merge into an existing `hooks` block if there is one):

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "bash ~/brain/scripts/session-context.sh"
      }]
    }]
  }
}
```

Open a new Claude Code session in any folder and ask "what are my top three this week?". If it answers from `now.md`, the hook works.

### 3. Connect one source

Claude Code reaches your tools through connectors (the desktop app's connector list, plus any local MCP servers you run). Start with whatever records your meetings; add one source a week. For each source, one file in `config/` holds its allowlist and rules; the ingest reads it before every run.

| Source | `config/` file | What the brain takes |
|---|---|---|
| Meeting notes | `sources.md` (the recorder table) | Summary, decisions, action items, participants. Several recorders are ranked; the best one wins. |
| WhatsApp | `whatsapp.md` | Allowlisted chats, plus a note-to-self chat as the capture inbox from the phone. |
| Email | `email.md` | Threads with a known entity in them. Nothing else. |
| Slack | `slack.md` | Messages that name a known entity or carry a decision. |
| Calendar | `calendar.md` | Known-entity meetings that no recorder covered. |
| Tasks | `tasks.md` | Your next actions, both ways, with the task id written on the page. |
| People (CRM) | `sources.md` | The contact link, and interaction notes written back after meetings. |

The pattern is the same for every source: fetch what is new since `last_run` in `config/state.json`, write one `inbox/` file per item, update `last_run`. The ingest never edits or deletes an inbox file.

Fill in the placeholders in the `config/` files you use (chat ids, calendar ids, project ids) and delete the rows and files you don't. Everything in `config/` is read by Claude as instructions, so write rules the way you would brief a colleague, and date them.

### 4. Teach it skills

A skill is a `SKILL.md` in `.claude/skills/<name>/`: a name, a one-line description that tells Claude when to use it, then numbered steps. Eight are included:

| Skill | Does |
|---|---|
| `/capture <text>` | Drop a note or decision into the inbox from any session. |
| `/ingest` | Pull what is new from every source, file it, link it, commit. |
| `/ask <question>` | Answer from the brain, with a citation on every claim. |
| `/prep <person or meeting>` | Everything known before a meeting: status, history, who owes what. |
| `/morning` | Today's brief: meetings with prep, what is due, money, overnight mail. |
| `/weekly` | Sunday look-back, then an interview that rewrites this week's priorities. |
| `/lint` | Stale pages, conflicts, missing sources, broken links, money overdue. |
| `/learn <url, file, text, topic>` | Add a framework, article or book to the wiki on purpose. |

Start with four: `/capture`, `/ingest`, `/ask`, `/prep`. Add `/morning` and `/weekly` once there are pages worth briefing from.

Install them globally so they work from any Claude Code session and always act on `~/brain`:

```bash
bash ~/brain/scripts/install-skills.sh
```

It writes thin wrappers to `~/.claude/skills/`. Re-run it after you change a skill's description. If your brain is not at `~/brain`, run it with `BRAIN=/other/path`.

Skills are prose, so they evolve like prose: when a run does something wrong, the fix is a dated sentence in the `SKILL.md`, not a new tool.

### 5. Routines and git

Routines are scheduled prompts in the Claude Code desktop app (Code → Scheduled): a cron expression and a prompt that calls a skill. No server. A sleeping Mac fires them on wake. Turn them on only after you have run each skill by hand a few times and read what it wrote. A schedule that works:

| When | Routine | Prompt |
|---|---|---|
| 06:30 daily | morning | `Work in ~/brain; read its CLAUDE.md first; git pull. Monday to Friday: run /ingest --quick (run record "ingest early"), then /morning, then /ingest in full. Saturday and Sunday: /ingest in full only. Use scripts/lock.sh as the skills say. End with the Suggested plan and one line on what was filed.` |
| 13:00 weekdays | midday | `Work in ~/brain; read its CLAUDE.md first; git pull. Run /ingest --quick exactly as the skill describes, lock included. End with a two-line summary.` |
| Sunday 18:00 | weekly | `Work in ~/brain; read its CLAUDE.md first; git pull. Run /weekly in routine mode (I am not present): look-back, /lint, next week's timeline file, and the interview questions with proposed answers at the top of journal/weekly-YYYY-Wnn.md. Do not rewrite telos/now.md yourself.` |

Three things keep unattended runs safe:

- **One run at a time.** `scripts/lock.sh` creates lock files atomically, so two runs that wake together cannot both write. The skills already call it; never create a lock by hand.
- **A record per run.** Every routine ends with `scripts/status.py log …` and `scripts/status.py render`, which rewrite `Status.md` (what ran today, source freshness, what went stale), `Waiting.md` (what others owe you) and `Home.md`. The *Run records* rule in `CLAUDE.md` has the exact lines. Optional: `scripts/com.example.brain-status.plist` re-renders hourly through launchd so the date rolls over on days without a run; the install command is in the file's comment.
- **Commit after every run.** One-line message, push to the private remote. The git log is the audit trail; a bad ingest is one revert away.

## Your first week

| Day | Do | You know it works when |
|---|---|---|
| 1 | Folder, `CLAUDE.md`, templates, TELOS, the hook | A new session in any folder opens knowing this week's top three. |
| 2 | Connect the meeting recorder; `/capture` a note (from the phone via the self-chat, or in a session) | The note sits in `inbox/` with a source and a time. |
| 3 | `/ingest` by hand after a real meeting; read what it filed | The page has a Status, a History line and a citation. Correct what is wrong, and put the missing rule into `CLAUDE.md`. |
| 4 | `/prep` before a meeting | The brief tells you something you had forgotten. |
| 5 | `/ask` a question you would otherwise search for | The answer cites a page, and the page cites an inbox file. |
| 7 | `/weekly`; rewrite `now.md` | Monday's sessions open with the new priorities. |
| Week 2 | Routines on; `/lint` on Sunday | The brief is written before you open the laptop. |

Day three is the one that decides whether you keep going: read the page the ingest wrote and fix it by hand. That is where you learn which rule is missing.

## Six rules that keep it honest

1. **Every fact has a source.** An inbox file, a URL, or "<your name>, date". No source, no fact.
2. **Conflicts are kept, not resolved.** A new fact that contradicts a page is added beside the old one with a `⚠ conflict` tag. `/lint` lists them; you decide.
3. **The inbox is append-only.** Raw captures are never edited or deleted.
4. **Update, don't duplicate.** One page per entity or topic. New pages only from a meeting, a CRM contact, or your say-so. Email and Slack never create one.
5. **Decisions go to the timeline.** One line: date, who, what was decided, next step, source. If in doubt, log it.
6. **It never sends anything.** Drafts only, never money or terms. The one optional exception: the morning plan and the weekly questions to your own WhatsApp chat with yourself, and only once you switch it on in `config/whatsapp.md`.

## Reading it in Obsidian

Open `~/brain` as a vault (Obsidian → Open folder as vault). `.obsidian/app.json` is included so new notes land in `inbox/` and frontmatter stays visible; Obsidian adds the rest on first open, and `.gitignore` keeps its workspace files out of git. `[[wikilinks]]` resolve by page name, so the graph and backlinks work out of the box.

For a start page, install the community plugin **Homepage** and point it at `Home`: `Home.md` keeps your own notes above the marker and, below it, today's status, the latest brief, this week's top three and what you are waiting on, all rewritten by `scripts/status.py render`.

## What is in the box

```
CLAUDE.md                  the operating manual
README.md                  this file
telos/                     me, goals, now, principles (placeholders)
entities/_templates/       person, company, deal, project
entities/{people,companies,deals,projects}/   empty
personal/README.md         the stricter rules for personal pages
timeline/README.md         the week-file format
knowledge/_template.md     plus the six area folders
journal/                   empty; briefs, preps, reviews and lint reports land here
inbox/README.md            the capture file format; _done/ for filed captures
config/                    sources, whatsapp, email, slack, calendar, tasks, state.json
scripts/                   session-context.sh, install-skills.sh, lock.sh, status.py, the launchd example
.claude/skills/            ask, capture, ingest, learn, lint, morning, prep, weekly
index.md, log.md, Home.md  headers only
```

Left out on purpose: anything tied to one person's tools (bank connectors, a bookkeeping routine, a task-comment watcher, write-back scripts for specific recorders). The skills mention where such things plug in; add them when you need them, as a dated rule first and a script second.

Run `python3 -I scripts/status.py render` once after setup: it creates `Status.md`, `Waiting.md` and the generated part of `Home.md`, and tells you which sources have never run.
