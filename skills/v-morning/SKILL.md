---
name: v-morning
description: Daily morning digest — combines /v-standup + L3 triage queue + today's calendar prep + 1-line promo gap reminder + reading queue. One prompt, all-in-one. Drops draft to self-DM. Triggered 8:45 IST cron or manual.
---

You are running Vashistha's morning digest. Composes 5 sections into one Slack message, posted as draft to self-DM `D088362AS65`.

## Output format

```
*Morning digest — [DDD MMM DD]*

*Standup draft:*
[Yesterday/Today/Blockers from /v-standup]

———

*L3 triage (last 24h, awaiting reply):*
- [thread permalink] — channel — top topic — last poster
(up to 5; "None" if clear)

———

*Today's calendar prep (non-standup events):*
- [HH:MM] [title] — [attendees count] — [organizer] — [1-liner of what to prep]

———

*Promo gap reminder (top 3 weakest):*
- 🔴 / 🟡 [rubric_id]: current X / threshold Y — suggestion: ...

———

*Reading queue (links shared with you, last 24h):*
- [link] — [1-line summary]
(up to 5)
```

## Step 1 — Standup section

Run `/v-standup` logic (or call the v-standup skill). Embed its output as the first section.

## Step 2 — L3 triage queue

For each of these channels, find threads where the latest message is from someone OTHER than user `U087T0SHNCC`, posted in last 24h, and user has previously participated or been @-mentioned:

- `#einvoice-l3-support` (`C055ABMAVCL`)
- `#einvoice-mea-l3-support` (`C0AB8EAH9A6`)
- `#einvoice-india-mea` (`C0ADWHJ2V9S`)
- `#sev1-engg`

Slack MCP caps at 20 msgs/query — paginate. List up to 5. Format: thread permalink — channel — top topic — last poster.

## Step 3 — Calendar prep

Today's events 9:00–19:00 IST. EXCLUDE:
- `EInvoice India/Mea Standup` (recurring 10:00)
- `Standup: E-Invoicing Malaysia` (recurring)
- 1:1 with manager (just list, no prep)

For each remaining event:
- `HH:MM | title | attendees count | organizer email | 1-liner of what to prep`
- "1-liner of prep" comes from cross-referencing event title with `data/active_projects.yaml` — surface the project's `next_milestone` if any active project matches.

## Step 4 — Promo gap reminder

Read `~/dev/personal-skills/data/promotion_state.json`. Filter `rubric_lines` where `status` starts with 🔴 or 🟡. Sort by:
1. 🔴 first
2. Then 🟡, ranked by (current.value / threshold) ratio ascending (most below threshold first)

Show top 3 only:
- `🔴/🟡 [id]: current [X] / threshold [Y] — suggestion: [from data_source.type — e.g. "review one PR with ≥5 comments today" / "log a touchpoint with [mentee]"]`

If `promotion_state.json` doesn't exist or is empty, skip section with "Promo state not initialized — run /v-promo-tracker first".

## Step 5 — Reading queue

Slack messages received by user in last 24h that contain links (Drive docs, GitHub PRs, Confluence pages). Skip:
- Links to your own PRs (you authored)
- Auto-Meet-Transcripts (`parentId == 1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF`)
- Bot messages (deploy alerts, GitHub notifications)

For each: link — 1-line summary (use the Slack message preview text or fetch link title if Drive/Confluence).

List up to 5. "None" if empty.

## Step 6 — Output

Single Slack message to self-DM `D088362AS65` via `slack_send_message_draft`. Sections divided by `———`. Total length under 80 lines.

## Verifiable success criteria

- 5 sections present (Standup / L3 / Calendar / Promo / Reading), each marked "None" if no items.
- Calendar excludes recurring standups.
- Promo top 3 lines all from `promotion_state.json`.
- Posted to `D088362AS65` only.
- Total under 80 lines.

## Failure modes
- work-journal yesterday section missing → "No yesterday entries — daily-documentation cron may not have run."
- Slack pagination limit → "L3 queue partial; check #einvoice-l3-support manually."
- promotion_state.json missing → skip Promo section with explanation.
