#!/usr/bin/env python3
"""Run log + generated Status.md, Waiting.md and Home.md for the brain.

  scripts/status.py log <skill> <mode> <status> [--trigger scheduled|manual] [--started HH:MM]
                        [--counts k=v,k=v] [--sources "src: problem; src: problem"] [--note "..."]
      Appends one line to runs.jsonl. skill: ingest|morning|weekly|lint.
      mode: full|quick|early|brief|review|check (early = the quick ingest before the morning brief). status: ok|partial|failed|skipped.
  scripts/status.py render [--cron]
      Rewrites Status.md, Waiting.md and the generated part of Home.md. Safe to run any time; touches nothing else.
      --cron (the hourly launchd job, scripts/com.example.brain-status.plist): does nothing while a
      run holds a lock, since that run renders itself before committing.

Every skill that commits runs `render` just before its commit. Run with `python3 -I`.
"""
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

BRAIN = Path(__file__).resolve().parent.parent
RUNS = BRAIN / "runs.jsonl"
STATE = BRAIN / "config" / "state.json"
STATUS = BRAIN / "Status.md"
HOME = BRAIN / "Home.md"
MARKER = "<!-- generated below by scripts/status.py: don't edit under this line, it is rewritten on every run -->"
# Your first name, exactly as it appears in `- [ ] Name: …` lines on pages (config/tasks.md). Lines with this
# owner are yours (they belong in the task manager); every other owner is someone who owes you something.
OWNER = "Me"

# Mirrors the routines you schedule in the Claude desktop app (Code → Scheduled). Keep in sync; delete rows you don't run.
# (skill, mode, label, hour, minute, weekdays Mon=0)
SCHEDULE = [
    ("ingest", "early", "Morning quick ingest", 6, 30, range(5)),
    ("morning", "brief", "Morning brief", 6, 30, range(5)),
    ("ingest", "full", "Full ingest (morning routine)", 6, 30, range(7)),
    ("ingest", "quick", "Midday quick ingest", 13, 0, range(5)),
    ("weekly", "review", "Weekly review", 18, 0, [6]),
]
# Rows that started later than the others: not expected before this date, e.g. {("ingest", "early"): dt.date(2026, 1, 1)}
SINCE = {}
# Source freshness: (label, hours until amber, hours until red). Quick sources refresh twice on weekdays.
# Keys are the `last_run` keys in config/state.json (see config/sources.md). Add one per source you connect.
SOURCES = {
    "meetings": ("Meeting notes", 26, 50), "notes": ("Notes app", 26, 50),
    "whatsapp": ("WhatsApp", 26, 50), "whatsapp_self": ("WhatsApp self-chat", 26, 50),
    "email": ("Email", 26, 50), "calendar": ("Calendar", 26, 50),
    "slack": ("Slack", 26, 50), "crm": ("CRM", 26, 50),
    "tasks": ("Task manager", 26, 50),
}
ICON = {"ok": "✅", "partial": "⚠️", "failed": "❌", "skipped": "⏭️"}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def write(path, text):  # atomic, so a commit never picks up a half-written page
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def locked():
    for name in ("ingest", "morning"):
        f = BRAIN / f".{name}.lock"
        if f.exists() and dt.datetime.now().timestamp() - f.stat().st_mtime < 7200:
            return name
    return None


def now():
    return dt.datetime.now().astimezone()


def load_runs():
    if not RUNS.exists():
        return []
    out = []
    for line in RUNS.read_text().splitlines():
        try:
            r = json.loads(line)
            r["_end"] = dt.datetime.fromisoformat(r["ended"])
            out.append(r)
        except (ValueError, KeyError):
            continue
    return sorted(out, key=lambda r: r["_end"])


def cmd_log(args):
    if len(args) < 3:
        sys.exit(__doc__)
    skill, mode, status = args[:3]
    if status not in ICON:
        sys.exit(f"status must be one of {', '.join(ICON)}")
    opts, i = {}, 3
    while i < len(args):
        if not args[i].startswith("--") or i + 1 >= len(args):
            sys.exit(f"bad option: {args[i]}")
        opts[args[i][2:]] = args[i + 1]
        i += 2
    t = now()
    rec = {"ended": t.isoformat(timespec="seconds"), "skill": skill, "mode": mode, "status": status,
           "trigger": opts.get("trigger", "manual")}
    if "started" in opts:
        h, m = opts["started"].split(":")
        s = t.replace(hour=int(h), minute=int(m), second=0)
        rec["started"] = (s if s <= t else s - dt.timedelta(days=1)).isoformat(timespec="seconds")
    if opts.get("counts"):
        rec["counts"] = {k.strip(): (int(v) if v.strip().isdigit() else v.strip())
                         for k, v in (p.split("=", 1) for p in opts["counts"].split(",") if "=" in p)}
    if opts.get("sources"):
        rec["sources"] = {k.strip(): v.strip() for k, v in
                          (p.split(":", 1) for p in opts["sources"].split(";") if ":" in p)}
    if opts.get("note"):
        rec["note"] = opts["note"]
    with RUNS.open("a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps(rec, ensure_ascii=False))


def ago(delta):
    h = delta.total_seconds() / 3600
    if h < 1:
        return f"{int(h * 60)} min ago"
    if h < 48:
        return f"{h:.0f} h ago"
    return f"{h / 24:.0f} days ago"


def today_rows(runs, t):
    rows, problems = [], 0
    for skill, mode, label, hh, mm, days in SCHEDULE:
        if t.weekday() not in days or t.date() < SINCE.get((skill, mode), dt.date.min):
            continue
        due = t.replace(hour=hh, minute=mm, second=0, microsecond=0)
        mine = [r for r in runs if r["skill"] == skill and r["mode"] == mode
                and r["_end"].date() == t.date() and r["status"] != "skipped"]
        if skill == "morning" and not mine and (BRAIN / "journal" / f"{t.date()}.md").exists():
            rows.append(f"| ✅ | {label} | {hh:02d}:{mm:02d} | brief written (no run record) |")
            continue
        if not runs:  # a brain with no run logged yet: nothing is scheduled, so nothing is late
            rows.append(f"| · | {label} | {hh:02d}:{mm:02d} | no run logged yet: schedule it in the desktop app, or delete the row in scripts/status.py |")
            continue
        if mine:
            r = mine[-1]
            # The morning routine runs on wake and files after the brief, so its ingest gets more room
            late = r["_end"] - due > dt.timedelta(hours=6 if (skill, mode) == ("ingest", "full") else 3)
            icon = ICON[r["status"]] if not (late and r["status"] == "ok") else "⚠️"
            detail = f"ran {r['_end']:%H:%M}" + (" (late)" if late else "") + f", {r['trigger']}"
            if r.get("sources"):
                detail += " · " + "; ".join(f"{k}: {v}" for k, v in r["sources"].items())
            elif r.get("note"):
                detail += " · " + r["note"]
            problems += icon != "✅"
        elif t < due:
            icon, detail = "⏳", "not due yet"
        elif t - due < dt.timedelta(hours=1):
            icon, detail = "⏳", "due, should be running"
        else:
            icon, detail = "❌", "did not run (Mac asleep or the run failed before logging)"
            problems += 1
        rows.append(f"| {icon} | {label} | {hh:02d}:{mm:02d} | {detail} |")
    if not rows:
        rows.append("| · | nothing scheduled today | | |")
    return rows, problems


def source_rows(t):
    try:
        last = json.loads(STATE.read_text()).get("last_run", {})
    except (OSError, ValueError):
        return ["| ❌ | config/state.json unreadable | | |"], 1
    rows, problems = [], 0
    for key, (label, amber, red) in SOURCES.items():
        if key not in last:
            continue
        if not last[key]:
            rows.append(f"| · | {label} | never | first run reads the last 7 days |")
            continue
        when = dt.datetime.fromisoformat(last[key])
        age = t - when
        h = age.total_seconds() / 3600
        icon = "✅" if h < amber else "⚠️" if h < red else "❌"
        problems += icon != "✅"
        rows.append(f"| {icon} | {label} | {when:%a %d %b %H:%M} | {ago(age)} |")
    return rows, problems


def waiting(t):
    lines, problems = [], 0
    inbox = [p for p in (BRAIN / "inbox").iterdir()
             if p.is_file() and p.suffix == ".md" and p.name != "README.md"]
    if inbox:
        problems += 1
        lines.append(f"- 📥 **{len(inbox)} unfiled** in `inbox/` (next `/ingest` files them)")
    else:
        lines.append("- 📥 inbox empty")
    pages = []
    for folder in ("entities", "knowledge", "personal"):
        for p in (BRAIN / folder).rglob("*.md"):
            try:
                n = p.read_text(errors="ignore").count("⚠ conflict")
            except OSError:
                continue
            if n:
                pages.append((p, n))
    total = sum(n for _, n in pages)
    if total:
        work = [f"[[{p.stem}]]" for p, _ in pages if not p.relative_to(BRAIN).parts[0] == "personal"]
        npers = sum(1 for p, _ in pages if p.relative_to(BRAIN).parts[0] == "personal")
        where = work + ([f"{npers} personal page(s)"] if npers else [])
        lines.append(f"- ⚠ **{total} open conflicts** on {', '.join(where)} (`/lint` lists them)")
    else:
        lines.append("- no open ⚠ conflicts")
    for name in ("ingest", "morning"):
        f = BRAIN / f".{name}.lock"
        if f.exists():
            age = t - dt.datetime.fromtimestamp(f.stat().st_mtime).astimezone()
            stuck = age > dt.timedelta(hours=2)
            problems += stuck
            lines.append(f"- 🔒 `.{name}.lock` held for {ago(age).replace(' ago', '')}"
                         + (" — **stale**, the next run takes it over" if stuck else " (a run is in progress)"))
    return lines, problems


def run_table(runs):
    rows = []
    for r in reversed(runs[-14:]):
        c = r.get("counts") or {}
        counts = ", ".join(f"{k} {v}" for k, v in c.items())
        issues = "; ".join(f"{k}: {v}" for k, v in (r.get("sources") or {}).items()) or r.get("note", "")
        rows.append(f"| {r['_end']:%a %d %b %H:%M} | {r['skill']} ({r['mode']}) | {ICON.get(r['status'], r['status'])} "
                    f"| {r['trigger']} | {counts} | {issues.replace('|', '/')} |")
    return rows or ["| | no runs logged yet | | | | |"]


# ---- Waiting.md (rules in config/tasks.md) -----------------------------------------------------
# The owner's own tasks live in the task manager. Pages keep `- [ ] Owner: … · due … · todoist:<id>` lines; this
# view lists what others owe the owner, plus any OWNER line that has no task yet (so nothing is lost).
WAITING = BRAIN / "Waiting.md"
TODOIST = BRAIN / "config" / "todoist-tasks.json"
DUE_RE = re.compile(r"\s*·?\s*\bdue (\d{4}-\d{2}-\d{2})")
TID_RE = re.compile(r"\s*·?\s*\b(?:todoist|crm):([0-9A-Za-z-]{8,40})")
SRC_RE = re.compile(r"\s*\(src:[^()]*(?:\([^()]*\)[^()]*)*\)\s*$")
OWNER_RE = re.compile(r"^([A-ZÁ-Ž][\wÀ-ž.()]*(?:\s*(?:\+|&|and|,)?\s*[A-ZÁ-Ž(][\wÀ-ž.()]*){0,4}):\s+(.*)$")


def page_tasks():
    """Every open `- [ ]` line in entities/ and personal/ (never personal/coaching/, which stays private)."""
    out = []
    for folder in ("entities", "personal"):
        for p in sorted((BRAIN / folder).rglob("*.md")):
            rel = p.relative_to(BRAIN)
            if "_templates" in rel.parts or rel.parts[:2] == ("personal", "coaching"):
                continue
            try:
                lines = p.read_text(errors="ignore").splitlines()
            except OSError:
                continue
            for line in lines:
                if not line.startswith("- [ ] "):
                    continue
                body = line[6:].strip()
                due, tid = DUE_RE.search(body), TID_RE.search(body)
                text = SRC_RE.sub("", TID_RE.sub("", DUE_RE.sub("", body))).strip(" ·")
                owner, m = OWNER, OWNER_RE.match(text)
                if m:
                    owner, text = m.group(1), m.group(2)
                if text:
                    out.append({"page": p.stem, "personal": rel.parts[0] == "personal", "owner": owner,
                                "mine": OWNER in owner, "text": text, "tid": tid.group(1) if tid else None,
                                "due": dt.date.fromisoformat(due.group(1)) if due else None})
    return out


def deal_steps():
    out = []
    for p in sorted((BRAIN / "entities" / "deals").glob("*.md")):
        fm = p.read_text(errors="ignore").split("---")
        if len(fm) < 3:
            continue
        f = dict(re.findall(r"^(next_step|next_step_due|stage):[ \t]*(.*)$", fm[1], re.M))
        if f.get("next_step", "").strip() and f.get("stage", "") not in ("closed-won", "closed-lost"):
            d = f.get("next_step_due", "").strip()
            out.append({"page": p.stem, "text": f["next_step"].strip(),
                        "due": dt.date.fromisoformat(d) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) else None})
    return out


def fmt_due(d, today):
    if not d:
        return ""
    n = (d - today).days
    tail = f" · **{-n} d overdue**" if n < 0 else " · today" if n == 0 else ""
    return f" · {DAYS[d.weekday()]} {d:%d %b}{tail}"


def render_tasks(t):
    """Writes Waiting.md; returns (open Todoist tasks, overdue Todoist tasks) from the last snapshot."""
    today = t.date()
    tasks = page_tasks()
    try:
        snap = json.loads(TODOIST.read_text())
        todo = snap.get("tasks", [])
        synced = dt.datetime.fromisoformat(snap["synced"])
    except (OSError, ValueError, KeyError):
        todo, synced = [], None
    n_open = len(todo)
    n_over = sum(1 for x in todo if x.get("due") and x["due"][:10] < str(today))
    others = [x for x in tasks if not x["mine"]]
    unfiled = [x for x in tasks if x["mine"] and not x["tid"]]
    by_owner = {}
    for x in others:
        by_owner.setdefault(x["owner"], []).append(x)
    wait = []
    for o in sorted(by_owner, key=lambda k: (-len(by_owner[k]), k)):
        rows = sorted(by_owner[o], key=lambda x: (x["due"] or dt.date.max))
        wait += [f"**{o}**"] + [f"- {x['text']}{fmt_due(x['due'], today)} — [[{x['page']}]]" for x in rows] + [""]
    by_page = {}
    for x in unfiled:
        by_page.setdefault(x["page"], []).append(x)
    nf = []
    for page in sorted(by_page, key=lambda k: (-len(by_page[k]), k)):
        nf += [f"**[[{page}]]**"] + [f"- {x['text']}{fmt_due(x['due'], today)}" for x in by_page[page]] + [""]
    steps = [f"- **[[{s['page']}]]**: {s['text']}{fmt_due(s['due'], today)}" for s in deal_steps()]
    sync = []
    if synced is None:
        sync.append("- no task-manager snapshot yet (`config/todoist-tasks.json`; `/ingest` writes it once a task manager is connected)")
    elif t - synced > dt.timedelta(hours=36):
        sync.append(f"- ⚠ Todoist snapshot is {ago(t - synced)}: run `/ingest`")
    text = "\n".join([
        "---", "generated: " + t.isoformat(timespec="minutes"), "---", "",
        "# Waiting", "",
        f"*Generated {DAYS[t.weekday()]} {t:%d %b %H:%M} by `scripts/status.py` from every page's open `- [ ]` lines. "
        "Your own tasks are in **Todoist** ([app](https://app.todoist.com/app/today)); this page is what others owe you, "
        "plus a safety net. Don't edit here: tick the line on its page. Rules: `config/tasks.md`.*", "",
        f"**{len(others)} waiting on others** · Todoist: {n_open} open, {n_over} overdue"
        + (f" (snapshot {ago(t - synced)})" if synced else ""), "",
        "## Waiting on others", "", *(wait or ["- nothing", ""]),
        "## Not in Todoist yet", "",
        "*Your page lines with no `todoist:` id. `/ingest` creates them; anything still here after a run needs a look.*", "",
        *(nf or ["- none", ""]),
        "## Deal next steps", "", "*From the deal pages' `next_step` field.*", "", *(steps or ["- none"]), "",
        "## Sync issues", "", *(sync or ["- none"]), "",
    ])
    write(WAITING, text)
    return n_open, n_over


def render():
    t = now()
    n_mine, n_over = render_tasks(t)
    runs = load_runs()
    trows, tp = today_rows(runs, t)
    srows, sp = source_rows(t)
    wlines, wp = waiting(t)
    head = "✅ All good" if not (tp or sp or wp) else f"⚠️ {tp + sp + wp} thing(s) to look at"
    status = "\n".join([
        "---", "generated: " + t.isoformat(timespec="minutes"), "---", "",
        "# Status", "",
        f"*Generated {DAYS[t.weekday()]} {t:%d %b %H:%M} by `scripts/status.py` at the end of every run. "
        "Don't edit: it's rewritten. Raw records: `runs.jsonl`; the story: [[log]].*", "",
        "## Today", "", f"**{head}**", "",
        "| | Run | Due | |", "|---|---|---|---|", *trows, "",
        "## Sources", "", "Last successful capture per source (from `config/state.json`).", "",
        "| | Source | Last run | |", "|---|---|---|---|", *srows, "",
        "## Waiting", "", *wlines, "",
        "## Recent runs", "",
        "| When | Run | | Trigger | Counts | Issues |", "|---|---|---|---|---|---|", *run_table(runs), "",
    ])
    write(STATUS, status)

    journal = BRAIN / "journal"
    briefs = sorted(p.stem for p in journal.glob("20??-??-??.md"))
    today = str(t.date())
    if today in briefs:
        brief = [f"## Today's brief · {DAYS[t.weekday()]} {t:%d %b}", "", f"![[journal/{today}]]"]
    elif briefs:
        brief = [f"## Today's brief · {DAYS[t.weekday()]} {t:%d %b}", "",
                 f"> [!warning] No brief for today yet. " +
                 ("It's due at 06:35." if t.weekday() < 5 and t.hour < 7 else
                  "No brief on weekends; run `/morning` if you want one." if t.weekday() >= 5 else
                  "The morning run didn't produce one: see [[Status]] or run `/morning`.") +
                 f" Latest is {briefs[-1]}, below.", "", f"![[journal/{briefs[-1]}]]"]
    else:
        brief = ["## Today's brief", "", "No briefs yet."]
    iso = t.isocalendar()
    week = f"timeline/{iso[0]}/{iso[0]}-W{iso[1]:02d}"
    week_link = f"[[{week}|this week's timeline]]" if (BRAIN / f"{week}.md").exists() else "no timeline file this week yet"
    reviews = sorted(journal.glob("weekly-*.md"))
    lints = sorted(journal.glob("lint-*.md"))
    preps = sorted(journal.glob("prep-*.md"), key=lambda p: p.name)[-5:]
    recent = [f"[[journal/{d}|{dt.date.fromisoformat(d):%a %d}]]" for d in briefs[-7:]][::-1]
    generated = "\n".join([
        MARKER, "",
        "## Status", "", "![[Status#Today]]", "",
        *brief, "",
        f"## Tasks · Todoist {n_mine} open, {n_over} overdue", "",
        "Your tasks: [Todoist](https://app.todoist.com/app/today) · who owes you what: [[Waiting]]", "",
        "## This week", "", "![[telos/now#This week's top 3]]", "", "![[telos/now#Waiting on]]", "",
        "## Jump to", "",
        f"- **Briefs:** {' · '.join(recent) or 'none yet'}",
        f"- **Week:** {week_link} · [[telos/now|now]] · [[telos/goals|goals]]"
        + (f" · [[journal/{reviews[-1].stem}|last weekly review]]" if reviews else "")
        + (f" · [[journal/{lints[-1].stem}|last lint]]" if lints else ""),
        "- **Recent preps:** " + (" · ".join(f"[[journal/{p.stem}|{p.stem[16:] or p.stem}]]" for p in reversed(preps)) or "none"),
        "- **Look-ups:** [[Waiting]] · [[index]] · [[log]] · [[Status]]", "",
        f"*Updated {DAYS[t.weekday()]} {t:%d %b %H:%M}.*", "",
    ])
    top = HOME.read_text().split(MARKER)[0] if HOME.exists() else "# Home\n\n<!-- Your own notes and pinned links go here, above the marker. -->\n\n"
    write(HOME, top.rstrip("\n") + "\n\n" + generated)
    print(f"rendered Status.md, Waiting.md and Home.md · {head} · todoist: {n_mine} open, {n_over} overdue")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("log", "render"):
        sys.exit(__doc__)
    if sys.argv[1] == "log":
        cmd_log(sys.argv[2:])
    elif "--cron" in sys.argv and locked():
        print(f"skipped: {locked()} run in progress")
    else:
        render()
