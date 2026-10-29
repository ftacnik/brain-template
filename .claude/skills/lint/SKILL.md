---
name: lint
description: Health check of the brain — stale pages, orphans, conflicts, missing sources, index drift, deals past due. Run weekly (part of /weekly) or when the brain feels off.
---

# /lint

Work in `~/brain`; every path below is relative to it.

Produce a report, fix what is mechanical, and list what needs the owner.

## Checks

1. **Index drift** — pages missing from `index.md` or listed but gone. Fix.
2. **Stale** — `entities/deals/` with `stage` active/negotiating/proposed and `updated` > 21 days; people/companies with Status older than 60 days but recent timeline mentions. List.
3. **Past due** — deals with `next_step_due` in the past. List.
4. **Conflicts** — every `⚠ conflict` tag, with both claims and sources. List for the owner to resolve.
5. **Missing sources** — facts in Status/Context/Terms without `(src: …)`. List.
6. **Orphans** — pages with no inbound `[[link]]` and no timeline mention. List; propose archive.
7. **Duplicates** — two pages likely the same entity (name similarity, same CRM id, same domain). List; propose merge.
8. **Template drift** — pages missing required frontmatter fields. Fix.
9. **TELOS age** — `telos/now.md` updated > 10 days ago → flag loudly.
10. **Personal leakage** — anything in `personal/` that looks like an IBAN, account number, or balance. Flag; never commit such a fix silently — tell the owner.
11. **Broken links** — `[[name]]` with no matching page anywhere in `entities/`, `personal/`, `knowledge/`, `telos/`. List; create the page or fix the link.
12. **Money owed** — `expected_payments` entries with `received` empty and `deadline` (or `promised` + 7 days) in the past. Flag loudly: this is money you are owed.
13. **Tasks** — per `config/tasks.md`: `- [ ]` lines with no owner or a topic as owner → fix to `Owner: …`; `<You>:` lines with no `todoist:` id after an ingest → list (`Waiting.md` *Not in Todoist yet*); a `todoist:` id whose task is completed → tick; the same task open on two pages → propose a merge (keep it on the project page).
14. **Size** — pages in `entities/` + `personal/` + `knowledge/` (no templates) ≥ 130 → flag: time to give `/ask` a search step (grep over pages) instead of reading `index.md` whole.

Write the report to `journal/lint-YYYY-MM-DD.md`, append a line to `log.md`, write the run record (`status.py log lint check <ok|partial> …`, `partial` when items need the owner's decision, see *Run records* in `CLAUDE.md`) and `status.py render`, commit. Then show the owner only the items that need a decision.
