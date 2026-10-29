# Slack

Workspaces:
<!-- - **<Workspace>** (`<connector name>`) -->

Scope: all channels you are a member of, in every listed workspace.

Filter per message/thread:
- keep if it mentions a known entity (page or CRM contact), or contains a decision, commitment, deadline or amount;
- drop everything else.

## Routing (channel → page)
<!-- channels whose every message files to one page, even without a known-entity mention -->
<!-- - <workspace> `#<channel>` → [[Page]] (added YYYY-MM-DD) -->
- 

## Exclusions
<!-- channels to ignore even though you are a member: bot feeds, archived projects -->
- 

## How to read
Search messages since the last run and page with the cursor until done; never rely on one page of results. Bot posts are skipped unless they carry a decision or amount tied to a known entity. A failed or timed-out call is logged as `partial` in `log.md`, and that workspace's `last_run` stays put, so the next run covers the gap.
